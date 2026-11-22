#!/usr/bin/env python3
"""Read-only health checks for an Obsidian vault, used by the /garden skill.

Only files git would sync are opened: the scan set comes from
`git ls-files --cached --others --exclude-standard`, so private folders
(--exclude), .secrets/ and anything else gitignored is never read, and nothing
from them can reach the report (which is itself synced). A filesystem walk
with a hard-coded exclude list is the fallback when git is unavailable, and
the report says so. Link targets are resolved against file *names* on disk
(never opened), so a link into a local-only note is not misreported. Reports:

  * unresolved wikilinks, including links that only match a note's aliases:
    or title: (Obsidian resolves links by file name/path only);
  * frontmatter gaps against the vault's frontmatter schema (REQUIRED_KEYS below);
  * inbox items (--inbox, default `01 Inbox/`) with their age;
  * Untitled* files, empty or invalid .canvas files, empty notes;
  * orphan notes, duplicate basenames, tag case drift, stale context packs;
  * a delta against the previous report's Metrics table.

It never writes to the vault. Output goes to stdout (markdown or JSON).
Standard library only.

    python3 garden_check.py --vault <vault> [--previous <report.md>] [--format md|json] [--today YYYY-MM-DD]
        [--inbox "01 Inbox"] [--exclude <private folder>]... [--redact <folder>]...
"""
from __future__ import annotations

import argparse
import datetime as dt
import json
import os
import re
import subprocess
import sys
from collections import defaultdict
from pathlib import Path

# Never scanned, whatever git says (belt and braces). Dot-folders (.git,
# .obsidian, .trash, .claude, .agents, any .secrets) are also pruned
# generically because Obsidian does not index them. Root folders passed with
# --exclude are private and are not even listed.
EXCLUDE_ROOT: set[str] = set()
EXCLUDE_PREFIXES: tuple[str, ...] = (".obsidian/", ".trash/", ".claude/", ".agents/")
SCAN_SUFFIXES = (".md", ".canvas", ".base")
# Frontmatter values of notes under these folders (--redact) are never printed
# (path and field name only), e.g. folders that describe private infrastructure.
REDACT_VALUES: tuple[str, ...] = ()
INBOX_DIR = "01 Inbox/"
REQUIRED_KEYS = ["title", "type", "domain", "status", "visibility", "created", "updated", "tags", "related"]
MAY_BE_EMPTY = {"tags", "related"}
LEGAL_VISIBILITY = {
    "personal": {"human", "shared"},
    "project": {"human", "shared"},
    "source": {"human", "shared"},
    "agent": {"hidden", "shared"},
    "system": {"hidden", "human"},
    "mixed": {"human", "shared"},
}
CORE_VISIBILITY = {"human", "agent", "shared", "hidden"}
# Repo-level docs that are not vault notes and carry no frontmatter by design.
FRONTMATTER_EXEMPT = {"readme.md", "agents.md", "claude.md"}
STALE_PACK_DAYS = 90
METRIC_KEYS = [
    ("in_scope_notes", "In-scope Markdown notes"),
    ("wikilinks_total", "Wikilinks checked"),
    ("unresolved_targets", "Unresolved link targets"),
    ("unresolved_links", "Unresolved links"),
    ("alias_only_targets", "…of which match only an alias/title"),
    ("frontmatter_missing", "Notes with no frontmatter"),
    ("frontmatter_missing_keys", "Notes missing required keys"),
    ("frontmatter_illegal_pairs", "Illegal domain/visibility pairs"),
    ("frontmatter_unknown_values", "Non-schema domain/visibility values"),
    ("inbox_items", "Inbox items"),
    ("untitled_files", "Untitled* files"),
    ("empty_canvases", "Empty or invalid .canvas files"),
    ("empty_notes", "Empty notes"),
    ("orphan_notes", "Orphan notes"),
    ("duplicate_basenames", "Duplicate note basenames"),
]

LINK_RE = re.compile(r"!?\[\[([^\[\]\n]+?)\]\]")
INLINE_CODE_RE = re.compile(r"(`+)(?:(?!\1).)+?\1")
FENCE_RE = re.compile(r"^\s{0,3}(?:>\s?)*\s{0,3}(`{3,}|~{3,})")
TAG_RE = re.compile(r"(?:^|\s)#([A-Za-z0-9_][\w/\-]*)")
DATE_RE = re.compile(r"(\d{4}-\d{2}-\d{2})")


# --------------------------------------------------------------- walking

def walk(vault: Path) -> list[Path]:
    out = []
    for root, dirs, files in os.walk(vault):
        rel_root = Path(root).relative_to(vault)
        dirs[:] = sorted(d for d in dirs if not d.startswith(".")
                         and not (rel_root == Path(".") and d in EXCLUDE_ROOT))
        for f in sorted(files):
            if not f.startswith("."):
                out.append(Path(root, f).relative_to(vault))
    return out


def posix(p: Path) -> str:
    return p.as_posix()


def excluded(rel: str) -> bool:
    return rel.startswith(EXCLUDE_PREFIXES) or any(seg.startswith(".") for seg in rel.split("/"))


def git_scan_set(vault: Path) -> list[Path] | None:
    """Notes git would sync (tracked, or untracked but not ignored); None if git is unavailable."""
    try:
        out = subprocess.run(
            ["git", "-C", str(vault), "ls-files", "-z", "--cached", "--others", "--exclude-standard",
             "--", *(f"*{s}" for s in SCAN_SUFFIXES)],
            capture_output=True, check=True, timeout=60).stdout
    except (OSError, subprocess.SubprocessError):
        return None
    rels = sorted({r for r in out.decode("utf-8", "replace").split("\x00") if r})
    return [Path(r) for r in rels if not excluded(r) and (vault / r).is_file()]


def redacted(rel: str) -> bool:
    return rel.startswith(REDACT_VALUES)


# --------------------------------------------------------------- frontmatter

def split_frontmatter(text: str) -> tuple[str | None, str]:
    text = text.lstrip("﻿")
    lines = text.split("\n")
    if not lines or lines[0].rstrip("\r") != "---":
        return None, text
    for i in range(1, len(lines)):
        if lines[i].rstrip("\r") in ("---", "..."):
            return "\n".join(lines[1:i]), "\n".join(lines[i + 1:])
    return None, text  # unterminated: Obsidian does not treat it as properties


def unquote(v: str) -> str:
    v = v.strip()
    if len(v) >= 2 and v[0] == v[-1] and v[0] in "\"'":
        return v[1:-1]
    return v


def parse_frontmatter(fm: str) -> dict[str, object]:
    """Top-level keys only: scalars as str, block or flow lists as list[str]."""
    data: dict[str, object] = {}
    key = None
    for raw in fm.split("\n"):
        line = raw.rstrip("\r")
        m = re.match(r"^([A-Za-z0-9_][\w\-]*)\s*:\s*(.*)$", line)
        if m:
            key, val = m.group(1), m.group(2).strip()
            if val.startswith("[") and val.endswith("]"):
                inner = val[1:-1].strip()
                data[key] = [unquote(x) for x in re.split(r",(?=(?:[^\"]*\"[^\"]*\")*[^\"]*$)", inner) if x.strip()] if inner else []
            elif val == "":
                data[key] = ""
            else:
                data[key] = unquote(val)
            continue
        m = re.match(r"^\s+-\s*(.*)$", line)
        if m and key is not None:
            cur = data.get(key)
            if not isinstance(cur, list):
                cur = [] if cur in ("", None) else [str(cur)]
            cur.append(unquote(m.group(1)))
            data[key] = cur
    return data


def as_list(v: object) -> list[str]:
    if isinstance(v, list):
        return [str(x) for x in v if str(x).strip()]
    if isinstance(v, str) and v.strip():
        return [v]
    return []


def blank(v: object) -> bool:
    return v is None or (isinstance(v, str) and v.strip() in ("", "null", "~")) or (isinstance(v, list) and not v)


def parse_date(v: object) -> dt.date | None:
    if isinstance(v, str):
        m = DATE_RE.search(v)
        if m:
            try:
                return dt.date.fromisoformat(m.group(1))
            except ValueError:
                return None
    return None


# --------------------------------------------------------------- links

def strip_code(body: str) -> str:
    """Blank out fenced code blocks and inline code, keeping line structure."""
    out, fence = [], None
    for line in body.split("\n"):
        m = FENCE_RE.match(line)
        if fence is None:
            if m:
                fence = m.group(1)
                out.append("")
                continue
            out.append(INLINE_CODE_RE.sub("", line))
        else:
            if m and m.group(1)[0] == fence[0] and len(m.group(1)) >= len(fence) \
                    and line.strip().lstrip(">").strip() == m.group(1):
                fence = None
            out.append("")
    return "\n".join(out)


def link_target(inner: str) -> str:
    inner = inner.replace("\\|", "|")
    t = inner.split("|", 1)[0]
    t = re.split(r"[#^]", t, 1)[0]
    return t.strip().replace("\\", "/").lstrip("/")


class Index:
    def __init__(self, files: list[Path]):
        self.keys: dict[str, set[str]] = defaultdict(set)
        for p in files:
            rel = posix(p)
            names = [rel]
            if rel.lower().endswith(".md"):
                names.append(rel[:-3])
            for n in names:
                segs = n.split("/")
                for i in range(len(segs)):
                    self.keys["/".join(segs[i:]).lower()].add(rel)

    def resolve(self, target: str) -> set[str]:
        t = target.lower()
        return self.keys.get(t, set()) | self.keys.get(t + ".md", set())


# --------------------------------------------------------------- main checks

def run(vault: Path, today: dt.date, previous: Path | None, *, use_git: bool = True) -> dict:
    on_disk = [p for p in walk(vault) if not excluded(posix(p))]
    index = Index(on_disk)  # names only; these files are never opened
    files = git_scan_set(vault) if use_git else None
    scan_source = "git ls-files (tracked + untracked, not ignored)"
    if files is None:
        scan_source = "filesystem walk with hard-coded excludes (git unavailable; gitignored files may be included)"
        files = [p for p in on_disk if p.suffix.lower() in SCAN_SUFFIXES]
    notes = [p for p in files if p.suffix.lower() == ".md"]

    texts: dict[str, str] = {}
    fms: dict[str, dict | None] = {}
    for p in notes:
        rel = posix(p)
        try:
            texts[rel] = (vault / p).read_text(encoding="utf-8", errors="replace")
        except OSError:
            texts[rel] = ""
        fm, _ = split_frontmatter(texts[rel])
        fms[rel] = parse_frontmatter(fm) if fm is not None else None

    alias_map: dict[str, set[str]] = defaultdict(set)
    for rel, fm in fms.items():
        if fm:
            for a in as_list(fm.get("aliases")) + as_list(fm.get("alias")):
                alias_map[a.strip().lower()].add(rel)
            if isinstance(fm.get("title"), str) and fm["title"].strip():
                alias_map[fm["title"].strip().lower()].add(rel)

    # -- links
    total = 0
    inbound: dict[str, set[str]] = defaultdict(set)
    unresolved: dict[str, dict] = {}
    for rel, text in texts.items():
        clean = strip_code(text.lstrip("﻿"))
        for m in LINK_RE.finditer(clean):
            target = link_target(m.group(1))
            if "<%" in m.group(1) or "{{" in m.group(1):
                continue  # Templater / placeholder syntax, not a real link
            total += 1
            if target == "":
                continue  # [[#Heading]] — same-note link
            hits = index.resolve(target)
            if hits:
                for h in hits:
                    if h != rel:
                        inbound[h].add(rel)
                continue
            key = target.lower()
            u = unresolved.setdefault(key, {"target": target, "count": 0, "sources": set(),
                                            "alias_of": sorted(alias_map.get(key, set()))})
            u["count"] += 1
            u["sources"].add(rel)

    unresolved_list = sorted(
        ({**u, "sources": sorted(u["sources"])} for u in unresolved.values()),
        key=lambda u: (not u["alias_of"], -u["count"], u["target"].lower()))
    for u in unresolved_list:
        # A target matching a redacted note's alias/title *is* that note's
        # frontmatter value: withhold it, keep the paths.
        hidden = sorted({p for p in REDACT_VALUES for a in u["alias_of"] if a.startswith(p)})
        if hidden:
            u["target"] = f"(withheld: alias/title of a note under {', '.join(hidden)})"

    # -- frontmatter
    no_fm, missing_keys, illegal, unknown_vals = [], [], [], []
    for rel, fm in fms.items():
        name = rel.rsplit("/", 1)[-1].lower()
        if name.endswith(".excalidraw.md") or ("/" not in rel and name in FRONTMATTER_EXEMPT):
            continue
        if not texts[rel].strip():
            continue  # reported as an empty note instead
        if fm is None:
            no_fm.append(rel)
            continue
        is_template = str(fm.get("type", "")).strip().lower() == "template" or rel.startswith("Templates/")
        miss = [k for k in REQUIRED_KEYS if k not in fm]
        empty = [] if is_template else [k for k in REQUIRED_KEYS if k in fm and k not in MAY_BE_EMPTY and blank(fm[k])]
        if miss or empty:
            missing_keys.append({"note": rel, "missing": miss, "blank": empty})
        dom = str(fm.get("domain", "")).strip().lower()
        vis = str(fm.get("visibility", "")).strip().lower()
        hide = redacted(rel)
        if dom and dom not in LEGAL_VISIBILITY:
            unknown_vals.append({"note": rel, "field": "domain", "value": None if hide else dom})
        if vis and vis not in CORE_VISIBILITY:
            unknown_vals.append({"note": rel, "field": "visibility", "value": None if hide else vis})
        if dom in LEGAL_VISIBILITY and vis in CORE_VISIBILITY and vis not in LEGAL_VISIBILITY[dom]:
            illegal.append({"note": rel, "domain": None if hide else dom, "visibility": None if hide else vis,
                            "allowed": None if hide else sorted(LEGAL_VISIBILITY[dom])})

    # -- inbox
    inbox = []
    for p in files:
        rel = posix(p)
        if not rel.startswith(INBOX_DIR):
            continue
        created, source = None, None
        fm = fms.get(rel)
        if fm:
            created = parse_date(fm.get("created"))
            source = "created:" if created else None
        if created is None:
            created = dt.datetime.fromtimestamp((vault / p).stat().st_mtime).date()
            source = "file mtime"
        inbox.append({"item": rel, "since": created.isoformat(), "age_days": (today - created).days, "source": source})
    inbox.sort(key=lambda i: -i["age_days"])

    # -- untitled / empty
    untitled = [posix(p) for p in files if p.name.lower().startswith("untitled")]
    empty_canvases = []
    for p in files:
        if p.suffix.lower() != ".canvas":
            continue
        raw = (vault / p).read_text(encoding="utf-8", errors="replace").strip()
        if not raw:
            empty_canvases.append({"file": posix(p), "why": "0 bytes"})
            continue
        try:
            data = json.loads(raw)
        except ValueError:
            empty_canvases.append({"file": posix(p), "why": "invalid JSON"})
            continue
        if not isinstance(data, dict):
            empty_canvases.append({"file": posix(p), "why": "not a JSON object"})
        elif not data.get("nodes") and not data.get("edges"):
            empty_canvases.append({"file": posix(p), "why": "no nodes or edges"})
    empty_notes = [rel for rel, t in texts.items() if not t.strip()]

    # -- orphans, duplicates, tags, context packs
    orphans = sorted(rel for rel in texts if rel not in inbound and not rel.startswith("Templates/")
                     and "/" in rel and not rel.lower().endswith(".excalidraw.md"))
    by_base: dict[str, list[str]] = defaultdict(list)
    for rel in texts:
        by_base[rel.rsplit("/", 1)[-1][:-3].lower()].append(rel)
    duplicates = {k: sorted(v) for k, v in sorted(by_base.items()) if len(v) > 1}

    tags: dict[str, set[str]] = defaultdict(set)
    for rel, text in texts.items():
        fm = fms.get(rel)
        found = [t.lstrip("#") for t in as_list(fm.get("tags"))] if fm else []
        _, body = split_frontmatter(text)
        found += [t for t in TAG_RE.findall(strip_code(body)) if re.search(r"[A-Za-z]", t)]
        for t in found:
            tags[t.strip()].add(rel)
    case_groups: dict[str, set[str]] = defaultdict(set)
    for t in tags:
        case_groups[t.lower()].add(t)
    tag_case_drift = {k: sorted(v) for k, v in sorted(case_groups.items()) if len(v) > 1}
    singleton_tags = sorted(t for t, n in tags.items() if len(n) == 1)

    stale_packs = []
    for rel, fm in fms.items():
        if rel.startswith("_system/context-packs/") and fm is not None:
            upd = parse_date(fm.get("updated"))
            if upd is None or (today - upd).days > STALE_PACK_DAYS:
                stale_packs.append({"pack": rel, "updated": upd.isoformat() if upd else None,
                                    "age_days": (today - upd).days if upd else None})

    metrics = {
        "in_scope_notes": len(notes),
        "wikilinks_total": total,
        "unresolved_targets": len(unresolved_list),
        "unresolved_links": sum(u["count"] for u in unresolved_list),
        "alias_only_targets": sum(1 for u in unresolved_list if u["alias_of"]),
        "frontmatter_missing": len(no_fm),
        "frontmatter_missing_keys": len(missing_keys),
        "frontmatter_illegal_pairs": len(illegal),
        "frontmatter_unknown_values": len(unknown_vals),
        "inbox_items": len(inbox),
        "untitled_files": len(untitled),
        "empty_canvases": len(empty_canvases),
        "empty_notes": len(empty_notes),
        "orphan_notes": len(orphans),
        "duplicate_basenames": len(duplicates),
    }
    prev = read_previous_metrics(previous) if previous else None
    return {
        "date": today.isoformat(),
        "scan_source": scan_source,
        "metrics": metrics,
        "previous": {"path": posix(previous.relative_to(vault)) if previous and previous.is_relative_to(vault)
                     else (str(previous) if previous else None),
                     "metrics": prev},
        "unresolved": unresolved_list,
        "frontmatter": {"none": sorted(no_fm), "missing_keys": sorted(missing_keys, key=lambda x: x["note"]),
                        "illegal_pairs": sorted(illegal, key=lambda x: x["note"]),
                        "unknown_values": sorted(unknown_vals, key=lambda x: x["note"])},
        "inbox": inbox,
        "untitled": sorted(untitled),
        "empty_canvases": empty_canvases,
        "empty_notes": sorted(empty_notes),
        "orphans": orphans,
        "duplicates": duplicates,
        "tags": {"distinct": len(tags), "case_drift": tag_case_drift, "singletons": singleton_tags},
        "stale_context_packs": stale_packs,
    }


def read_previous_metrics(path: Path) -> dict | None:
    """Parse the `## Metrics` table a previous /garden report wrote, if any."""
    try:
        text = path.read_text(encoding="utf-8", errors="replace")
    except OSError:
        return None
    m = re.search(r"^## Metrics\s*$(.*?)(?=^## |\Z)", text, re.M | re.S)
    if not m:
        return None
    out = {}
    for row in re.finditer(r"^\|\s*`([a-z_]+)`\s*\|[^|\n]*\|\s*(\d+)\s*\|", m.group(1), re.M):
        out[row.group(1)] = int(row.group(2))
    return out or None


# --------------------------------------------------------------- markdown

def code(s: str) -> str:
    return f"`{s}`"


def group_key(rel: str) -> str:
    segs = rel.split("/")
    if len(segs) == 1:
        return "(vault root)"
    return "/".join(segs[:2]) if len(segs) > 2 else segs[0]


def grouped(items: list, path_of=lambda x: x) -> dict[str, list]:
    g: dict[str, list] = defaultdict(list)
    for it in items:
        g[group_key(path_of(it))].append(it)
    return dict(sorted(g.items()))


def short(rel: str, prefix: str) -> str:
    return rel[len(prefix) + 1:] if prefix != "(vault root)" and rel.startswith(prefix + "/") else rel


def list_grouped(paths: list[str], *, inline: int = 3, examples: int = 3) -> list[str]:
    """One bullet per folder group; small groups list every note, big ones show examples."""
    out = []
    for prefix, items in grouped(paths).items():
        label = f"**{prefix}/**" if prefix != "(vault root)" else "**(vault root)**"
        names = [code(short(i, prefix)) for i in items]
        if len(items) <= inline:
            out.append(f"- {label} ({len(items)}): " + ", ".join(names))
        else:
            out.append(f"- {label} ({len(items)}): e.g. " + ", ".join(names[:examples]))
    return out


def render_md(r: dict) -> str:
    m, prev = r["metrics"], (r["previous"] or {}).get("metrics")
    L = ["## Metrics", "",
         f"Scan set: {r['scan_source']}. Machine-readable: the next `/garden` run diffs against this table. "
         "Keep the keys.", "",
         "| Key | Measure | Value | Δ since last |", "| --- | --- | --- | --- |"]
    for k, label in METRIC_KEYS:
        d = "—"
        if prev and k in prev:
            diff = m[k] - prev[k]
            d = f"{diff:+d}" if diff else "0"
        L.append(f"| `{k}` | {label} | {m[k]} | {d} |")
    L.append("")
    if not prev:
        L += ["No comparable `## Metrics` table in the previous report"
              + (f" ({code(r['previous']['path'])})" if r["previous"]["path"] else "") + ".", ""]

    L += ["## Possible Duplicates", "",
          f"{m['duplicate_basenames']} note names exist in more than one folder; a bare `[[Name]]` link to them is ambiguous.", ""]
    for name, paths in r["duplicates"].items():
        if len(paths) <= 3:
            L.append(f"- **{name}**: " + ", ".join(code(p) for p in paths))
        else:
            where = ", ".join(f"{code(k)} ×{len(v)}" for k, v in grouped(paths).items())
            L.append(f"- **{name}**: {len(paths)} copies — {where}")
    L.append("")

    L += ["## Broken Links", ""]
    alias = [u for u in r["unresolved"] if u["alias_of"]]
    plain = [u for u in r["unresolved"] if not u["alias_of"]]
    L.append(f"{m['unresolved_targets']} unresolved targets across {m['unresolved_links']} links "
             f"(of {m['wikilinks_total']} wikilinks checked; code blocks and inline code ignored).")
    L.append("")
    if alias:
        L += ["### Resolve only via `aliases:` / `title:` (Obsidian leaves these unresolved)", "",
              "Fix by linking the file name, e.g. `[[File Name|Alias]]`.", "",
              "| Target | Links | Matching note(s) | Linked from |", "| --- | --- | --- | --- |"]
        for u in alias:
            L.append(f"| {code(u['target'])} | {u['count']} | {', '.join(code(a) for a in u['alias_of'])} | "
                     f"{fmt_sources(u['sources'])} |")
        L.append("")
    if plain:
        L += ["### No matching note", "",
              "| Target | Links | Linked from |", "| --- | --- | --- |"]
        for u in plain:
            L.append(f"| {code(u['target'])} | {u['count']} | {fmt_sources(u['sources'])} |")
        L.append("")

    fm = r["frontmatter"]
    L += ["## Frontmatter", "",
          f"Checked against [[frontmatter-schema|Frontmatter Schema]]: {m['frontmatter_missing']} notes without frontmatter, "
          f"{m['frontmatter_missing_keys']} missing or blank required keys, "
          f"{m['frontmatter_illegal_pairs']} illegal domain/visibility pairs, "
          f"{m['frontmatter_unknown_values']} non-schema values. "
          "Root README/AGENTS/CLAUDE, Excalidraw drawings and empty notes are not checked here.", ""]
    if fm["illegal_pairs"]:
        L += ["### Illegal domain/visibility pairs", "",
              "| Folder | Notes | domain → visibility | Allowed | Examples |", "| --- | --- | --- | --- | --- |"]
        combos: dict[tuple, list] = defaultdict(list)
        for x in fm["illegal_pairs"]:
            if x["domain"] is None:
                combos[(group_key(x["note"]), "(withheld)", "(withheld)", "(withheld)")].append(x["note"])
            else:
                combos[(group_key(x["note"]), x["domain"], x["visibility"], " or ".join(x["allowed"]))].append(x["note"])
        for (prefix, dom, vis, allowed), notes in sorted(combos.items()):
            ex = ", ".join(code(short(n, prefix)) for n in notes[:3]) + (" …" if len(notes) > 3 else "")
            L.append(f"| {code(prefix)} | {len(notes)} | {dom} → {vis} | {allowed} | {ex} |")
        L.append("")
    if fm["unknown_values"]:
        L += ["### Non-schema values", "", "| Note | Field | Value |", "| --- | --- | --- |"]
        L += [f"| {code(x['note'])} | {x['field']} | {code(x['value']) if x['value'] is not None else '(withheld)'} |"
              for x in fm["unknown_values"]]
        L.append("")
    if fm["none"]:
        L += ["### No frontmatter", ""] + list_grouped(fm["none"]) + [""]
    if fm["missing_keys"]:
        L += ["### Missing or blank required keys", "",
              "| Folder | Notes | Most often missing | Examples |", "| --- | --- | --- | --- |"]
        for prefix, items in grouped(fm["missing_keys"], lambda x: x["note"]).items():
            cnt: dict[str, int] = defaultdict(int)
            for x in items:
                for k in x["missing"] + [f"{b} (blank)" for b in x["blank"]]:
                    cnt[k] += 1
            common = ", ".join(f"{k} ×{n}" if len(items) > 1 else k
                               for k, n in sorted(cnt.items(), key=lambda kv: (-kv[1], kv[0]))[:6])
            ex = ", ".join(code(short(x["note"], prefix)) for x in items[:3]) + (" …" if len(items) > 3 else "")
            L.append(f"| {code(prefix)} | {len(items)} | {common} | {ex} |")
        L.append("")

    L += ["## Inbox", "", f"{m['inbox_items']} items in `{INBOX_DIR}`, oldest first.", ""]
    if r["inbox"]:
        L += ["| Item | Since | Age (days) | Dated by |", "| --- | --- | --- | --- |"]
        L += [f"| {code(i['item'][len(INBOX_DIR):])} | {i['since']} | {i['age_days']} | {i['source']} |" for i in r["inbox"]]
        L.append("")

    L += ["## Cleanup Candidates", "",
          "Listed only. Nothing was moved or deleted.", ""]
    if r["untitled"]:
        L += ["### Untitled files", ""] + [f"- {code(u)}" for u in r["untitled"]] + [""]
    if r["empty_canvases"]:
        L += ["### Empty or invalid canvases", ""] + [f"- {code(c['file'])} — {c['why']}" for c in r["empty_canvases"]] + [""]
    if r["empty_notes"]:
        L += ["### Empty notes", ""] + [f"- {code(n)}" for n in r["empty_notes"]] + [""]
    if not (r["untitled"] or r["empty_canvases"] or r["empty_notes"]):
        L += ["None.", ""]

    L += ["## Orphan Notes", "",
          f"{m['orphan_notes']} notes have no inbound wikilink from another note "
          "(root files, templates and drawings excluded). Many are structural; triage, don't bulk-link.", ""]
    L += list_grouped(r["orphans"], inline=6, examples=4)
    L.append("")

    t = r["tags"]
    L += ["## Tag Drift", "", f"{t['distinct']} distinct tags; {len(t['singletons'])} used by one note only.", ""]
    if t["case_drift"]:
        L += ["Same tag, different casing:", ""] + [f"- {', '.join(code('#' + x) for x in v)}" for v in t["case_drift"].values()] + [""]
    else:
        L += ["No casing drift.", ""]

    L += ["## Context Packs", ""]
    if r["stale_context_packs"]:
        L += [f"Not updated in {STALE_PACK_DAYS}+ days:", ""]
        L += [f"- {code(p['pack'])} — updated {p['updated'] or 'unknown'}" for p in r["stale_context_packs"]]
    else:
        L.append(f"All context packs updated within {STALE_PACK_DAYS} days.")
    L.append("")
    return "\n".join(L)


def fmt_sources(srcs: list[str], limit: int = 4) -> str:
    shown = ", ".join(code(s) for s in srcs[:limit])
    return shown + (f" +{len(srcs) - limit} more" if len(srcs) > limit else "")


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    ap.add_argument("--vault", type=Path, default=Path("."))
    ap.add_argument("--previous", type=Path, help="previous Vault Health report to diff against")
    ap.add_argument("--format", choices=["md", "json"], default="md")
    ap.add_argument("--today", help="override today's date (YYYY-MM-DD)")
    ap.add_argument("--inbox", default="01 Inbox", help="inbox folder, relative to the vault (default: 01 Inbox)")
    ap.add_argument("--exclude", action="append", default=[], metavar="FOLDER",
                    help="private folder never read or listed (repeatable)")
    ap.add_argument("--redact", action="append", default=[], metavar="FOLDER",
                    help="folder whose frontmatter values are withheld from the report (repeatable)")
    a = ap.parse_args()
    global EXCLUDE_ROOT, EXCLUDE_PREFIXES, REDACT_VALUES, INBOX_DIR
    norm = lambda f: f.strip().replace("\\", "/").strip("/") + "/"
    INBOX_DIR = norm(a.inbox)
    EXCLUDE_PREFIXES = EXCLUDE_PREFIXES + tuple(norm(f) for f in a.exclude)
    EXCLUDE_ROOT = EXCLUDE_ROOT | {norm(f)[:-1] for f in a.exclude if "/" not in norm(f)[:-1]}
    REDACT_VALUES = REDACT_VALUES + tuple(norm(f) for f in a.redact)
    vault = a.vault.resolve()
    if not (vault / ".obsidian").is_dir():
        print(f"not an Obsidian vault: {vault}", file=sys.stderr)
        return 2
    today = dt.date.fromisoformat(a.today) if a.today else dt.date.today()
    prev = a.previous.resolve() if a.previous else None
    result = run(vault, today, prev)
    sys.stdout.reconfigure(encoding="utf-8")
    print(json.dumps(result, indent=2, ensure_ascii=False) if a.format == "json" else render_md(result))
    return 0


if __name__ == "__main__":
    sys.exit(main())

---
name: garden
description: Report-only Obsidian vault health check (unresolved and alias-only wikilinks, frontmatter gaps, inbox age, Untitled and empty files, delta since the last report), written to <reviews folder>/Vault Health - YYYY-MM-DD.md
disable-model-invocation: true
triggers:
  - /garden
---

# /garden — vault health report

A report-only vault gardener. If your vault has its own gardening procedure
(its CLAUDE.md or a skill note may name one), read it first; its hard stops
apply here unchanged.

`/garden` never mutates the vault. Any cleanup a procedure allows (normalising
frontmatter, moving generated artifacts to a trash-review folder) needs an
explicit, separate request. Cleanup candidates are **listed**, and nothing
else.

## Configuration (defaults; adjust to your vault)

| Setting | Default | Where |
| --- | --- | --- |
| Reports folder | `06 Reviews/` | this file |
| Inbox folder | `01 Inbox/` | `--inbox` |
| Report template | `Templates/Vault Health Report.md` (optional) | this file |
| Frontmatter schema | `REQUIRED_KEYS`, `LEGAL_VISIBILITY` | top of `scripts/garden_check.py` |
| Private folders, never read or listed | none | `--exclude <folder>` (repeatable) |
| Folders whose frontmatter values are withheld | none | `--redact <folder>` (repeatable) |
| Context packs | `_system/context-packs/` | `scripts/garden_check.py` |

If the vault's CLAUDE.md names different folders, use those.

## When to use

Only when the human types `/garden`. It is not model-invoked. If the human then
asks for a fix from the report, that is a new, explicit task, not part of this
skill.

## Hard rules

- **Write exactly one file:** `<reviews folder>/Vault Health - YYYY-MM-DD.md`. Never
  delete, move, rename or rewrite another note, attachment, canvas or base. That
  includes "obvious" frontmatter fixes.
- **Never read or list private folders.** Pass each one with `--exclude`; the
  checker skips it without opening it.
- **Out of scope:** `--exclude` folders, `.obsidian/`, `.trash/`, `.claude/`,
  `.agents/`, any `.secrets/`. The checker prunes every dot-folder, which is
  also what Obsidian itself does.
- **Only what git would sync gets read.** The report may sync to a remote, so the
  checker builds its scan set with
  `git ls-files --cached --others --exclude-standard`: tracked files, plus
  untracked files that aren't ignored. Gitignored notes (local-only personal
  notes, access details, private folders, `.secrets/`) are never opened or
  named. Links into them still resolve, because targets are matched against
  file names alone. If git is unavailable, the checker falls back to a
  filesystem walk and says so in the Metrics line. Treat that run as unsafe:
  check the output before pasting any of it.
- **Paths and counts, never contents.** Don't quote note text in the report.
  For notes under any `--redact` folder, the checker withholds frontmatter
  values, giving the path and field name only. That includes a link target
  that is such a note's alias. Don't add the values back by hand.
- **Every wikilink you write must resolve by file name.** Obsidian does not
  resolve `[[Alias]]` or `[[Title]]`. Link `[[file-name|Shown Text]]` instead.
- **Git:** follow the vault's CLAUDE.md. If it syncs on its own, just write the
  report. In a worktree or a cloud session, commit only the report.

## Procedure

### 1. Pre-flight

1. If the vault is a git repo with a remote, `git pull --rebase`. The vault may
   move between sessions.
2. If the vault keeps a sync log (for example `_system/status/sync.log`), read it. Any line ending
   `CONFLICT-NEEDS-HUMAN` or `FAILED-NEEDS-HUMAN`, or any `privacy` action,
   goes at the top of **Needs Attention**. Do not try to fix it.
3. Find the previous report: the newest `<reviews folder>/Vault Health - *.md` dated
   before today. If a report for today already exists, ask before replacing it.

### 2. Run the checker

The checks are deterministic, so they live in a bundled script and two runs
always count the same way:
[scripts/garden_check.py](scripts/garden_check.py). It needs only the Python 3
standard library, and it never writes to the vault.

```bash
# from the vault root; use `python` where `python3` is missing (Windows)
# add --inbox, --exclude and --redact per the Configuration table
python3 <skill dir>/scripts/garden_check.py --vault . \
  --previous "<reviews folder>/Vault Health - <previous date>.md" > "<scratch>/garden.md"
python3 <skill dir>/scripts/garden_check.py --vault . --format json > "<scratch>/garden.json"
```

Put both outputs in the session scratchpad, never in the vault. What it checks:

| Check | Rule |
| --- | --- |
| Unresolved wikilinks | `[[…]]` and `![[…]]` in Markdown notes, frontmatter included; fenced code and inline code ignored; Templater `<% %>` ignored. Resolves the way Obsidian does: file name, path or path suffix, attachment name with extension, case-insensitive. A link that matches only a note's `aliases:` or `title:` is **unresolved** and is reported separately, with the file it was probably meant to reach. |
| Frontmatter | Missing frontmatter, missing required keys (`title type domain status visibility created updated tags related`), blank required values (templates are exempt), domain/visibility pairs that `LEGAL_VISIBILITY` forbids, non-schema domain/visibility values. Root `README`/`AGENTS`/`CLAUDE` and Excalidraw drawings are exempt. |
| Inbox | Every file under the inbox folder, aged from `created:`, else file mtime (the report says which). |
| Cleanup candidates | `Untitled*` files, `.canvas` files that are empty, invalid JSON or have no nodes and no edges, and empty notes. |
| Also, for the template's sections | Duplicate basenames (ambiguous bare links), orphan notes, tag casing drift and singletons, context packs not updated in 90+ days. |
| Delta | Parses the previous report's `## Metrics` table and fills the Δ column. |

### 3. The delta when the previous report has no Metrics table

Older hand-written reports may be prose. Take only the numbers they state
outright, such as notes checked, broken links, orphans or Untitled files, and
compare those. Say plainly where the methods differ. If those reports used
alias-aware resolution, their broken-link counts are **undercounts** compared
with this checker. Never estimate a number the previous report didn't give.

### 4. Write the report

Start from the report template if the vault has one, and fill in the
frontmatter per the vault's schema. A default shape:

```yaml
title: Vault Health - YYYY-MM-DD
type: review
domain: agent
status: active
visibility: shared        # agent allows hidden or shared
created: YYYY-MM-DD
updated: YYYY-MM-DD
tags:
  - topic/maintenance
related:
  - "[[Vault Health - <previous date>]]"
last_agent: claude
last_agent_run: YYYY-MM-DD-garden
agent_modified: true
review_state: report-only
```

Body, in this order. Template headings come first in the template's order;
the checker's extra sections slot in after them:

1. **Summary.** The headline numbers, the delta, and a short verdict on what
   changed and what matters most. Written by you.
2. **Metrics.** Paste it from the checker output. Keep the `` `key` `` column
   exactly as it is, because the next run parses it.
3. **Fixed Automatically.** "Nothing. `/garden` is report-only."
4. **Needs Attention.** Your triage. Sync-log alarms come first, then whatever
   breaks navigation (alias-only links clustered on a few targets are usually
   one fix each), then privacy or schema problems. Group problems by cause,
   such as one folder with its own frontmatter convention, rather than listing
   notes.
5. **Possible Duplicates**, **Broken Links**, **Frontmatter**, **Inbox**,
   **Cleanup Candidates**, **Orphan Notes**, **Tag Drift**, **Context Packs**.
   Paste these from the checker. Add a sentence of interpretation where it
   helps; for example, orphans often fall once alias-only links are fixed.
6. **RAG Index Status.** One line from the vault's index status note, if it
   has one (for example `_system/status/rag-index.md`), or "Not checked."
7. **Suggested Next Actions.** An ordered list, each item small enough for one
   session. Begin by saying which of the previous report's actions are still
   open.

### 5. Verify, then tell the human

1. Re-run the checker. The new report must not appear as a source of any
   unresolved link. Running with `--previous` set to the new report must fill
   every Δ cell. The only movement should come from the report itself: one
   more note and its own links.
2. Reply with the report path and the headline numbers (unresolved targets and
   links, frontmatter issues, inbox items, Untitled and empty files), plus
   anything you couldn't check.

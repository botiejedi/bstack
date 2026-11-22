#!/usr/bin/env python3
"""Rank Claude Code plugins by install count and flag the ones already installed.

Reads only local files Claude Code keeps under ~/.claude:
  plugins/plugin-catalog-cache.json   install counts and context cost per plugin
  plugins/installed_plugins.json      what is installed
  settings.json                       enabledPlugins (on/off)

Usage: python3 catalog.py [--top N] [--all]
  --top N   show the N most-installed plugins (default 40)
  --all     include plugins that are already installed
"""
import argparse
import json
import sys
from datetime import datetime, timezone
from pathlib import Path

CLAUDE = Path.home() / ".claude"


def load(path):
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (OSError, ValueError):
        return {}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--top", type=int, default=40)
    ap.add_argument("--all", action="store_true")
    args = ap.parse_args()

    cache = load(CLAUDE / "plugins" / "plugin-catalog-cache.json")
    catalog = cache.get("catalog", {})
    plugins = catalog.get("plugins", {})
    if not plugins:
        sys.exit("No catalog cache at ~/.claude/plugins/plugin-catalog-cache.json. "
                 "Open /plugin once so Claude Code downloads it, or fall back to web search.")

    enabled = load(CLAUDE / "settings.json").get("enabledPlugins", {})
    installed = set(load(CLAUDE / "plugins" / "installed_plugins.json").get("plugins", {})) | set(enabled)
    installed_names = {i.split("@")[0] for i in installed}

    stamp = catalog.get("installs_generated_at") or cache.get("fetchedAt", "")
    age = ""
    try:
        when = datetime.fromisoformat(stamp.replace("Z", "+00:00"))
        days = (datetime.now(timezone.utc) - when).days
        age = f" ({days} days old{' - STALE, confirm popularity with a web search' if days > 30 else ''})"
    except ValueError:
        pass
    print(f"Install counts as of {stamp[:10] or 'unknown'}{age}")
    print("installs  state  ctx  id  |  description")

    rows = sorted(plugins.items(), key=lambda kv: -(kv[1].get("unique_installs") or 0))
    shown = 0
    for pid, p in rows:
        name = p.get("plugin", pid.split("@")[0])
        if pid in installed or name in installed_names:
            state = "on" if enabled.get(pid, True) else "off"
            if not args.all:
                continue
        else:
            state = "new"
        tokens = next(iter(p.get("tokens", {}).values()), {})
        desc = (p.get("marketplace_entry") or {}).get("description", "").replace("\n", " ")
        print(f"{p.get('unique_installs') or 0:>8}  {state:<5} {tokens.get('always_on', '?'):>4}  {pid}  |  {desc[:120]}")
        shown += 1
        if shown >= args.top:
            break


if __name__ == "__main__":
    main()

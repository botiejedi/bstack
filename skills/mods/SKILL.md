---
name: mods
description: Use when the user asks which Claude Code plugins or mods are popular, what they are missing, wants plugin recommendations, wants a set of plugins installed, or wants an infographic or guide on how and when to use plugins they just added. Also triggers on /mods.
---

# Mods

## Overview

Recommend popular Claude Code plugins the user does not already have, install the ones they pick, and leave them a one-page guide showing **when** each plugin fires and **how** to use it.

**Core principle:** popularity is a starting point, not the answer. A plugin that duplicates a built-in skill, or one that doesn't fit the user's stack, is noise even with a million installs.

## Workflow

1. **Rank what's missing.** Run `python3 scripts/catalog.py --top 40` (use `python -I` on Windows). It reads Claude Code's local catalog cache, which holds install counts and the always-on context cost (`ctx`, in tokens). It hides plugins that are already installed. Add `--all` to see those too.
   - If the header says `STALE`, say so, and check current popularity with one web search.
   - Third-party marketplaces have no install data. Name them separately, and don't rank them.
2. **Filter by fit.** Drop a plugin when:
   - a skill or plugin already loaded does the same job. Check the session's skill list: built-in `/code-review`, `/simplify` and skill-creator often duplicate catalog entries.
   - it targets a stack the user doesn't use. Check their CLAUDE.md for language and platform.
   - its `ctx` is high and its benefit is narrow.
3. **Recommend at most 5.** Show a table with plugin, installs and why it fits *this* user. Then list what you skipped and why, one line each. Ask which ones to install. Install nothing yet.
4. **Install.** Run `claude plugin install <name>@<marketplace>` for each one.
   - If the user has a managed plugin list or a security gate (an `agent-skills` manifest, for example), add the plugins there instead, or tell them the direct install skips that gate.
   - LSP plugins need the language server binary. Install it with `rustup component add rust-analyzer` or the README's equivalent, then check that the binary starts.
5. **Read before you write.** For each plugin, read `~/.claude/plugins/cache/<marketplace>/<name>/<version>/`: the README, `commands/*.md`, `skills/*/SKILL.md` and `hooks/hooks.json`. Every command, event and env var in the guide must come from these files.
6. **Build the guide.** Copy `guide-template.html` and replace its five plugins with the new ones:
   - **Matrix:** one row per plugin. Columns follow a single turn: you send a prompt → Claude edits a file → Claude runs a command → turn ends → Claude runs git commit. A filled tag means automatic. An outlined tag means the user triggers it. Put a tag only where the plugin's hooks or tools actually fire.
   - **Cards:** Use it when / Type this (copyable) / You'll see / Watch out.
   - "Watch out" names real costs: usage, data leaving the machine, files that sync or get committed, required env vars.
   - Update the date, the "Start here" steps and the footer.
7. **Deliver.** Publish the guide as an Artifact. Also save it wherever the user keeps deliverables (their memory may name a folder). Tell them to restart Claude Code, because plugins load at startup.
8. **Document it in the wiki (optional).** Do this step only if the user's Obsidian vault keeps a tool wiki (for example a `Tool Wiki/` folder with one page per plugin, and a generated index such as `Claude Wiki`). Otherwise skip it.
   - If the vault has refresh scripts that generate those pages (its CLAUDE.md should name them), run them from the vault root so the new pages and rows exist now instead of at the next session start.
   - On each new plugin's wiki page, fill its personal-notes section (for example `## My notes`) with that plugin's card from the guide (Use it when / Type this / Watch out). Add the guide's Artifact link, and mark the page documented if the frontmatter has a field for it (for example `docs: done`).
   - Leave anything between generated-content markers (for example `<!-- tool-wiki:… -->`) alone, because the scripts rewrite it.

## Common mistakes

| Mistake | Fix |
| --- | --- |
| Recommending by installs alone | Run the step 2 filters first |
| Installing before the user picks | Recommend, then ask |
| Guide lists a command you didn't read | Write only what came from the plugin's files |
| Matrix tags a column the plugin never hooks | Check `hooks.json` events: PreToolUse, PostToolUse, Stop, UserPromptSubmit |
| Saying the plugins work now | They load only after a restart |
| New plugin's wiki page left as a bare README | Fill `My notes` from the guide (step 8) |
| Editing a generated wiki table | Write outside the markers. The next refresh overwrites what's inside them |

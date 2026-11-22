---
name: handoff
private: false
description: "Use when the user wants to hand off, checkpoint or save progress before compacting context, ending a session, or passing work to a fresh agent (\"make a handoff\", \"before we compact\", \"/handoff\"). Writes a complete, verified recovery document from live state, updates the pointers to it, then gives the user the exact /compact line to run."
metadata:
  version: "1.0.0"
  owner: botiejedi
  created: 2026-09-25
user-invocable: true
argument-hint: "[project or topic] [--no-compact]"
---

# /handoff: write a recovery point, then compact

Compaction and new sessions lose everything that isn't written down. In-process subagents do **not** survive a compaction, and scheduled session jobs die with the session. This skill writes the one document a fresh context needs to resume without asking the user anything, then hands the user the `/compact` command.

**Limit:** you can't run `/compact` yourself. It's a built-in command only the user can type. Your job ends by printing the exact line for them to run.

## 1. Gather live state (verify; don't rely on recollection)

Collect facts from tools, not from memory of the conversation:

- **Repos touched this session:**
  - `git status -sb`, `git log --oneline -3`
  - branch heads: `git rev-parse --short origin/<branch>`
  - open PRs: `gh pr list --json number,title,isDraft,headRefName`
  - worktrees: `git worktree list`
- **Agents and background work:** `ListAgents`, running background tasks, and `CronList`. Record what each is doing. Anything still running will be lost at compaction: either wait for it, or record exactly how to restart it.
- **Decisions:** every decision the user made this session (with their words where they matter), and every decision still pending with your recommendation.
- **Changes to real systems** (servers, accounts, configs): what was applied, how it was verified, where the rollback is.
- **Existing handoff docs** for this project: find the newest (for example `Handoff - *.md`), and read it so nothing it carried is dropped.

## 2. Choose where it goes

1. If the project already has handoff docs, write the new one **next to them** as `Handoff - <YYYY-MM-DD>.md`. If one already exists for today, update it in place and bump `updated:`.
2. Otherwise, in an **Obsidian vault** (a cwd inside one): `<vault>/<projects folder>/<Project>/Handoff - <YYYY-MM-DD>.md`, with frontmatter copied from a neighbouring note in the same folder (keep its keys; set `created`/`updated` and any agent-provenance fields the vault uses). Follow the vault's CLAUDE.md for whether to just edit or branch/commit, and for any folders agents must not touch.
3. Otherwise, in a code repo: `docs/handoff/HANDOFF-<YYYY-MM-DD>.md`. Leave it uncommitted unless the user asks, and say where it is.

**Secrets rule:** never write credential values, tokens, or exploitable security specifics (open ports, IPs tied to weaknesses, credential paths) into a tracked doc. Put those in a gitignored location (for example a `.secrets/` folder) and link to it by path only.

## 3. Write it: required sections

Keep it skimmable, with tables where possible. Every claim must be something you verified in step 1.

1. **Start here:** a callout saying which doc it supersedes, that agents don't survive compaction (respawn fresh agents briefed from this doc), and any standing reading preference the user set (for example ADHD mode).
2. **What we're building:** one paragraph.
3. **Status at a glance:** a table of the major pieces and their state.
4. **Decisions:** everything the user decided, with a pointer to the canonical record if one exists (for example a plan doc section).
5. **Branches, PRs, worktrees:** a table with exact heads.
6. **Next steps in order:** numbered, each small enough to act on. Include pending user decisions with your recommendation, so the next context can ask them directly.
7. **Systems touched:** what changed, how it was verified, and the rollback. Link to private detail rather than copying it.
8. **Operational facts:** tool quirks, credential *access paths* (never values), rate limits, and things that were blocked and why.
9. **Open items for the user:** a checklist.

## 4. Update the pointers

- **Mark the older handoff superseded:** add a callout at the top linking to the new one. Don't delete it.
- **Project note:** if the project has a hub note with `next_action`, update it to point at the new handoff.
- **Memory:** if a memory entry points at the recovery doc, update it to "the newest `Handoff - <date>.md`". If none exists and the work spans sessions, create one (and add its index line).

## 5. Verify, then hand over

1. Re-read the new doc once. Check that the branch heads, PR numbers and file paths still match what you just ran, and fix any drift.
2. Check that nothing from the previous handoff was silently dropped (open items, glue lists, owner decisions).
3. Unless `--no-compact` was passed, finish with exactly this shape (short, no recap):

   > Handoff saved: `<path>`
   >
   > Run: `/compact Resume from <path>. Next: <the single next step>.`
   >
   > After compacting, I'll read that file first and continue from step <n>.

The text after `/compact` becomes the compaction's focus instruction, so it must name the handoff path and the next step.

## After the compaction (the resuming context)

- Read the handoff named in the compaction summary **before** any other action.
- Don't message old agent IDs. Spawn fresh agents from the doc when needed.
- Re-verify anything time-sensitive (branch heads, running jobs) before acting on it.

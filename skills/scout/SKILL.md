---
name: scout
private: false
description: Research topics and create briefs — queue for later or research immediately, optionally with a 30-day community pulse
triggers:
  - /scout
  - scout
  - scout this
  - research this
  - look into
  - dig into
  - I'm curious about
  - what are people saying
  - --pulse
---

# /scout — Research & Create Briefs

Researches topics and creates structured Research Briefs.

## Vault layout (configurable)

Run from your Obsidian vault root. These are defaults — edit the table to
match your vault's folders and use your names everywhere below.

| Role | Default |
|------|---------|
| Inbox (new captures) | `Inbox/` |
| Notes (briefs, logs) | `Notes/` |
| Sources (raw evidence dumps) | `Sources/` |
| Topic indexes | `Indexes/<Topic> Index.md` |

Templates ([[Research Brief]], [[Research Queue]]) are optional: if your vault lacks one,
write a plain note with `created`/`updated` dates and the listed tags.

## Two Modes

| Mode | When | Output |
|------|------|--------|
| Queue It | "later", "when you have time" | Note in `Inbox/` with `topic/research` tag |
| Research Now | "now", "dig into", "scout this" | Full Research Brief in `Notes/` |

## Step-by-Step: Queue Mode

1. Extract research topic
2. Create note in `Inbox/` with `topic/research` tag and priority
3. Add entry to [[Research Queue]]
4. Confirm added to queue

## Step-by-Step: Research Now

### Step 1: Extract Topic and Question
Parse main topic, specific question, and constraints.

### Step 2: Check Existing Knowledge
Search vault for related notes. MCP-first (`obsidian_simple_search` /
`obsidian_complex_search`), obsidian-cli fallback, Grep last resort.

### Step 3a: Conduct Research (web)
Web search for: main question, comparisons, recent updates, community opinions.

### Step 3b: Community Pulse (optional)
Decide whether the topic wants the `last30days` engine — real posts and
engagement from Reddit, Hacker News, YouTube, GitHub, Polymarket, and X across
the trailing 30 days.

| Signal | Call |
|--------|------|
| Current events, product/model release, "what are people saying", opinions, X vs Y, buying decision | Propose the pulse |
| Settled technical facts, API syntax, historical topics, questions about the vault itself | Skip silently |
| User passed `--pulse` or `--no-pulse` | Obey it, no confirmation |

**Auto-detect, then confirm.** The sweep costs ~2 minutes of live network, so
ask in one line before running: `Topic looks current — add a 30-day community
pulse (Reddit/HN/YouTube/GitHub)? ~2 min.` Wait for the answer.

On yes, call the engine directly. Do **not** invoke the `/last30days` skill:
its output contract bans `##` headers and mandates a badge and invitation,
which fight the [[Research Brief]] template.

```bash
export LAST30DAYS_NATIVE_SEARCH=1
VAULT="${CLAUDE_PROJECT_DIR:-$PWD}"
L30=$(ls -d ~/.claude/plugins/cache/last30days-skill/last30days/*/skills/last30days 2>/dev/null | sort -V | tail -1)
python3 "$L30/scripts/last30days.py" "<anchored topic>" \
  --emit=compact \
  --save-dir="$VAULT/Sources/Last30Days"
```

Anchor collision-prone names before passing them (`Mistral AI new model`, not
`mistral`). Add `--subreddits=` and `--github-repo=` when Step 1 resolved them.
Read the engine's `Saved output to <path>` line for the real filename — never
recompute the slug. The engine's evidence clusters are raw input: synthesize
them, never paste them into the brief.

### Step 3c: Stash the Dump
The engine wrote a raw evidence file into `Sources/Last30Days/`. Prepend
vault frontmatter so it indexes and links:

```yaml
title: Last30Days - <Topic>
type: capture
domain: source
status: active
visibility: hidden
created: <YYYY-MM-DD>
updated: <YYYY-MM-DD>
tags:
  - topic/research
  - topic/capture
related:
  - "[[Research Brief - <Topic>]]"
capture_source: last30days
captured_at: <ISO-8601>
```

`type: capture` + `visibility: hidden` marks it as un-synthesized raw
evidence. Adjust the frontmatter keys to your vault's schema. Dumps land in
`Sources/Last30Days/` because they are topic-scoped, not feed-scoped.

### Step 4: Create Research Brief
Create `Notes/Research Brief - [Topic].md` from the [[Research Brief]]
template (tag `topic/research`), all sections filled:
- TL;DR (2-3 sentences)
- Key Findings (organized by sub-topic)
- Community Pulse (Last 30 Days) — **only when 3b ran**
- Action Items (Now/Soon/Later)
- Budget Considerations (if spending involved)
- Rabbit Holes Worth Exploring
- Sources

Community Pulse holds: 2-4 findings as bold-lead-in bullets, at least two
verbatim comments attributed with vote counts (`u/name`, 856 upvotes), the
engine's per-source counts, and a wikilink to the Step 3c dump. Quote real
comments — a 856-upvote reply outweighs the parent post. Keep web findings in
Key Findings and community findings here; do not blend them.

### Step 5: Update Indices
- Add to [[Research Queue]]
- Add to the relevant `Indexes/<Topic> Index.md` if one exists
- Link the Step 3c dump from the brief's Sources section

### Step 6: Present Summary
Show TL;DR, key takeaway, top actions, and link to full brief.

## Error Handling

| Error | Response |
|-------|----------|
| Topic too broad | Ask to narrow down |
| No sources found | Report what was found, offer different terms |
| Brief exists | Offer to update or create separate |
| Pulse declined | Skip 3b and 3c, omit the Community Pulse section |
| Engine missing, or Python < 3.12 | Say so in one line, continue web-only |
| Engine says "Nothing solid this window" | Record that verbatim in the brief; never pad the section with web results dressed as community signal |
| A source reports partial / rate-limited / unreachable | Do not write "nothing on X" for it; say coverage was partial |

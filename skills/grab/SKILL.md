---
name: grab
description: Pull vault context into conversation — search notes, indices, and project context
triggers:
  - /grab
  - grab
  - pull up
  - find
  - what do I know about
  - search my vault
---

# /grab — Pull Vault Context

Searches your Obsidian vault and brings relevant notes into the current conversation.

## Vault layout (configurable)

Run from your Obsidian vault root. These are defaults — edit the table to
match your vault's folders and use your names everywhere below.

| Role | Default |
|------|---------|
| Projects (one note per project) | `Projects/` |
| Topic indexes | `Indexes/<Topic> Index.md` |

## When to Use

- "What do I know about X?"
- "Grab everything about [topic]"
- "Pull up my notes on [subject]"
- "Find what I've saved about [thing]"

## Step-by-Step Execution

### Step 1: Parse the Query
Extract the search topic from the user's message. Handle variations:
- "/grab mac switching" → topic: "mac switching"
- "what do I know about neural networks" → topic: "neural networks"

### Step 2: Search the Vault
MCP-first: `obsidian_simple_search` / `obsidian_complex_search`.
Fallback: obsidian-cli (`obsidian search:context query="[topic]" limit=10`,
`obsidian tags name="topic/[topic]" verbose`).
Last resort: Grep tool on vault directories.
Include `Indexes/` and `Projects/` in scope.

### Step 3: Read Top Results
For each matching file (up to 5-7 most relevant):
1. Read the full note content
2. Extract: title, summary/TL;DR, key points, related links
3. Note the `updated` date to show freshness

### Step 4: Present Results
Format as glanceable summary with links and excerpts.

Do not write engagement counters to surfaced notes — staleness is derived
from `updated` (e.g. via Dataview), not stored.

## Error Handling

| Error | Response |
|-------|----------|
| No results | Offer to create a research item via /scout |
| Too many results | Show top 7, offer to narrow down |
| MCP and CLI unavailable | Fall back to Grep/Read tools |

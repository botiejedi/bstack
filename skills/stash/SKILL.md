---
name: stash
description: Push conversation content to vault — save insights, decisions, and context
triggers:
  - /stash
  - stash
  - save this
  - keep this
  - remember this
  - note this
  - add to vault
  - update the project brief
---

# /stash — Push Content to Vault

Saves content from the current conversation into the appropriate place in the vault.

## Vault layout (configurable)

Run from your Obsidian vault root. These are defaults — edit the table to
match your vault's folders and use your names everywhere below.

| Role | Default |
|------|---------|
| Inbox (new captures) | `Inbox/` |
| Notes (briefs, logs) | `Notes/` |
| Projects (one note per project) | `Projects/` |
| Sources (raw evidence dumps) | `Sources/` |
| Decisions | `Indexes/Decisions/` |
| Topic indexes | `Indexes/<Topic> Index.md` |

Templates ([[Capture Note]], [[Research Brief]], [[Decision]], [[Research Queue]]) are optional: if your vault lacks one,
write a plain note with `created`/`updated` dates and the listed tags.

## When to Use

- "Stash this insight"
- "Save this to my notes"
- "Remember this for the [project] brief"
- "Note this decision"

## Content Routing

| Content Type | Destination | Template |
|--------------|-------------|----------|
| New idea/insight | `Inbox/` | [[Capture Note]] |
| Research finding | `Notes/` (tag `topic/research`) | [[Research Brief]] |
| Decision made | `Indexes/Decisions/` | [[Decision]] |
| Action item | `Inbox/` with `topic/action` | [[Capture Note]] |
| Project update | Append to project note in `Projects/` | — |
| Research topic | `Inbox/` with `topic/research` | [[Capture Note]] |
| last30days report | `Notes/` brief, dump to `Sources/Last30Days/` | [[Research Brief]] + scout Step 3c |

## Step-by-Step Execution

### Step 1: Identify Content Type
Analyze what the user wants to save based on keywords and context.

### Step 2: Extract Content
If unspecified, look at last 2-3 exchanges and identify key insight.

### Step 3: Check for Existing Context
Search for related notes, project notes, and indices. MCP-first
(`obsidian_simple_search`), obsidian-cli fallback, Grep last resort.

### Step 4: Route and Save
Create new note or append to existing based on content type. Update the
`updated` date on any note touched.

### Step 5: Update Indices
Add links to the relevant `Indexes/<Topic> Index.md` if one exists;
research items also go on [[Research Queue]].

### Step 6: Confirm
Show what was saved, where, and what it's linked to.

Do not write engagement counters (`escalation_tier`, `last_engaged`) —
staleness is derived from `updated`, not stored.

## Error Handling

| Error | Response |
|-------|----------|
| Can't determine content | Ask for clarification |
| No project note exists | Offer to create one |
| Duplicate exists | Offer to append or create new |

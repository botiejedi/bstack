---
name: blurb
description: Classify and route thought dumps — parse unstructured braindumps into organized notes
triggers:
  - /blurb
  - blurb
  - brain dump
  - braindump
  - let me dump this
---

# /blurb — Braindump Processor

Parses unstructured streams of consciousness into classified, routed notes.

## Vault layout (configurable)

Run from your Obsidian vault root. These are defaults — edit the table to
match your vault's folders and use your names everywhere below.

| Role | Default |
|------|---------|
| Inbox (new captures) | `Inbox/` |
| Projects (one note per project) | `Projects/` |
| Topic indexes | `Indexes/<Topic> Index.md` |

Templates ([[Capture Note]]) are optional: if your vault lacks one,
write a plain note with `created`/`updated` dates and the listed tags.

## When to Use

- User sends long unstructured message with multiple topics
- "Let me just brain dump this..."
- Any message containing 3+ distinct thoughts

## Classification Routing

| Type | Indicators | Destination | Tags |
|------|------------|-------------|------|
| Action item | "need to", "should", "before [date]" | `Inbox/` | `topic/action` |
| Research question | "I wonder", "should look into" | `Inbox/` | `topic/research` |
| Idea | "what if", "thinking about" | `Inbox/` | `topic/idea` |
| Media to review | "sent me", "article about" | `Inbox/` | `topic/to-review` |
| Project context | References existing project | Append to project note in `Projects/` | existing |
| Person reference | Names someone | Tag the mention inline; do not create a People note (v1 decision) | — |
| Emotion/reflection | "feeling", "frustrated" | `Inbox/` | `topic/reflection` |

New captures use the [[Capture Note]] template.

## Step-by-Step Execution

### Step 1: Receive the Dump
Accept raw input without interruption.

### Step 2: Parse into Discrete Items
Split by topic shifts, conjunctions, different references.

### Step 3: Classify Each Item
Assign type and destination per routing table.

### Step 4: Convert Relative Dates
"end of month" → YYYY-MM-DD, "next week" → specific date

### Step 5: Check Existing Context
Search for related notes to append vs. create new. MCP-first
(`obsidian_simple_search`), obsidian-cli fallback, Grep last resort.

### Step 6: Create Notes
One note per classified item with proper template and tags.

### Step 7: Create Master Braindump Note
Single note in `Inbox/` with full dump and classification receipt.

### Step 8: Update Indices
Link new notes to the relevant `Indexes/<Topic> Index.md` if one exists.

### Step 9: Present Receipt
Show all created notes, actions, and connections.

## Error Handling

| Error | Response |
|-------|----------|
| Can't parse | Ask to break into separate thoughts |
| Unclear person | Ask for clarification |
| Ambiguous date | Confirm specific date |

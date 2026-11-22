---
name: clip
private: false
description: Snapshot conversations — save chat logs with summaries and connections
triggers:
  - /clip
  - clip this
  - clip it
  - log this
  - save this conversation
---

# /clip — Conversation Snapshots

Creates structured Chat Log notes from conversations.

## Vault layout (configurable)

Run from your Obsidian vault root. These are defaults — edit the table to
match your vault's folders and use your names everywhere below.

| Role | Default |
|------|---------|
| Inbox (new captures) | `Inbox/` |
| Notes (briefs, logs) | `Notes/` |
| Projects (one note per project) | `Projects/` |
| Topic indexes | `Indexes/<Topic> Index.md` |

Templates ([[Chat Log]]) are optional: if your vault lacks one,
write a plain note with `created`/`updated` dates and the listed tags.

## Two Modes

| Mode | Trigger | Output |
|------|---------|--------|
| Log Conversation | "clip this" | Chat Log in `Notes/` with TL;DR, decisions, actions |
| Search Past Chats | "what have I discussed about X?" | Timeline of related conversations |

## Step-by-Step: Log Conversation

### Step 1: Analyze Conversation
Extract: topics, decisions, action items, open questions, ideas, context.

### Step 2: Generate Title
"Chat Log - [Main Topic] - [Date]"

### Step 3: Find Related Notes
Search for previous chat logs, project notes, research briefs. MCP-first
(`obsidian_simple_search`), obsidian-cli fallback, Grep last resort.

### Step 4: Create Chat Log
Create `Notes/Chat Log - [Topic] - [Date].md` from the [[Chat Log]]
template (tag `topic/chat-log`), all sections filled:
- TL;DR
- Topics Covered
- Key Decisions
- Action Items
- Open Questions
- Ideas Generated
- Related Conversations
- Conversation Context

### Step 5: Update Project Note
If relates to an active project, append to its note in `Projects/`.

### Step 6: Update Indices
Link from the relevant `Indexes/<Topic> Index.md` if one exists.

### Step 7: Create Tasks
Ensure action items are captured as notes in `Inbox/` with `topic/action`.

### Step 8: Confirm
Show what was saved and all connections.

## Step-by-Step: Search Past Chats

1. Parse topic from query
2. Search `Notes/` for `topic/chat-log` tags
3. Search project note histories in `Projects/`
4. Build chronological timeline
5. Present with key decisions over time

## Error Handling

| Error | Response |
|-------|----------|
| Nothing significant | Ask if still want to clip |
| No previous chats | Note this is first on topic |
| Can't determine topic | Ask for title |

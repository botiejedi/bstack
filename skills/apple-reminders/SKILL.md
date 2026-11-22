---
name: apple-reminders
private: false
description: Create, read, complete and edit tasks in Apple Reminders through the apple-events MCP. Use whenever the user says "remind me", "set a reminder", "add a reminder", "add to my list/to-do", "what's on my list", "what do I have due", or mentions Reminders at all — "remind me" ALWAYS means an Apple Reminders entry, never a Claude scheduled task, cron job or /loop. Also use when a conversation surfaces a concrete follow-up the user owns (renew a key, check a result, reply to someone) and they agree to track it.
---

# Apple Reminders

Tools come from the `apple-events` MCP server (EventKit, local to this Mac):
`mcp__apple-events__reminders_tasks`, `mcp__apple-events__reminders_lists`,
`mcp__apple-events__reminders_subtasks`. If they aren't loaded, load them with
ToolSearch (`+apple-events reminders`). If the server isn't connected, say so —
do not fall back to a scheduled task.

## "Remind me" routing

| User says | Do |
|---|---|
| "remind me to X [when]" | Create an Apple reminder. |
| "remind me … in 20 minutes / at 5" | Apple reminder with a timed `dueDate`. Still not a cron job. |
| "check on X in an hour" / "run Y every morning" (Claude does the work) | That is an agent task → `schedule`/`loop`, not this skill. |

When unsure whether the user or Claude owns the follow-up, the user owns it → Reminders.

## Creating

1. Resolve the time to local wall-clock (`date` if you need "now"; use the Mac's
   local zone). Pass `dueDate` as `YYYY-MM-DD HH:mm:ss`, or
   `YYYY-MM-DD` for a day with no time. "Tomorrow" with no time → date only.
   "Tonight" → 19:00, "this morning/tomorrow morning" → 09:00, "end of day" → 17:00.
2. List: omit `targetList` (Reminders' default list) unless the user names a
   list or the item obviously belongs to an existing one. Run
   `reminders_lists` `read` once per session before picking a non-default list;
   never create a new list unless asked.
3. Title is the action in the user's words, short ("Renew API key").
   Put context in `note`: why, and where it came from (vault note path, repo,
   URL). Use `url` for a single link. Multi-step → `subtasks`.
4. Priority only when the user signals it ("urgent" → 1, "important" → 5).
5. Before creating, `read` with `search` for the same title to avoid duplicates.
6. Confirm in one line: `Reminder set: "<title>" — <due, human-readable> (<list>)`.

Don't ask permission for a clear "remind me" request — just create it. Ask only
when the time is genuinely ambiguous ("next week" for a timed thing, "later").

## Reading and completing

- "What's due / what's on my list": `read` with `dueWithin` (`today`, `tomorrow`,
  `this-week`, `overdue`) or `filterList`. Present ≤5 items first, grouped by
  due time; offer the rest.
- "Done with X" / "mark X complete": find it with `search`, then `update`
  `completed: true`. If several match, list them and ask which.
- Delete only when the user says delete/remove; completing is the default for
  "I did it".

## Limits

Alarms, recurrence and location triggers are read-only here. For "every
Monday" or "when I get home", create the reminder and tell the user to set the
repeat/location in Reminders.app. A timed `dueDate` normally produces the
Reminders notification; if the user reports no alert, point them to the
reminder's alert setting in the app.

Fallback CLI if the MCP is down and the user wants it done anyway: `remindctl`
(installed via Homebrew; needs Reminders permission for the terminal).

---
name: apple-calendar
description: Read and write Apple Calendar events through the apple-events MCP. Use when the user asks what's on their calendar or whether they're free, asks to schedule/add/move/cancel an event, or when the conversation surfaces a concrete dated commitment — a meeting, appointment, flight, deadline, launch, market close/settlement date, maintenance window, certificate/API-key/trial/subscription expiry, or a tool or project requirement with a hard date. In those cases add it to Calendar proactively (after a duplicate check) and say so in one line.
---

# Apple Calendar

Tools come from the `apple-events` MCP server (EventKit, local to this Mac):
`mcp__apple-events__calendar_events` and `mcp__apple-events__calendar_calendars`.
If they aren't loaded, load them with ToolSearch (`+apple-events calendar`).
If the server isn't connected, say so and give the event details for manual entry.

## When to add an event without being asked

Add it when **all three** hold:
1. It is concrete: a specific date (and time, if it has one) is known or
   stated in a source you just read — not "sometime next month".
2. The user owns or attends it: their meeting, their deadline, a date one of
   their tools/projects depends on (key rotation, cert or domain expiry, trial
   end, market close, scheduled maintenance, filing deadline, release date).
3. It isn't already there (see duplicate check).

If any is uncertain — hypothetical plans, someone else's schedule, a date
you inferred rather than read — offer in one line instead: `Add "<title>" on
<date> to your calendar?`

Deadlines and expiries are **all-day events** on the due date (`YYYY-MM-DD`).
If there's lead time to act (renewals, filings), also create an Apple reminder
a few days before via the `apple-reminders` skill, and say both in one line.

## Creating

1. Run `calendar_calendars` `read` once per session to learn calendar names.
   Omit `targetCalendar` (the default calendar) unless the user names one or a
   calendar clearly fits (a "Work" calendar for work meetings). Never guess at
   shared/family calendars — ask.
2. Times: local wall-clock `YYYY-MM-DD HH:mm:ss` (use the Mac's
   local zone — check with `date` if unsure). If the source gives another zone, pass that IANA name in `timezone`
   instead of converting by hand. No end time given → 1 hour for meetings,
   30 min for calls. All-day: `startDate` and `endDate` as `YYYY-MM-DD`.
3. Duplicate check: `read` the event's day with `search` on a distinctive word
   from the title. Existing match → update it (if details changed) or leave it.
4. Title: short and scannable ("Market close — CPI", "Cert expires —
   example.com"). `note`: why it matters, the source (vault note path, URL,
   email subject), and the line `Added by Claude` so agent-created events are
   findable later. `location` if there is one.
5. Confirm in one line: `Added to Calendar: "<title>" — <day, time> (<calendar>)`.

## Reading

- "What's on today/tomorrow/this week": `read` with `startDate`/`endDate`.
  Lead with the next event; list ≤5, then offer the rest.
- "Am I free at X": read that window and answer yes/no first, conflicts after.

## Changing and removing

- Move/rename: find by `search` + date window, then `update` by `id`. For a
  recurring event ask whether it's `this-event` or `future-events` (`span`).
- Delete only when the user asks. Confirm first if the event was not created
  by Claude (no `Added by Claude` in its note) or has other attendees.
- Events can't move between calendars via update — delete and recreate, and
  say so.

## Limits

Alarms, recurrence, URL and availability are read-only here; for "every
Tuesday" create the first instance and tell the user to set the repeat in
Calendar.app. No invitations/attendees can be sent — this is local-only.

---
name: ntfy
private: false
description: Use when the user asks to be notified, pinged, alerted or updated about something that finishes or changes later, in phrases such as "notify me", "let me know when", "update me when this changes", "ping me when it's done", "tell me if it fails", "send it to my phone", or "keep me posted". Also use when the user starts long work and says they are stepping away, and on /ntfy.
---

# ntfy

## Overview

Send a push notification to the user's phone through their own ntfy server, at
the moment the thing they asked about happens.

**Core principle:** a notification is a promise. "Let me know when X" is kept
only when a push is sent at X, or the user is told now, in chat, why it cannot
be. Saying "I'll let you know" and then only writing in chat breaks it: the
user asked because they will not be looking at the chat.

## Step 1: check this machine can send

```bash
test -r ~/.config/ntfy/claude.conf && echo ready || echo missing
```

- `ready`: continue.
- `missing`: say so now, in one line: push is not set up on this machine, so
  the update will arrive in chat only. Offer the setup in the last section.
  Carry on with the work.

The file holds the server URL, the topic and an access token. Never print it,
`cat` it, or copy its contents into a message, a note or a commit.

## Step 2: pick the shape

| The user wants | Do this |
|---|---|
| "Tell me when you're done" (work you are doing) | Do the work. Send one push when it ends: finished, failed, or blocked on a question only they can answer. If it has already ended, send now |
| "Let me know when X changes / is up / is merged" (something outside you) | Start a background watcher that sends the push itself (below) |
| A check that must outlive this session or run while the PC is off | Use a scheduled task or cloud routine whose prompt says to follow this skill, and say that is what you did |
| `/ntfy <text>` with nothing to wait for | Send `<text>` now |

State the limit when you start a watcher: it lives only as long as this
session and this computer stay on.

## Step 3: send

Use the Bash tool. The config file supplies the URL and the token, so neither
appears on the command line.

```bash
curl -sS --fail -m 20 -o /dev/null -K ~/.config/ntfy/claude.conf \
  -H "Title: Backup finished on nas" \
  -H "Priority: default" \
  -H "Tags: white_check_mark" \
  -d "restic run ended OK at 03:41 UTC, 2 new snapshots. Nothing needs you."
```

| Field | Rule |
|---|---|
| Title | What happened, 50 characters or fewer, readable on a lock screen. ASCII only |
| Body | 1 to 3 short lines, separated by real newlines: the outcome with real numbers or names, then the one thing the user should do next, or "Nothing needs you" |
| Priority | `default` for good news and plain updates. `high` when something failed or work is stopped waiting on the user. Nothing else |
| Tags | One of `white_check_mark` (done), `x` (failed), `raised_hand` (needs you), `eyes` (changed) |
| Click | Optional `-H "Click: <url>"` when one link is the obvious next step |

`curl` exits 0 on success. On any other exit code, tell the user in chat that
the push failed and give the code; do not retry more than once. Exit 22 means
the server refused it (bad or revoked token, or wrong topic); 6, 7 or 28 mean
the server could not be reached.

## Watching for a change

Run one background command (Bash tool with `run_in_background`) that polls,
then sends the push itself, so the push goes out even if nobody is reading the
session. Bound it so it cannot run forever.

```bash
# Poll every 60 s for up to 6 h. Push on change, or push that the watch ended.
end=$((SECONDS + 21600)); hit=0
while [ $SECONDS -lt $end ]; do
  if gh pr view 42 --json state -q .state | grep -q MERGED; then hit=1; break; fi
  sleep 60
done
if [ $hit = 1 ]; then
  curl -sS --fail -m 20 -o /dev/null -K ~/.config/ntfy/claude.conf -H "Title: PR 42 merged" \
    -H "Tags: eyes" -d "The PR merged. Nothing needs you."
else
  curl -sS --fail -m 20 -o /dev/null -K ~/.config/ntfy/claude.conf -H "Title: Stopped watching PR 42" \
    -H "Tags: raised_hand" -d "Not merged after 6 h. Ask me to watch again if you still want it."
fi
```

- The check must be read-only and cheap. Poll no faster than every 30 seconds.
- To watch "this" for any change, record the current value first, then compare.
- One push per event the user asked about. If the thing flaps, send the first
  change and stop.
- When the background command ends you are re-invoked: report the result in
  chat too.

## What goes in a push

A push shows on a lock screen and is stored on the server for 12 hours.

- Never include passwords, tokens, keys, one-time codes or credential paths.
- Summarise; do not paste logs, diffs or file contents.
- Send only what the user asked to hear about. Do not add pushes for routine
  progress.

## Common mistakes

| Mistake | Instead |
|---|---|
| Promising a push, then ending the turn with only a chat message | Send the push before the closing message |
| Putting the URL or token on the command line or in a script file | Always `-K ~/.config/ntfy/claude.conf` |
| A watcher with no end | Give it a deadline and push when it gives up |
| `Priority: urgent` or `max` to be safe | `high` at most; urgent overrides Do Not Disturb |
| Sending from PowerShell with backtick continuations | Use the Bash tool |

## Setting up another machine

Each machine gets its own token, so one can be revoked alone. This needs shell
access to the server that runs ntfy. On the server, in the ntfy container:

```bash
ntfy token add --label=<machine>-claude-skill claude
```

Then on the new machine create `~/.config/ntfy/claude.conf`, readable only by
the user, with two lines: `url = "<server>/<topic>"` and
`header = "Authorization: Bearer <token>"`. Pipe the token straight into the
file; do not show it in the conversation. The `claude` account can publish to
its one topic and cannot read anything.

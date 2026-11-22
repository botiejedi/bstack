---
name: rule
description: Router for toggleable Claude Code state. Invoked via /rule <subcommand> [args]. Subcommands: help, status, list, delegate. The delegate subcommand toggles I/O delegation to a cheap worker model and manages which worker is active. Use when the user types /rule, asks to enable/disable delegation, or wants to switch worker models.
---

# /rule

Router skill for toggleable state. Parse the first arg as the subcommand and dispatch.

If no subcommand is given, run `help`.

State file: `~/.claude/state/rule.json`. Read on every invocation; write only on state-changing subcommands.

## Subcommands

### help
Print this subcommand list with one-line descriptions.

### status
Read `~/.claude/state/rule.json` and pretty-print the current state of every rule. Default output:
```
delegate.active = <bool>
delegate.model  = <alias>
```

### list
Same as `status`. Alias for discoverability.

### delegate <action> [args]
Sub-router for delegation. Actions:

#### delegate on
Set `delegate.active = true` in the state file. Confirm: `delegate.active = true (model: <alias>)`.
Then announce to the user: "Delegation is on. I will now route bulk reading and boilerplate generation to the worker model. Type `/rule delegate off` to disable."

#### delegate off
Set `delegate.active = false`. Confirm: `delegate.active = false`. Stop using `delegate-ask` etc. for the rest of the session.

#### delegate status
Print: `delegate.active = <bool>, delegate.model = <alias>`.

#### delegate model <alias>
Switch the active worker. Three cases:

1. **Alias is in `~/.claude/config/delegate-models.yaml`** AND its provider's `api_key_env` is set:
   - Update `delegate.model` in state.
   - Confirm: `delegate.model = <alias>`.

2. **Alias is in models.yaml** but env var is missing:
   - Read the provider's `api_key_env` from `~/.claude/config/delegate-providers.yaml`.
   - Print: "Model `<alias>` requires `<ENV_VAR>` to be set. Get a key at <signup_url>."
   - Ask the user to paste the key in chat.
   - Once received, instruct the user to run (in PowerShell):
     ```powershell
     [Environment]::SetEnvironmentVariable("<ENV_VAR>", "<KEY>", "User"); $env:<ENV_VAR>="<KEY>"
     ```
   - Tell them to restart Claude Code for the var to take effect.

3. **Alias is NOT in models.yaml**: run the **registration wizard** (see below).

#### delegate models
List all registered model aliases from `~/.claude/config/delegate-models.yaml`. Mark the active one.

## Registration Wizard (when delegate model <new>)

Walk the user through these steps in order, asking one question at a time:

1. **Provider:** Read `~/.claude/config/delegate-providers.yaml` and show the available providers. Ask which one (offer `custom` for unknown).
2. **Defaults:** Look up the provider preset. Show the suggested `base_url`, env var name, and `suggested_models`. Ask if they want to override anything.
3. **Model ID:** Confirm the `model_id` (default = first in `suggested_models`).
4. **API key:** Check if `api_key_env` is set. If not, print signup URL and the PowerShell command to set it. Wait for confirmation.
5. **Test call:** Make a small test call (one short message, max_tokens=10) to verify the key + model work. If it fails, print the error and ask if they want to retry.
6. **Append to YAML:** Add the new model to `~/.claude/config/delegate-models.yaml` under `models:`. Preserve existing entries.
7. **Activate:** Ask if they want to set this as the active model now (default: yes).

Record the new alias and confirm.

## Output Conventions

- State change: one-line confirmation `<key> = <value>`
- Status: key-value list, one per line
- Help: bulleted subcommand list
- Errors: `rule error: <message>` + suggested fix

## Unknown Subcommand

```
rule error: unknown subcommand "<arg>"
Try: /rule help
```

## When Delegation Is On — Routing Rules for Claude

These rules apply only when `delegate.active = true`. If false, ignore this section.

**Use `delegate-ask` when:**
- Reading 3+ files just to answer a single question
- Reading any file >400 lines
- Searching across many files for a fact (after grep narrows it down)

**Don't delegate:**
- Tasks under ~2000 tokens of source — overhead isn't worth it
- Architectural decisions, debugging, safety-critical code
- Anything requiring careful reasoning about cause/effect
- When you need exact line numbers for editing

**How to invoke:**
```bash
delegate-ask --paths file1 file2 file3 --question "your question"
```
The output is a structured summary. Use that instead of reading the files yourself.

**Boundary phrase:** Claude does the thinking. The worker does the I/O.


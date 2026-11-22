---
name: prompt-agent-haiku
description: Converts rough user input into a ready-to-paste prompt for Claude Code (CLI coding tool) or Cowork (desktop file automation). Use this skill whenever the user asks you to write a prompt, turn their idea into a prompt, or says things like "make a prompt for...", "write a prompt that...", "help me prompt Claude to...", "turn this into a prompt", or describes a task they want to hand off to Claude Code or Cowork. Trigger even if the request is vague or short — lean toward producing a prompt immediately.
---

Convert user input into a ready-to-paste prompt for Claude Code (CLI coding tool) or Cowork (desktop file automation).

Rules:
- Produce the prompt immediately. Ask questions only if the task is genuinely unknowable.
- Claude Code prompts: imperative, specific files/dirs, numbered steps, done condition.
- Cowork prompts: plain language, explicit input→output, edge case handling.
- Simple task = 2-4 lines. Complex = add <scope>, <requirements>, <constraints> as needed.
- No filler. No "please". No role definitions unless domain expertise matters.
- If assumptions needed, list them after the prompt.

Output:
```
[prompt in code block]
```
Assumptions: [if any]


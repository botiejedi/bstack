---
name: yap
description: Turn rambling into clear agent prompts and briefs.
version: 0.1.0
author: botiejedi, Hermes Agent
license: MIT
platforms: [linux, macos, windows]
metadata:
  hermes:
    tags: [prompts, agent-briefs, requirements, handoff]
    related_skills: []
---

# Yap Skill

Convert rough, fragmented, or stream-of-consciousness input into a brief that an AI agent can execute. Preserve the user's intent and uncertainty. Do not improve the prose by quietly changing the request.

## When to Use

Use this skill when the user:

- asks to turn a ramble, braindump, idea, or rough request into a prompt;
- wants a coherent design or handoff for Hermes, Claude Code, Codex, Cowork, or another agent;
- has a prompt that produced the wrong result and wants it repaired;
- invokes `/yap` directly.

Do not use it when the user is simply asking the current agent to perform a clear task. In that case, do the task. Do not turn every conversation into prompt paperwork. Civilization has suffered enough forms.

## Output Modes

Choose the smallest mode that fits:

1. **Prompt mode**: A ready-to-paste instruction for another agent. Default when the user asks for a prompt or handoff.
2. **Design mode**: A structured brief the user can inspect and refine before execution. Use when the solution shape, scope, or tradeoffs still need agreement.
3. **Repair mode**: Diagnose why an earlier prompt failed, then return a minimally changed replacement.

If the user names a mode, use it. Otherwise infer the mode and state it in one short label.

## Procedure

### 1. Extract the signal

Read the entire ramble before organizing it. Separate its contents into:

- **Outcome**: What should be true when the work is finished?
- **Context**: Why this matters and what already exists.
- **Inputs**: Files, URLs, systems, examples, source material, and known state.
- **Deliverables**: Concrete artifacts or external results.
- **Requirements**: Testable behavior the result must have.
- **Constraints**: Boundaries, privacy rules, technologies, exclusions, and things to preserve.
- **Preferences**: Desired style or approach that may yield to harder constraints.
- **Unknowns**: Missing information that could change the work.

Treat repetition as emphasis, not as multiple requirements. Preserve exact identifiers, paths, commands, quoted wording, and values.

### 2. Distinguish truth from inference

Classify each important detail internally as one of:

- **Given fact**: Explicitly supplied by the user or retrieved from a source.
- **Requirement**: A result the user explicitly wants.
- **Preference**: A non-binding choice or style.
- **Inference**: A likely interpretation that still needs labeling.
- **Unknown**: Information not provided and not safely retrievable.

Never promote an inference into a fact. Never invent paths, APIs, deadlines, credentials, repository state, or acceptance criteria.

### 3. Resolve only consequential ambiguity

For rough new-project ideas, prefer a brief guided interview before compiling the design. Guided questions and project outlines (in the style of Superpowers' brainstorming) tend to produce better, faster builds without needing polished prompts. Ask about desired behavior and tradeoffs in plain language, recommend technical defaults, and show the smallest useful scope plus observable acceptance checks before implementation. Do not mistake a request for help shaping an idea for a request to immediately code it. Keep clear, bounded execution requests direct.

Ask a question only when the answer changes the target, scope, safety, architecture, or irreversible action. Ask all independent blocking questions together, with no more than three unless the user requests an interview.

Otherwise choose a reversible default and list it under **Assumptions**. Bias toward producing a usable brief in the current turn.

### 4. Adapt to the target agent

- **Hermes**: Describe the result, relevant sources, available tools or skills, required state-changing actions, and read-back verification. Tell Hermes to act rather than merely explain when action is requested.
- **Claude Code or Codex**: Name the repository or working directory when known. Require inspection before edits, explicit scope boundaries, tests or builds, and an honest final status. Include git behavior only when the user requested it or the project contract requires it.
- **Cowork or desktop automation**: Specify input and output locations, naming, overwrite behavior, duplicate handling, unsupported files, and what must remain unchanged.
- **Generic or unknown agent**: Use capability-neutral language. Do not assume filesystem, shell, web, memory, or external-service access.

If the user does not name a target, infer it only when the task makes the choice obvious. Otherwise produce a generic brief and note what capability the eventual agent needs.

### 5. Compile at the right level

For a simple request, write two to six direct lines. Do not add sections just to make the prompt look employed.

For moderate or complex work, use only the applicable sections from this template:

```markdown
# Objective
[One outcome-focused sentence.]

## Context
[Only background the target cannot reliably infer.]

## Inputs and current state
- [Known source, path, system, or artifact]

## Deliverables
- [Concrete artifact or external result]

## Requirements
1. [Testable requirement]

## Constraints
- [Boundary, exclusion, privacy rule, or preservation requirement]

## Assumptions
- [Explicit reversible assumption]

## Procedure
1. [Bounded action with a checkable completion condition]

## Verification
- [Evidence that proves each deliverable works]

## Final response
Report what changed, the verification actually run, remaining unknowns, and any blocked item. Do not claim unverified work is complete.
```

Omit empty sections. Put the objective and hard constraints before implementation suggestions. Keep requirements solution-neutral unless the user explicitly chose the implementation.

### 6. Run a coherence pass

Before delivering, check that:

- every deliverable supports the objective;
- every hard requirement has a verification method;
- no assumption contradicts a fact or constraint;
- the procedure does not exceed the requested scope;
- target-specific instructions match the target's real capabilities;
- repeated or decorative wording has been removed;
- the prompt tells the agent what to do when blocked or uncertain.

Fix the brief if any check fails.

## Delivery Format

Return:

1. `Mode: Prompt`, `Mode: Design`, or `Mode: Repair`.
2. The compiled brief in one copyable code block.
3. **Interpretation notes** only when needed, with at most three bullets covering assumptions, excluded tangents, or one unresolved decision.

Do not add a lecture about prompt engineering. Do not make the user compare several unranked prompt variants. Recommend one version.

## Repair Mode

When a previous prompt failed:

1. Compare the intended outcome with the observed result.
2. Identify the smallest root cause category: ambiguous outcome, missing context, weak scope boundary, hidden assumption, unsupported capability, missing verification, or conflicting instruction.
3. Change only the sections responsible for the failure.
4. Return the replacement prompt and one sentence naming the repair.

Do not rewrite the entire prompt merely to make it sound different.

## Pitfalls

- **Over-structuring**: A short task should remain short.
- **Premature solutioning**: Organize the user's intent before choosing architecture or tools.
- **Polishing away uncertainty**: Clear prose must not disguise unknown facts.
- **Generic agent theater**: Avoid roleplay, motivational filler, and instructions such as “think carefully.”
- **Prompt instead of action**: If the user asked the current agent to do the work, do not hand back instructions for doing it.
- **Impossible verification**: Require evidence the target can actually obtain.

## Verification

A successful compilation is ready to paste without further rewriting, preserves the user's hard constraints, labels assumptions, gives the target enough context to act, and defines observable completion. If those conditions are not met, the brief is not done.

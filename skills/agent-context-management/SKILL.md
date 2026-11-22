---
name: agent-context-management
private: false
description: "Use when managing long LLM context windows in agents."
version: 0.1.0
author: botiejedi, Hermes Agent
license: MIT
platforms: [linux, macos, windows]
metadata:
  hermes:
    tags: [context, compression, compaction, retrieval, prompt-cache, agents]
    related_skills: [adaptive-model-routing, software-alternative-vetting]
---

# Agent Context Management

Manage context pressure as a runtime policy, not as a larger system prompt. Start with the host's built-in compressor, measure what actually fills the window, and add a replacement context engine only when a measured recall or latency problem remains. Preserve exact requirements outside the transcript because every lossy summary can omit something important.

## When to Use

- A long Hermes, Claude Code, Codex, or similar agent session is approaching its context limit.
- The user asks how `/compress`, `/compact`, automatic compaction, memory, or context-engine plugins differ.
- The user wants model-specific context thresholds or dynamic context selection.
- A session loses requirements, paths, error strings, corrections, or tool results after compaction.
- You are deciding between config, a prompt rule, tool-result pruning, provider-native compaction, or a plugin.

Do not use this skill to choose a single static model with no context-management problem. Use the model-routing workflow instead.

## Standing Rules

- Inspect the active provider, route, model, context window, and effective threshold before changing policy. A configured ratio is not necessarily the runtime trigger because providers and small-window floors can override it.
- Keep dynamic context management out of the main system prompt. Static prompt text consumes every request, cannot delete history, and prompt mutation damages cache stability.
- Keep exact requirements, rejected substitutes, acceptance criteria, current blockers, and evidence paths in `REQUIREMENTS.md` and `HANDOFF.md`, not only in a summary.
- Prefer the built-in compressor and deterministic tool-result pruning before installing or writing a context engine.
- Treat a separate auxiliary compression model as a data-transfer decision. Verify its provider, privacy boundary, context capacity, latency, and fallback path.
- Do not enable micro-compaction or provider-native compaction globally without measuring cache impact and route compatibility.
- Trial replacement context engines in a separate profile. Promote one to the default profile only after explicit user approval, an immutable source revision, a rollback copy, dependency validation, config read-back, plugin diagnostics, and a fresh-process smoke test.
- Only one context engine can be active, so a plugin replaces rather than layers on top of the built-in compressor.
- Preserve the user's stable tail and recent actionable instructions. Raise `min_tail_user_messages` when losing recent user requirements is more costly than retaining a little extra context.

## Quick Reference

Use the Hermes `terminal` tool for CLI reads and writes:

```text
hermes config get model
hermes config get compression
hermes config get auxiliary
hermes config get context
hermes config set compression.proactive_prune_tokens 48000
hermes config set compression.min_tail_user_messages 3
```

In a live session:

```text
/context all
/compress --preview
/compress here 4
/compress focus <topic>
```

## Procedure

### 1. Measure the actual pressure

Run `/context all` before changing anything. Record the shares occupied by the system prompt, tool schemas, skills, MCP definitions, memory, subagents, and conversation. Read the effective `model`, `compression`, `auxiliary`, and `context` settings with `terminal`.

Completion criterion: the dominant context category and current compression state are identified.

### 2. Resolve the real model window

Determine the model and provider route that will serve the next request. Check live model metadata or the provider's model listing instead of trusting a stale transcript or a manually typed context length. Recalculate after every model or route switch.

Check for provider-native compaction eligibility, route-specific hard caps, Hermes-side wide-window aliases, auxiliary-model feasibility limits, and small-context threshold floors. Never fake a larger window by setting an arbitrary `model.context_length`.

Completion criterion: the route, model, context length, effective threshold tokens, and compaction owner are known.

### 3. Baseline the built-in engine

Keep the built-in compressor enabled with `tail_mode: lean` and `in_place: true` unless a measured requirement contradicts them. Use `/compress --preview` to inspect a manual boundary, then use `/compress here N` or `/compress focus <topic>` at a meaningful task boundary.

If tool results dominate, enable deterministic proactive pruning first. Start with a conservative token trigger such as `48000`, keep the default minimum reclaim gate, and preserve at least three recent real user messages when recent instructions matter.

Read the config back after every change. Start a fresh session or use the documented reload boundary before assuming a changed policy is active.

Completion criterion: one controlled session demonstrates the chosen threshold, tail policy, and pruning behavior.

### 4. Externalize durable state

Create or maintain a short `REQUIREMENTS.md` with exact non-negotiables and a `HANDOFF.md` with current state, completed work, blockers, tests, and next action. Tell the agent to reread them after compaction or resume. Keep large logs, file contents, and research results on disk and reference their paths rather than repeating them in chat.

Completion criterion: a fresh session can continue the task from the two files without reconstructing the entire transcript.

### 5. Add stricter caps only where they belong

Use an absolute `compression.threshold_tokens` cap when a particular model needs earlier compaction than its ratio or small-window floor allows. Put that cap in a dedicated model/profile policy if the user switches between small and large windows. Do not apply a cap sized for a small-window model to a 900K or 1M default model.

Completion criterion: each supported model has an intentional absolute trigger, or the global ratio is explicitly accepted for all routes.

### 6. Test micro and native compaction separately

Test micro-compaction only when the user needs occupancy kept flat or wants to amortize a long batch stall. Measure auxiliary latency, tokens, prompt-cache reuse, and net context occupancy. Remember that each committed micro pass rewrites already-sent history.

Test provider-native compaction only after verifying model, endpoint, API mode, and fallback behavior. Treat opaque provider checkpoints as a different compaction authority from Hermes' human-readable summary pipeline.

Completion criterion: the feature improves the selected metric without unacceptable cache loss, latency, or route failures.

### 7. Evaluate a replacement context engine

Install a candidate only in an isolated profile. Compare it with the built-in engine using the same controlled transcript and model route. Test:

- exact requirement retention;
- user corrections and rejected alternatives;
- file paths, SHAs, error strings, and test results;
- retrieval after two or more compactions;
- tool-result and message-pair validity;
- latency and auxiliary calls;
- prompt-cache behavior;
- tool-schema and prompt overhead;
- local storage, redaction, backup, and deletion;
- model-switch and session-resume behavior.

Adopt a plugin only when it wins on a stated metric and its recovery path is simpler than the built-in path.

Completion criterion: a written comparison shows why the plugin is better for this workload, not merely that it can compact.

### 8. Activate an approved Hermes context engine

For a user-approved Hermes-LCM rollout, use the plugin's source installer rather than pip. Pin a reviewed tag or immutable commit, keep the checkout in the profile's supported plugin path, and expose the bundled skill through the install script. The manifest name is `hermes-lcm`; the runtime engine name is `lcm`.

Configure with Hermes' CLI, never by hand-editing `config.yaml`, and preserve every existing enabled plugin when adding the new name:

```text
hermes config set plugins.enabled '[existing-plugin-1, existing-plugin-2, hermes-lcm]'
hermes config set context.engine lcm
hermes config set --force lcm.context_threshold 0.35
hermes config set compression.proactive_prune_tokens 48000
hermes config set compression.min_tail_user_messages 3
```

Read back every value. Then start a fresh Hermes process and verify the plugin list, context-engine selection, plugin diagnostics, and one minimal real request. Check the context-engine database integrity after the smoke test. If the current Desktop or gateway process is not restarted, say explicitly that it still owns the old in-memory engine and do not claim the active session uses the new one.

Completion criterion: a fresh process reports the selected engine, the smoke request succeeds, the database passes integrity checks, and the rollback path is documented.

## Pitfalls

- Do not equate `/compress`, Claude `/compact`, ChatGPT memory, and provider-native compaction. They may all reduce pressure, but they have different owners, visibility, retained state, and billing behavior.
- Do not lower a configured ratio and assume the trigger moved lower. A host may apply a raise-only floor or a route-specific override. Inspect the effective threshold.
- Do not make a global absolute cap while switching between models with materially different windows. A cap that protects a small-window model can make a 900K model compact wastefully early.
- Do not add a prompt instruction such as “compress more often” and call the context problem solved. The model cannot reliably enforce a runtime token policy from prose alone.
- Do not enable micro-compaction merely because it is more dynamic. Frequent history rewrites can cost more prompt-cache reuse than they save in stalls.
- Do not enable native compaction solely because a model name contains a familiar vendor string. Verify the exact endpoint and API mode.
- Do not send the full transcript to a cheaper auxiliary model without checking its context window. A summary request that cannot fit is not a safe fallback.
- Do not install an uncurated context engine into the default profile. Replacement engines add storage, retrieval tools, migrations, and another failure surface.
- Do not treat a summary as proof of exact historical state. Use the durable handoff, local session search, or bounded retrieval to verify details.

## Verification

Before finalizing a context-policy change:

- Read back every changed config value.
- Confirm the plugin name and selected context engine in a fresh process when a replacement engine is involved.
- Run `/context all` before and after a representative task.
- Force or wait for one compaction and test recall of exact requirements, corrections, paths, errors, and next steps.
- Confirm the active model, provider route, context length, effective threshold, and compression count in status or logs.
- Check that the session still resumes, tool-call pairs remain valid, and no secret values entered a summary or auxiliary endpoint.
- Compare the result against `REQUIREMENTS.md` before claiming the task survived compaction.

For Hermes compression internals and current route-specific behavior, read `references/hermes-compression.md`. For provider comparisons and plugin selection, read `references/provider-comparison.md` and `references/plugin-evaluation.md` as needed.

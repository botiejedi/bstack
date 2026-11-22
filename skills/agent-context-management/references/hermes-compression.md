# Hermes Compression Reference

## Built-in pipeline

Hermes has two relevant layers:

- Gateway session hygiene is a rough pre-agent safety net for oversized sessions.
- The agent `ContextCompressor` is the normal in-loop owner. It uses provider usage anchors when available and bounded heuristic fallbacks otherwise.

The built-in compressor generally:

1. removes or replaces older bulky tool results outside the protected tail;
2. protects the system prompt, configured head, recent tail, and complete tool-call groups;
3. summarizes the middle with the auxiliary compression route;
4. inserts a structured summary and sanitizes orphaned tool-call/result pairs;
5. updates the previous summary on later passes;
6. soft-archives replaced rows when using in-place compaction.

`tail_mode: lean` keeps a small bounded tail and puts continuity into the summary through a session log, mechanically extracted anchors, bounded verbatim user messages, and recovery pointers. `tail_mode: legacy` keeps a larger token-ratio tail. Use lean for large windows unless a task needs more recent verbatim material.

## Settings to inspect

```text
hermes config get compression
hermes config get auxiliary
hermes config get context
hermes config get model
```

Important controls include:

- `compression.enabled`
- `compression.threshold`
- `compression.threshold_tokens`
- `compression.model_thresholds`
- `compression.tail_mode`
- `compression.protect_last_n`
- `compression.min_tail_user_messages`
- `compression.proactive_prune_tokens`
- `compression.proactive_prune_min_reclaim_tokens`
- `compression.micro_compact`
- `compression.codex_responses_native`
- `compression.in_place`
- `auxiliary.compression.provider`
- `auxiliary.compression.model`

The threshold is a preflight trigger, not a strict ceiling. A long tool result or generated response can still push a request above it. Use an earlier absolute cap when the route has little overflow headroom.

## Small-window and Codex route checks

Do not infer a model's usable context from the model slug alone. Check the active `openai-codex` route, live account model list, and Hermes model metadata.

At the currently observed Hermes route, a base small-window model may be treated as a smaller Codex OAuth window and Hermes applies a raise-only small-context floor. A Hermes-side wide-window (`-900k`-style) variant is handled differently. Recheck the installed source and live model picker before copying those values into a new profile, because provider limits and aliases can change.

A route may expose provider-native compaction for one model family but not another. Confirm `api_mode`, endpoint, and native capability before setting `codex_responses_native: true`. Keep Hermes' local compressor available as the fallback owner unless the native path has been tested for the exact route.

## Manual compaction

Use:

```text
/compress --preview
/compress here 4
/compress focus <topic>
```

Use `here N` when recent turns must remain exact. Use `focus` when one project or decision must dominate the summary. Use a handoff file when exact requirements must survive more than one compaction.

## Proactive pruning

Use proactive pruning when old tool results, not conversation intent, dominate `/context all`. It is deterministic and does not require an auxiliary model. Keep a meaningful reclaim threshold so history is rewritten in episodic batches rather than on every small result.

A practical first test is:

```text
hermes config set compression.proactive_prune_tokens 48000
hermes config set compression.min_tail_user_messages 3
```

Read the values back and compare context occupancy before adopting them permanently.

## Micro-compaction

Micro-compaction absorbs one old assistant/tool exchange after completed turns into a rolling summary. It can keep occupancy flatter and amortize a long pause, but every committed pass rewrites already-sent history and can invalidate the provider prompt-cache prefix. Keep it off until a measurement shows that the reduced stalls justify the repeated cache breaks.

## Privacy and auxiliary routes

The compression model receives the material selected for summarization. If it is not the main local or trusted route, treat compression as an outbound data transfer. Confirm redaction, provider retention, context capacity, timeout, fallback, and cost before pinning the route.

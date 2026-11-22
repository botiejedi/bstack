# Provider and Plugin Comparison

## Compaction ownership

| Mechanism | Owner | Summary visibility | Typical control |
|---|---|---|---|
| Hermes built-in compression | Hermes client plus auxiliary route | Structured text and local session records | Thresholds, tail policy, focus, `here N`, auxiliary model |
| Claude Code `/compact` | Claude Code client or Anthropic compaction path, depending on surface | Usually a continuation summary or compaction block | Manual command, automatic compaction window, custom instructions in the API |
| OpenAI Responses compaction | OpenAI server | Opaque compaction item | Server threshold or standalone compact endpoint |
| ChatGPT memory/project features | Product memory layer | User-facing memory controls vary | Memory and project settings, not live transcript compaction |

Do not use memory features as a substitute for reducing the active prompt. Do not compare a visible Hermes summary with an opaque provider checkpoint as if they were the same artifact.

## Decision table

| Observed problem | First intervention | Escalate when |
|---|---|---|
| Old terminal/file/web output dominates | Hermes proactive pruning | A single result still floods the request before pruning, then test Toolaria-like externalization |
| Long batch stall at threshold | Smaller, fast non-reasoning auxiliary model or measured micro-compaction | Stall remains unacceptable and native route is compatible |
| Exact requirements disappear | `REQUIREMENTS.md`, `HANDOFF.md`, higher recent-user retention, focused manual compression | Repeated recall failures justify a retrieval-based context engine |
| Static prompt/tools dominate | Reduce always-loaded skills, tools, MCP schemas, and context files | A selection engine can choose request-specific context without changing stable defaults |
| Model route has a smaller hard limit | Dedicated profile and absolute threshold cap | A context engine is needed only if model-specific selection must be automatic |
| Provider-native checkpoint is available | Test it in the exact API mode and endpoint | Use it only after verifying fallback, replay, and opaque-state behavior |

## Replacement context engines

A context-engine plugin replaces the built-in compressor. Evaluate it as a runtime subsystem, not as a drop-in summarizer. Require:

- bounded active context;
- durable raw-message storage;
- source-linked summaries;
- bounded retrieval and expansion tools;
- session and profile isolation;
- backup, delete, and retention controls;
- redaction or clear sensitive-data behavior;
- model-switch and resume handling;
- tests for tool-call/result pairing and role alternation.

Known candidate shapes:

- **DAG retrieval engines such as `hermes-lcm`**: promising when flat summaries lose exact history. Compare retrieval quality, tool overhead, storage, and autonomous recall. Treat release-candidate or non-curated status as a review gate. A default-profile rollout is reasonable only after explicit approval, an immutable revision, rollback preparation, dependency validation, plugin diagnostics, and a fresh-process smoke test.
- **Tool-result externalizers such as Toolaria**: useful when oversized MCP or web payloads are the main problem. They complement a compressor conceptually, but may add local blob storage, handles, retention, and security policy.
- **Instruction rehydration tools such as MemLock**: useful for standing-instruction drift after compaction, not for reducing context occupancy. Review model-callable pinning, prompt-injection handling, and concurrent-session behavior.
- **Vision archive engines such as Snapcompact**: useful only when every active model can read the generated frames and lossy recovery is acceptable. Treat vision dependencies and exact-detail loss as hard constraints.

## Hermes-LCM activation recipe

Use the plugin's source installer and host-owned Hermes environment. Do not create a second pip-managed runtime for the plugin.

1. Clone a reviewed tag or immutable commit into `$HERMES_HOME/plugins/hermes-lcm`, or run the checkout's `scripts/install.sh` when using a separate source directory. For a named profile, set `HERMES_PROFILE` before running the installer.
2. Preserve a config and state rollback copy before enabling it. Treat the plugin's release-candidate status as a review gate, not as proof of stability.
3. Run the plugin's dependency-contract validator and compile/import smoke checks. Distinguish those checks from the optional unit-test suite.
4. Enable both names with `hermes config set`: add the manifest name `hermes-lcm` to the existing `plugins.enabled` list and set `context.engine` to `lcm`. Set plugin-owned YAML values such as `lcm.context_threshold` with `--force` only when the installed plugin documents that key.
5. Enable deterministic Hermes pruning alongside LCM when tool results dominate: start with `compression.proactive_prune_tokens 48000` and `compression.min_tail_user_messages 3`.
6. Read every changed value back, then launch a fresh process. Verify `hermes plugins`, the selected context engine, `hermes-lcm` diagnostics, one minimal real request, and `PRAGMA integrity_check` on the LCM database.
7. If a live Desktop or gateway process was not restarted, report that its in-memory engine is unchanged. Do not claim the newly configured engine is active in that existing session.

## Evaluation recipe

Use one representative transcript and two fresh profiles:

1. Run the built-in compressor through at least two compactions.
2. Record exact-recall checks for requirements, corrections, paths, errors, tests, and current state.
3. Record `/context all`, latency, auxiliary calls, prompt-cache indicators, and storage growth.
4. Run the same transcript through the candidate engine.
5. Test resume, model switch, tool retrieval, deletion, and a prompt-injection-shaped historical message.
6. Adopt only if the candidate improves the user's chosen metric without weakening privacy, recovery, or operational simplicity.

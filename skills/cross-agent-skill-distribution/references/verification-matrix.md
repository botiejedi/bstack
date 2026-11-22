# Cross-Agent Verification Matrix

Use this reference after the canonical skill and every intended mirror have passed static checks. Replace `<skill>`, `<project>`, and the sample input with real values. Keep smoke tests read-only and small.

## Static checks for every mirror

1. Read each `SKILL.md` with `read_file`.
2. Parse frontmatter and confirm the same `name`, `version`, description, platforms, and body.
3. Compare checksums with `execute_code` or `terminal`.
4. Confirm every linked `references/`, `templates/`, and `scripts/` path exists.
5. Search portable files for machine-local paths, secrets, and stale target names.

A matching checksum is evidence of identity, not proof that the target loader will discover the file.

## Hermes

Discovery check:

```text
terminal(command="hermes skills list --source local --enabled-only")
```

Behavior check from a fresh process:

```text
terminal(command="hermes chat -q 'Use <skill> on this read-only sample: [small sample]. Return only the distinctive output required by the skill.'")
```

Pass when the process identifies or visibly loads the skill and follows a rule that is distinctive to it. If the current chat does not see a newly written skill, treat that as a startup-cache boundary and use a fresh process rather than editing the skill again.

## Codex

Run from the intended project with the least-privilege sandbox available:

```text
terminal(command="codex exec --sandbox read-only -C '<project>' 'Use <skill> on this read-only sample: [small sample]. Return only the distinctive output required by the skill.'")
```

Pass when Codex reads the intended project-local skill or otherwise demonstrates the skill's distinctive behavior. A command that merely starts Codex is not a smoke test.

## Claude Code, Cowork, and other runtimes

Use the runtime's native fresh-session entry point and the project or user scope where the skill is installed. Ask it to apply the skill to a small read-only sample whose expected structure is obvious. Record:

- how the runtime discovered the skill;
- the observed distinctive behavior;
- whether trust, enablement, or restart was required;
- any target capability the skill correctly avoided assuming.

Do not invent a CLI command for a runtime whose current invocation syntax has not been checked. A native UI session is valid evidence when it is fresh and observable.

## Evidence record

```markdown
### <runtime>
- Scope/path:
- Ownership:
- Discovery evidence:
- Behavior evidence:
- Fresh process/session: yes/no
- Read-only: yes/no
- Warnings:
- Result: verified / unverified / blocked
```

## Failure interpretation

- **Not listed**: investigate path, trust, enablement, and startup timing.
- **Listed but behavior wrong**: inspect the loaded content and target context; do not assume the loader used the newest mirror.
- **Non-blocking warning**: record it separately from the skill result. Do not turn a transient setup warning into a permanent capability restriction.
- **No working method**: mark the runtime unverified. Do not report a guessed command as a successful workflow.

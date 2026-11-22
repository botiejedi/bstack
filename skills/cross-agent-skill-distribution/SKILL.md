---
name: cross-agent-skill-distribution
description: Publish and verify one skill across agent runtimes.
version: 0.1.0
author: botiejedi, Hermes Agent
license: MIT
platforms: [linux, macos, windows]
metadata:
  hermes:
    tags: [skills, cross-agent, distribution, verification]
    related_skills: []
---

# Cross-Agent Skill Distribution

Use this skill when one reusable skill must be available to multiple agent runtimes, such as Hermes, Claude Code, Codex, Cowork, or a project-local loader. It governs source-of-truth selection, target-specific installation, mirror consistency, and fresh-process verification. It does not replace a runtime's skill-authoring rules or silently modify protected skills.

## When to Use

Use this skill when:

- a skill should work across two or more agents or projects;
- a project needs both a portable skill copy and a user-local Hermes copy;
- a skill was installed but may not be discovered because of path, trust, or session-cache behavior;
- mirrored skill copies need consistency checks;
- a cross-agent skill needs a repeatable smoke test.

Do not use it for a skill that belongs to one runtime only, or for a one-off prompt that does not need persistence.

## Ownership and Safety

Before editing anything, classify each target skill as bundled, hub-installed, externally owned, pinned, user-owned, project-local, or curator-managed.

- Do not edit bundled, hub-installed, externally owned, pinned, or user-owned skills.
- If a user-owned skill needs a change, report the issue and recommend the supported adoption path instead.
- Use `skill_manage` for Hermes user-local skills. Use `write_file` or `patch` for repository-owned skill files.
- Never overwrite unrelated dirty files, credentials, or another agent's in-progress work.
- Treat a successful install as unverified until the target runtime discovers and exercises the skill.

## Source-of-Truth Decision

Choose one canonical copy before writing:

1. **Project-specific skill**: keep the canonical source in the project repository, normally under the target agent's project skill directory.
2. **Personal cross-project skill**: keep the canonical source in the user's skill library and install or mirror it into project loaders only when required.
3. **Portable multi-agent skill**: keep a repository copy in a loader-neutral project directory such as `.agents/skills/<name>/`, then add exact-content copies only for runtimes that require their own directory.

Record the mapping from canonical source to every mirror in the project's skill registry or equivalent inventory. Do not create an untracked copy with no ownership or update path.

## Procedure

### 1. Inventory the targets

List the runtimes that must load the skill and determine, for each one:

- skill directory and discovery rules;
- whether the project must be trusted or enabled;
- whether the target reads the current session only at startup;
- ownership and whether the existing skill is editable;
- the least-privilege, read-only smoke-test method.

Completion criterion: every target has a known loader path, ownership status, and verification method, or is explicitly marked unavailable.

### 2. Draft one portable skill

Write the canonical `SKILL.md` first. Keep its frontmatter and core behavior target-neutral. Put runtime-specific commands, provider quirks, or error transcripts in `references/` rather than forking the core instructions.

Completion criterion: the canonical skill has a valid name, short trigger-oriented description, explicit scope, procedure, pitfalls, and verification criteria.

### 3. Install or mirror deliberately

Use the target's supported write path:

- `skill_manage(action='create', ...)` for a new Hermes user-local skill;
- `write_file` for a repository-local `SKILL.md`;
- `skill_manage(action='write_file', ...)` for support files under `references/`, `templates/`, or `scripts/`.

When multiple copies are unavoidable, copy the complete canonical content. Do not hand-edit one mirror to compensate for a target difference. Put target adaptation in the shared skill or in a clearly named reference.

Completion criterion: every intended target has exactly one owned copy or a documented supported installation, and no protected skill was changed.

### 4. Validate static consistency

Check every mirror for:

- identical content and matching checksums;
- valid frontmatter and non-empty body;
- a description within the active repository or loader limit;
- no machine-specific paths in portable content;
- references that actually exist;
- no stale target name, old path, or contradictory version.

Use `read_file`, `search_files`, `execute_code`, or `terminal` as appropriate. Do not treat a directory listing as proof that the content is valid.

Completion criterion: all intended mirrors pass the same validation set and any intentional difference is documented.

### 5. Smoke-test fresh runtimes

For each target, start a fresh process or session and ask it to use the skill on a small, representative, read-only input. Verify both discovery and behavior:

- discovery shows the expected skill name or the agent visibly loads it;
- the output follows a distinctive rule from the skill;
- no write, delete, network mutation, or irreversible action is needed for the test;
- startup-cache behavior is recorded when the current session cannot reload skills.

Completion criterion: each target has an observed result, not merely an installation command or a self-report from an unverified process.

### 6. Record and report

Update the project inventory with the skill name, source, target runtimes, install paths, ownership, and review date. Report:

- canonical source and mirrors;
- static validation result;
- fresh-process smoke-test result for each target;
- any non-blocking warning that occurred;
- reload or trust steps required for future sessions;
- unrelated changes intentionally left untouched.

Completion criterion: another agent can locate the source, reproduce the checks, and understand what was actually verified.

## Quick Reference

- Discover installed Hermes skills: `terminal(command="hermes skills list --source local --enabled-only")`
- Read a skill: `skill_view(name='<skill>')` or `read_file(path='<path>')`
- Write a Hermes skill: `skill_manage(action='create', ...)`
- Write a repository skill: `write_file(path='<repo-relative-skill-path>', content='...')`
- Add a support file: `skill_manage(action='write_file', name='<skill>', file_path='references/<topic>.md', file_content='...')`
- Compare mirrors: use `execute_code` or `terminal` to calculate checksums, then inspect mismatches with `read_file`
- Verify after startup: run a fresh target process, not only the current chat

See `references/verification-matrix.md` for a compact target-by-target verification checklist.

## Pitfalls

- **One copy per target with no source of truth**: this creates silent drift. Record a canonical source and mirror map.
- **List-only verification**: a listed skill may be disabled, unreadable, stale, or ignored by the active project. Exercise it.
- **Current-session optimism**: many loaders cache skills at startup. Use a fresh process or explicitly record the reload boundary.
- **Protected-skill edits**: being relevant or loaded does not grant ownership. Stop and recommend adoption when required.
- **Target-specific forks**: forks make later fixes inconsistent. Prefer shared instructions plus references.
- **Unsafe smoke tests**: a skill can be verified with a dry run or read-only sample. Do not mutate real data merely to prove discovery.
- **Warning inflation**: distinguish a non-blocking runtime warning from a failed skill test. Record it without turning it into a permanent refusal.

## Verification

The distribution is complete only when the canonical source is identified, every intended target has a documented owned copy or supported install, mirrors pass static consistency checks, each target has a fresh-session behavior check, and the registry records the result. If any target is unverified, report it as unverified rather than calling the distribution complete.

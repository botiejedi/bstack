---
name: central-skill-registry
private: false
description: "Use when creating, installing, or discovering any skill."
version: 1.0.0
author: botiejedi, Hermes Agent
license: MIT
platforms: [macos]
metadata:
  hermes:
    tags: [skills, registry, obsidian, provenance]
    related_skills: [cross-agent-skill-distribution, obsidian]
---

# Central Skill Registry

Register every skill that is created, installed, or discovered while working on a project in your central Obsidian skill inventory. This records provenance and ownership without turning the vault into an uncontrolled software mirror.

## When to Use

Load this skill whenever a task creates, installs, imports, mirrors, updates from a new source, or newly discovers a reusable agent skill in any project. Use it before declaring that skill task complete.

## Central Record

Configure these for your setup (defaults shown):

- Vault: `<vault>` (your Obsidian vault, ideally a Git repository)
- Registry: `<vault>/_system/skills/registry.md`
- Vault-native procedures: `<vault>/_system/skills/active/`
- Private folder(s) never to touch: `<private-folder>`

The registry is the inventory source of truth. Do not copy a third-party skill's full code into the vault unless the user explicitly chooses the vault as its canonical source.

## Procedure

1. Read the vault's agent instruction files (for example `AGENTS.md` and `CLAUDE.md`) before editing, if present.
2. Fetch `origin/main`. If the working tree is clean, pull with rebase. If it is dirty, verify that local `main` and `origin/main` have not diverged, then make only a targeted merge into the registry. Never overwrite unrelated dirty work.
3. Check the registry file for the skill name and canonical source. Update an existing row instead of creating a duplicate.
4. Record, at minimum: name, canonical source or repository, privacy classification (`private: true` vs `private: false`), status and ownership, agent targets, scope, install paths, version or immutable revision when available, review date, and operational notes.
5. **Privacy gate (on create and every revision):** check whether the skill contains sensitive details (credentials, private IPs, hostnames, internal URLs) or deployment-specific setup (personal paths, machine names, private-only plugins/tools, vault internals) that would not be useful publicly. If yes, ensure `SKILL.md` frontmatter declares `private: true` (and includes `private` in `tags:` if present) and store it in `private-skills/` (excluded from public sync). If no, declare `private: false` and store it in `skills/`. Re-verify on every revision.
6. For a project-local skill, record its project path and whether it is canonical or a mirror. For an external skill, record the upstream URL and installed revision. For a mirrored skill, identify the canonical copy and every target.
7. Add or update a source note in the vault's sources area (for example `<vault>/Sources/Repos/`) only when the external repository needs adoption context beyond the registry row.
8. Verify the targeted diff and confirm that no unrelated vault file, private-folder content, or secret was staged or changed.

## Completion Gate

A skill task is not complete until the central registry reflects the current source, targets, paths, version or revision, and ownership. If the vault is unavailable or conflicted, report the registry update as pending rather than silently omitting it.

## Pitfalls

- Do not treat the registry as a package manager.
- Do not vendor externally owned skills merely to make the row look complete.
- Do not replace an existing row without reconciling its prior mirrors and notes.
- Do not run `git pull --rebase` through unrelated dirty work.
- Do not claim a runtime can load a skill until a fresh process discovers it.

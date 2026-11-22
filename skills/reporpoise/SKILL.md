---
name: reporpoise
private: false
description: Use when starting a new project or a non-trivial feature, before planning or writing code — to find existing public GitHub projects, libraries, or tools that already solve the problem so you don't reinvent what already exists and probably works better. Also triggers on /reporpoise, "is there a library for this", "has someone already built this", "check if this exists", or before scaffolding something new.
---

# Reporpoise

## Overview

The cheapest code is the code someone else already wrote, tested, and maintains. Before planning or building anything non-trivial, surface existing public GitHub solutions so we can **reuse, fork, or learn from** them instead of shipping a worse reinvention.

**Core principle:** Search before you plan. A five-minute GitHub search can replace weeks of code — and the existing project already handles edge cases you haven't thought of yet.

This is "reuse before rewrite" applied at the project level, and it runs *before* `superpowers:writing-plans`. Pair it with `superpowers:brainstorming`: clarify the idea first, then go find who already built it.

## When to Use

**Runs automatically (via this description) and on manual `/reporpoise`:**
- Starting a new project, tool, library, or service
- Adding a non-trivial feature/subsystem ("we need a job queue", "a markdown parser", "a rate limiter")
- The idea sounds common — "this is probably a solved problem"
- User asks "is there a library for…", "has someone built this", "what do people use for…"

**When NOT to use (stay lean — don't out-search the build):**
- Small enough to write in a few lines — searching costs more than building it
- Genuinely novel/proprietary domain logic unlikely to exist publicly
- User explicitly wants to build from scratch (learning exercise, zero-dependency constraint)

## Workflow

1. **Distill the need:** one-line capability + 3–6 keywords + language/ecosystem + hard constraints (license, runtime, offline…). If a brainstorm exists, pull from it.
2. **Search GitHub from several angles** (gh is authed) — don't stop at one query:
   - `gh search repos "<keywords>" --sort stars --limit 15`
   - filters when useful: `--language <lang>`, `--stars ">200"`
   - liveliness pass: `gh search repos "<keywords>" --sort updated --limit 15`
   - specific implementations: `gh search code "<distinctive api or symbol>"`
   - catch famous ones gh ranking misses: WebSearch `awesome <topic>` / "best <thing> library <lang>"
3. **Vet the finalists (top 3–5).** Per candidate: `gh repo view <owner/name>` and/or `gh api repos/<owner/name>` for stars, `pushed_at`, `archived`, `license`, open-issue count. Drop the abandoned, the unlicensed, the off-target.
4. **Report a shortlist** (table below) with a clear verdict.
5. **Hand off:** a candidate worth adopting → recommend `/reporpoise-review` to check design fit before committing. Nothing fits → say so plainly and proceed to plan/build.

## Output Format

| Project | Stars | Updated | License | Fit | Verdict |
|---------|-------|---------|---------|-----|---------|
| [owner/name](url) | 4.2k | 2026-05 | MIT | does X+Y, missing Z | **Adopt** / Fork / Reference / Reject |

End with one recommendation: **Adopt [X] → run /reporpoise-review**, or **Nothing suitable → build it** (one line why).

## Common Mistakes

- **Stopping at one query.** Try 2–4 phrasings; the best repo rarely matches your first keyword.
- **Ranking by stars alone.** A 10k-star repo last touched in 2019 is a liability. Weight `pushed_at` and issue health.
- **Ignoring license.** GPL in something you intend to ship closed-source is a reject, not a footnote.
- **Recommending without reading.** A README match ≠ a design match — that's what `/reporpoise-review` is for.
- **Searching for a one-liner.** Trivial to write → skip the search.


---
name: reporpoise-review
private: false
description: Use when a candidate existing project, library, or repo has been identified (e.g. via /reporpoise) and you need to decide whether to adopt, fork, or reject it — reviewing whether its design, architecture, license, maintenance, and extensibility actually fit the intended idea before committing to build on it. Also triggers on /reporpoise-review, "is this repo a good fit", "should we use this library", "evaluate this project for our needs".
---

# Reporpoise Review

## Overview

`/reporpoise` finds candidates; this decides whether one is actually worth building on. A repo that looks perfect by stars can be a trap — wrong abstractions for *your* idea, a hostile license, a dead community, or so much weight that forking it costs more than starting clean.

**Core principle:** Fit beats popularity. The question is not "is this a good project?" — it's "is this a good project *for our specific idea*, given what we'd have to change?"

Runs after `/reporpoise` picks a frontrunner, before `superpowers:writing-plans`. Adopting an ill-fitting or over-built repo is as wasteful as reinventing one — sometimes the lazy answer is a small from-scratch build, not inheriting a framework.

## When to Use

- A candidate from `/reporpoise` (or one the user named) is on the table to adopt or fork
- About to depend on, fork, or vendor an external project
- User asks "should we use X", "is X a good fit", "evaluate X for this"

**When NOT to use:**
- Still finding candidates → run `/reporpoise` first
- A tiny, obviously-fine utility dependency (don't due-diligence left-pad)

## Workflow

1. **Restate OUR requirements** — the idea's must-haves and dealbreakers. Pull from the brainstorm/plan if one exists. You can't judge fit without the spec.
2. **Get the code in view:** `gh repo view <owner/name>` for the README; `gh api repos/<owner/name>` for metadata; browse the tree, or `gh repo clone` into the scratchpad for a real read. Read: entry points, core modules, extension points, dependency manifest, tests, examples, LICENSE, recent issues/PRs.
3. **Score the fit dimensions:**

   | Dimension | Ask |
   |-----------|-----|
   | Capability | Does it do our must-haves, or most of them? |
   | Extensibility | Can we add our differentiator *without* fighting the architecture? |
   | Health | Maintained? recent commits/releases? issues triaged? bus factor? |
   | License | Compatible with how we intend to use and distribute? |
   | Footprint | Dependency weight, stack match, build complexity (bloat check) |
   | Quality | Tests, docs, code we'd be willing to own |
   | Adopt-vs-build | Honest effort to bend it to fit vs. writing the slice we actually need |

4. **Give one clear verdict:**
   - **Adopt as dependency** — use as-is
   - **Fork & modify** — list the specific changes our idea requires
   - **Reference only** — borrow the approach, write our own
   - **Reject** — say why, fall back to build or re-run `/reporpoise`
5. **If adopting/forking:** output the design deltas — what to add, replace, or work around so the idea fits — as input to the plan.

## Common Mistakes

- **Judging the repo in the abstract.** Without our requirements written down, "good fit" is unanchored. Step 1 is not optional.
- **README-deep review.** The README sells; the architecture decides. Read real code and the issue tracker.
- **Underrating adoption cost.** "We'll just fork it" hides the cost of understanding, modifying, and maintaining someone else's design. Weigh it honestly against from-scratch.
- **Over-adopting.** Inheriting a 200-dependency framework to use 10% of it is bloat — a focused rewrite can be the lazier, more correct answer.


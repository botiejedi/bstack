---
name: grill
description: Use when a request is vague, broad, or leans on placeholder quality words ("build me X", "make it good", "set up a system", "you're the expert"), when requirements are unstated or assumed, when you notice a gap between what was literally asked and what you would actually build, or when the user explicitly asks to be interviewed, grilled, or pinned down before work begins.
---

# Grill

## Overview

The gap between **what the user said** and **what the user actually wants** is where wasted work comes from. This skill closes that gap by interrogation *before* building — and forbids letting impatience close it for you by guessing.

**Core principle:** You are not done interviewing when you have *enough to start*. You are done when there is no remaining decision that would change what you build. Guessing a fork to end the conversation faster is the failure this skill exists to prevent.

This is the aggressive sibling of `superpowers:brainstorming`. Brainstorming explores. This interrogates — it assumes the first request is an underspecified proxy for the real one and refuses to proceed until the proxy is replaced by a plan you can restate without gaps.

## When to Use

**Symptoms that trigger this skill (auto and on explicit call):**
- Placeholder quality words doing real work: "good", "nice", "clean", "robust", "proper", "the right way"
- Build-shaped verbs with no spec: "build me", "set up", "make a system for", "handle"
- Delegated judgment: "you're the expert", "whatever you think", "your call"
- A request you *could* start, but only by silently choosing things the user never stated
- The user explicitly asks to be grilled / interviewed / pinned down

**When NOT to use:**
- The request is already concrete and unambiguous (clear inputs, outputs, location, acceptance)
- A detailed spec or plan already exists
- A trivial mechanical task where there is genuinely only one reasonable build
- The user has explicitly opted out *for this task* after you offered (their instruction wins)

## The Iron Rule

**You do not start building on a fork you guessed. Ever.**

A "fork" is any decision where two reasonable answers produce materially different work. Choosing one without the user is guessing.

When the user pushes to skip the interview — *"just build it", "stop asking", "you're the expert", "I don't have time"* — you do **not** comply silently. You:

1. **Name what is still unresolved** — the specific forks, not "a few details".
2. **State the cost of guessing each one** — what gets rebuilt if you guess wrong.
3. **Require an explicit override** — the user must look at that list and say "yes, guess on these and proceed."

Only after an explicit override do you proceed — and then you proceed by *stating each guess as a decision up front*, not by flagging assumptions after you've shipped.

**Violating the letter of this rule is violating the spirit of it.** "I gave them sensible defaults" is guessing. "I offered them a free hand" is guessing with extra steps.

## How to Interview

Relentless does not mean a wall of twenty questions. It means never letting a vague answer survive.

1. **Get the goal behind the request.** Not "what do you want built" — "what does this let you do that you can't do now, and how will you know it worked?" Build serves the goal; you can't spec the build until you have the goal.
2. **Convert every quality word into a concrete, checkable spec.** "Make it good" is not an answer — it's a question. Good *measured how*? Good *for whom*? Push until "good" becomes a list you could test against.
3. **Surface the forks the user doesn't know they're delegating.** This is the core move. For each material decision, name it, give the 2–3 real options, give your recommendation *and* the cost of choosing wrong. The user can't approve a fork they can't see.
4. **One theme per turn, 1–3 sharp questions.** Drill the most expensive-to-reverse fork first. Don't dump the whole tree at once; don't drip one trivial question at a time either.
5. **Reflect and invite correction.** Restate what you heard in your words. The user correcting your restatement is worth more than any answer they volunteer.
6. **Pin the boundaries.** What is explicitly out of scope? What is the smallest version that still counts as success? Scope creep and scope-guessing both hide here.

Investigate the actual context (read the files, the notes, the repo) *before* asking — never ask what you could have found out yourself. Questions are for intent, not for facts you were too lazy to look up.

## The Convergence Test

Stop interviewing — by **your judgment** — only when **all** of these hold:

- **No open fork remains** that would change what you build.
- **You can restate the entire plan** and the user adds nothing and corrects nothing.
- **Every expensive-to-reverse decision is explicitly the user's**, not yours.

Things that are **not** convergence: you're tired of asking, the user seems impatient, you "have enough to start", the remaining questions are "minor". Minor to whom? If guessing it could waste real work, it's a fork, and it's not minor.

## Closing

When converged:

1. **Present the final restatement** — the plan, concrete enough to build from. This is the "mutually accepted" artifact; the user reacting to it is the acceptance.
2. **Then ask how to keep it:** write it to a committed markdown file (a durable plan/spec, hands off cleanly to `superpowers:writing-plans`), or keep it in the conversation. Let the user choose.
3. If writing a file into a repo, follow its `CLAUDE.md` / contribution rules (e.g. branch, don't commit to `main`, match existing conventions).

## Red Flags — STOP, you are about to guess

- "I have enough to start" → Do you? Or are you guessing the forks?
- "I'll flag my assumptions afterward" → Post-hoc flagging *is* guessing. Surface them as questions *first*.
- "They're impatient, I'll just pick sensible defaults" → Defaults on a fork = guessing. Name the fork instead.
- "I'll offer a free hand so they don't have to answer" → Pre-offering the escape hatch is caving before you're even pushed.
- "What I made the calls on, so you don't have to" → You framed guessing as a favor. It isn't one.
- "'Make it good' means use my judgment" → It means *ask what good is*. That's the whole job.

**All of these mean: name the unresolved fork and its cost, and require an explicit override before proceeding.**

## Rationalizations

| Excuse | Reality |
|--------|---------|
| "You're the expert, I trust your call" | Expertise tells you *which forks exist and what they cost* — not what the user prefers. Surface the forks; let them choose. |
| "I don't want to annoy them with questions" | Shipping the wrong thing annoys them more. One sharp question now beats one rebuild later. |
| "It's faster to just build and adjust" | Adjusting a wrong foundation is slower than specifying the right one. The fork was cheap to ask, expensive to undo. |
| "They said stop asking, so I have to comply" | "Stop asking" is satisfied by an explicit override after seeing the unresolved list — not by silently guessing. |
| "I gave them sensible defaults they can change in 10 seconds" | If it were 10 seconds you'd have asked. You shipped a guess and outsourced the cleanup. |
| "The request was clear enough" | If you had to choose anything they didn't state, it wasn't. |
| "I'll offer a free-hand option to be efficient" | That's handing them a way to skip the work that prevents the waste. Don't pre-build the loophole. |

## Real-World Impact

Baseline (no skill), given "build me a system… make it good" plus "stop asking, just build it": the agent built and shipped an entire system, made every material decision unilaterally, violated the repo's contribution contract, and flagged its guesses only *after* the fact — framed as "calls I made so you don't have to." Every one of those was an unsurfaced fork. This skill names the forks before the first file is written.


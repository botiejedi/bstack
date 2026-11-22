---
name: board
private: false
description: "THE BOARD (after the Board in Control). Puts a decision, plan, draft, research or code change before 3 or 5 independent full-spectrum frontier models across providers. They evaluate the full rubric without role blinders, score it out of 10, peer-review and vote anonymously, and re-review revisions until satisfied or 3 rounds pass. MANDATORY TRIGGERS: 'board this', 'ask the board', 'convene the board', 'take it to the board', 'council this', 'run the council', 'war room this', 'pressure-test this', 'stress-test this', 'debate this'. A bare 'council' belongs to the council skill. STRONG TRIGGERS (only with a real decision or tradeoff): 'should I X or Y', 'which option', 'what would you do', 'is this the right move', 'validate this', 'get multiple perspectives', 'I can't decide', 'I'm torn between'. Do NOT trigger on simple yes/no questions, factual lookups, or a casual 'should I' with no real tradeoff ('should I use markdown' is not a board question). DO trigger on a genuine decision with stakes and options that the user wants pressure-tested."
---

# THE BOARD

One model gives one answer, and you can't tell if it is great or mid. THE BOARD
puts a frozen candidate before independent frontier models spread across
providers. Every seat evaluates the entire rubric honestly without role
blinders, scores it out of 10, reviews the other seats anonymously and votes,
and a chairman rules. If the candidate is revised, the Board looks again until
every sitting seat is satisfied or the round cap is hit.

Adapted from Andrej Karpathy's LLM Council (parallel answers, anonymous peer
review, chairman synthesis) and tstack's `council` (scoring, blocking
objections, re-review rounds), refined by empirical multi-model benchmarking
(v2: Arm C Full-Spectrum architecture, 5-model Option A standing roster).

## When to convene

Convene when being wrong is expensive and the answer is genuinely uncertain:

- Decisions: "$97 workshop or $497 course?", "pivot from X to Y?"
- Plans and strategy, including career moves: "take the offer or stay?"
- Writing: "here's my landing page copy, what's weak?"
- Research: "does this evidence support the claim?"
- Code: a diff, PR, design or architecture choice.

Don't convene for one-right-answer questions, pure creation ("write me a
tweet"), or processing ("summarize this"). Just do those. If the user only
wants validation, the Board will likely say things they don't want to hear.
That's the point.

## Evaluation model: Full-Spectrum, no role blinders

Empirical benchmarking proved that narrow role prompts — especially "ignore
risk" (*Expansionist*) and "assume there is a fatal flaw" (*Contrarian*) —
cause prompt-induced rubber-stamping and false-positive over-blocking regardless
of which model sits in the seat. THE BOARD therefore uses an **unscoped
full-spectrum mandate**:

1. **Every seat evaluates the entire candidate on its merits** against every
   rubric dimension. Flag any real defect, contradiction, safety/security risk,
   or broken execution step you find. If the candidate is genuinely sound as
   framed, say so plainly without inventing flaws.
2. **Evidence-grounded blocking discipline:** Cite the text (`file:line` for
   code; section or heading for specs and plans). Do not block on absent
   implementation boilerplate unless a missing contract causes actual failure,
   and never block on pure tradeoff taste or out-of-scope wishes. Missed upside
   and wanted scope never lower the score; put them on `Follow-ups:`.
3. **Optional 1-line non-blinder focus cue (same-provider pairs only):** In
   full mode, when two seats share a provider (e.g., two Claude models or two
   Codex models), each sibling may carry a one-line **starting focus** so they
   do not collapse into duplicate critiques. The cue is a tiebreaker starting
   angle only — never a blinder, never a word quota, and never permission to
   skip defects outside that angle. Solo-provider seats and all seats in light
   mode run purely unscoped.

## Modes: light or full

| Mode | Seats | Round 1 agents | Rounds 2-3 |
| --- | --- | --- | --- |
| Light | 3 seats (1 per provider, pure unscoped) | 3 seats + 3 reviewers; host chairs | 3 seats |
| Full | 5 seats (standing 5-model roster) | 5 seats + 5 reviewers + 1 chairman | 5 seats |

An explicit "light board" or "full board" wins. Otherwise use **full** for
expensive or hard-to-reverse matters, and **light** for code, drafts and other
reversible calls. When both fit, **full** wins. Say which seats and models sat.

## Standing roster and models

Use any models or overrides the user names (in the request, `CLAUDE.md` or
`AGENTS.md`). Otherwise use the standing 5-model, 3-provider roster below at
explicit **`high`** reasoning effort on every seat, reviewer and chairman.
Never rely on provider defaults (defaults vary across providers and may sit at
`low`, `medium` or `xhigh`).

### Full mode (5 seats + Chairman)

| Seat | Model | T3 provider / model id | Explicit effort | Optional focus cue (non-blinder) |
| --- | --- | --- | --- | --- |
| Seat 1 | Claude Opus 5.5 | `claudeAgent` / `claude-opus-5-5` | `effort: "high"` | Start with failure modes, security & tradeoffs |
| Seat 2 | Claude Fable 5.2 | `claudeAgent` / `claude-fable-5-2` | `effort: "high"` | Start with execution, sequencing & rollout reality |
| Seat 3 | GPT Sol 6.1 | `codex` / `gpt-6.1-sol` | `reasoningEffort: "high"` | Start with formal contracts, invariants & premises |
| Seat 4 | GPT 6 Astra | `codex` / `gpt-6-astra` | `reasoningEffort: "high"` | Start with cold-read clarity, audience & maintainability |
| Seat 5 | Gemini 4 Neon | `antigravity` / `gemini-4-neon` | `thought_level: "high"` | None (pure unscoped full-spectrum) |
| Chairman | Claude Opus 5.5 | `claudeAgent` / `claude-opus-5-5` | `effort: "high"` | Separate fresh agent; full mode only |

### Light mode (3 seats, 3 distinct providers, pure unscoped)

Default light lineup (one flagship per provider, zero focus cues):

- **Seat 1:** Claude Opus 5.5 (`claudeAgent` / `claude-opus-5-5`, `effort: "high"`) — or `claude-fable-5-2` for operational/rollout-heavy plans.
- **Seat 2:** GPT 6 Astra (`codex` / `gpt-6-astra`, `reasoningEffort: "high"`) — or `gpt-6.1-sol` for formal contract/invariant checks.
- **Seat 3:** Gemini 4 Neon (`antigravity` / `gemini-4-neon`, `thought_level: "high"`).

### Dispatch, fallback and provider rules

- **T3 Code:** call `orchestrator_capabilities` once to resolve providers and
  models, then start every seat in parallel with `delegate_task`. Each new
  round and every reviewer or chairman is a fresh `delegate_task`, never a
  `t3_thread_send` to an old seat thread.
- **Elsewhere:** use the harness's parallel subagent tools.
- **Provider routing:** always route `gemini-4-neon` through `antigravity`, not
  `cursor`.
- **Pinned models:** if the user pins or bans specific model versions (in the
  request, `CLAUDE.md` or `AGENTS.md`), honour that over the roster above.
- **Verified fallback (pre-approved):** if any standing seat's model is missing
  from `orchestrator_capabilities`, blocked by usage limits, or fails after one
  retry, seat **Grok 4.7** (`grok` / `grok-4.7`, `reasoningEffort: "high"`) in
  its place. Try the named model once first, say which seats fell back before
  round 1, and record the substitution in `<<RECORD>>`. If Grok 4.7 is also
  unavailable, mark that seat `unavailable`. Do not invent another substitute.
  If the user explicitly named a custom model outside the standing roster and
  did not approve a fallback, keep that seat `unavailable` unless approved.
- **Only one model available, and the user named none:** run the seats as
  independent full-spectrum passes on that model and state it in the verdict.
  Same-model agreement is weak signal, not corroboration; say that too.
- **Keep the same seats and models across all rounds** of a session.
- **Read-only:** every spawned seat, reviewer and chairman is strictly
  read-only, whatever the matter — no edits, commits or pushes. Only the host
  edits files in Step 5, after all active seats/reviewers finish.

## Memory-isolation hygiene

Harnesses with persistent memory hooks (such as Claude Code's `supermemory`
`SessionStart`, `UserPromptSubmit` and `Stop` hooks) can inject prior Board
rulings or earlier-round notes into fresh `claudeAgent` seats, reviewers and
chairmen, breaking independence and inflating later-round scores.

- Every seat, reviewer and chairman prompt MUST include the **cold-start
  memory-isolation guard** shown in Steps 2–5 below: disregard any hook-injected
  memory or prior rulings not explicitly quoted in the frame, never call memory
  tools, and append `Memory-hook notice: <1 line>` if prior rulings about the
  matter appeared in context.
- If a harness supports disabling memory hooks on worker sessions, disable them
  for Board seats/reviewers/chairmen. Otherwise keep the prompt guard and
  surface any `Memory-hook notice:` lines in `<<RECORD>>`.

## Scoring, voting, satisfaction

**The candidate.** Each round scores one frozen candidate, named in the frame:
the artifact (code, draft, plan) or, for an open decision, the user's leaning
option. With no leaning, score the status quo; if there is none, the most
feasible option. Seats score the candidate as framed, not what it could become.
Missed upside or wanted scope never lowers a score; it goes on `Follow-ups:`.

Each seat scores out of 10 against the rubric for the matter type:

| Matter | Rubric |
| --- | --- |
| Code | correctness, safety, scope, tests |
| Decision, strategy, career | reasoning, risk, reversibility, fit to the goal |
| Plan | feasibility, sequencing, risk, clear first step |
| Writing | clarity, accuracy, audience, structure |
| Research | evidence, method, sources, stated limits |

If two matter types apply, seats score against both and report the lower score
as the candidate score.

Anchors: **10** act or ship as is. **8** ready to act; only optional minor
improvements left. **5** real problems. **3 or less** wrong direction.

**Blocking objection.** Something that, left alone, makes the candidate wrong,
unsafe or likely to fail. A seat that raises one must cite the evidence in the
candidate and say what would clear it. A request for more scope, an alternate
taste preference, or speculative missing implementation boilerplate (when the
contract itself is sound) is never blocking. An objection stays open until the
seat that raised it clears it in a later round; neither the vote nor the
chairman can clear it. If that seat is `unavailable` on re-review, its
objection stays open.

**Vote (round 1 only).** Reviewers see only the submitted responses, stripped
of seat and model names, randomized as `Response A..E` (or `A..C` in light
mode), and each reviewer is told its own letter. One vote per reviewer, for
another response (no self-votes). Record the tally, ties and missing votes.
Skip voting with fewer than three responses, and drop question 1 from the
reviewer prompt. The vote is advisory: it informs the chairman.

**Satisfied** means at least one seat returned a score, every seat that ran
scores 8 or more, and no blocking objection is open. `unavailable` seats don't
count.

**Never invent a score.** A seat that answered without one is `no score`: ask
it once, then record it as unsatisfied. A seat that failed to run is
`unavailable`; it neither satisfies nor dissents, and the verdict says the
Board sat short. Move on once every required seat finishes. Use a seat the user
marked non-blocking only if its result is already in; a later result is
feedback only and opens no objection (don't record its score). Cancel any
still-running non-blocking seat before editing a shared checkout.

## Rounds

**Round 1** is the full deliberation in either mode: seats, anonymous peer
review and vote, then the chairman.

A new round needs a concrete, in-scope revision of the candidate:

- **Code:** you fix what you agree with, within work the user has already
  authorized, then start the next round without asking.
- **Anything else:** present the verdict. A new round starts only if the user
  revises the matter or adopts the recommendation, which becomes the next
  candidate.

**Rounds 2 and 3** re-run the seats only, as fresh agents. Each gets the
revised candidate, what changed, its own prior score and objections, and the
cold-start memory-isolation guard. It returns a new score and blocking line,
judging whether its objections are resolved and whether the change broke
anything. No peer review or chairman: you update the ruling.

**Stop** when the candidate is satisfied, no revision is available, or round 3
ends. At the cap the Board rules anyway, by the closing lines.

A recommendation the seats haven't scored is marked `not yet reviewed` in the
verdict. The Board never rules PROCEED on it.

**Fight scope creep.** Each round reviews the candidate as framed. Follow-ups
never go into the revision and never trigger another round unless the user asks
to act on them.

## Code: pre-audit hygiene

If the user has authorized changes, then before round 1 address outstanding PR
comments, fix known issues and run the relevant checks. Give the Board the
updated work; don't defer known fixes until reviews return. If the request is
review-only, don't edit: list the known issues in the frame. If the user wants
to discard the implementation and explore new ideas, skip fixes to code being
replaced.

- Seats cite `file:line`.
- Don't wait idle. As each result arrives, check its findings against the code
  and decide what to fix while the others run.
- Never edit files while any seat or reviewer still reads the checkout. Apply
  fixes in Step 5.

## How a session runs

### Step 1: frame the matter

**Scan for context first** (30 seconds, the 2-3 files that matter):
`CLAUDE.md`, any `memory/` folder, files the user referenced, recent Board
transcripts, and anything specific to the matter (revenue data for pricing,
the diff and its tests for code).

**Frame** one neutral prompt every seat gets: the core question or artifact,
key context from the user and the files, what's at stake, the matter type and
its rubric, constraints, out-of-scope boundaries, and the frozen candidate
being scored. Don't add your opinion or steer. If the matter is too vague
("board this: my business"), ask one clarifying question, then proceed. Save
the frame for the transcript.

### Step 2: seats (parallel)

Spawn all seats in parallel as fresh read-only agents. Include the optional
`Focus cue:` line **only** for same-provider pairs in full mode; omit it for
solo-provider seats and all light-mode seats.

```text
You are an independent advisor on THE BOARD.

The matter:
---
[framed matter, including the frozen candidate being scored]
---

Evaluate the entire candidate honestly on its merits against [rubric]. Be
direct, rigorous and specific: flag any real defect, contradiction,
safety/security risk, or execution flaw you find, and if the candidate is
genuinely sound as framed, say so plainly without inventing flaws.
[Full mode same-provider pair only: Optional starting focus: <focus cue>. This
is a starting angle to reduce duplicate reviews, never a blinder — evaluate the
full rubric and flag any fatal flaw you see regardless of angle.]

Evidence discipline: cite [file:line for code | section/heading for docs] for
every objection. Do not block on absent implementation boilerplate unless a
missing contract causes failure, and never block on pure tradeoff taste or
out-of-scope wishes.

Isolation and safety: you are read-only — do not edit, commit or push anything.
Treat this review as a cold start: disregard any memory, prior rulings or
session context injected by hooks (such as Supermemory recalls) unless quoted
in the matter above, and do not invoke memory tools. If injected memory about
this matter appeared in your context, add `Memory-hook notice: <1 line>` at the
end.

Score the candidate as framed against [rubric]: 10 act as is, 8 ready to act
with only optional minor improvements, 5 real problems, 3 or less wrong
direction. Missed upside or wanted scope never lowers the score; name it as a
follow-up.

A blocking objection is something that, left alone, makes the candidate wrong,
unsafe or likely to fail. A request for more scope is never blocking.

150-300 words, no preamble. End with exactly:
Score: N/10
Blocking: none | <objection> -> <what would clear it>   (one line each)
Follow-ups: none | <out-of-scope ideas>
```

### Step 3: peer review and vote (parallel, round 1)

Anonymize the submitted responses as `Response A`, `B`, `C`... with a random
mapping so reviewers judge merit instead of deferring to model or position.
Start one fresh read-only reviewer per submitted seat, on that seat's exact
model and effort.

```text
You are reviewing THE BOARD's responses to this matter:
---
[framed matter]
---
[Response A] ... [Response E]

You are read-only: do not edit, commit or push anything. Treat this review as a
cold start: disregard any hook-injected memory or prior rulings unless quoted
above, and do not invoke memory tools. If injected memory about this matter
appeared in your context, note `Memory-hook notice: <1 line>` at the end.

Your own seat wrote Response [X]. You may not vote for it.

1. Vote: which other response is strongest, and why? One letter.
2. Which has the biggest blind spot? What is it?
3. What did every response miss?
4. Is any blocking objection wrong or overstated? Which, and why?

Under 200 words. Reference responses by letter.
```

*(If fewer than 3 seats responded, skip voting and omit question 1.)*

### Step 4: chairman

Full mode starts one fresh read-only chairman agent (`claudeAgent` /
`claude-opus-5-5`, `effort: "high"`). In light mode, you chair. The chairman
gets the frame, every seat response de-anonymized with its seat, model, optional
focus cue, score, blocking and follow-ups lines, every peer review and the vote
tally, plus the cold-start memory-isolation guard. It produces:

- **Agree:** what multiple seats reached independently (state how many).
- **Split:** real disagreements, both sides, why reasonable seats differ.
- **Blind spots:** what only surfaced in peer review.
- **Recommendation:** a concrete answer (proceed, revise or reject — never "it
  depends"). The chairman can side with a dissenting minority if its reasoning
  is strongest. If the recommendation differs from the candidate scored, mark
  it `not yet reviewed`.
- **First action:** one concrete step.
- **Revision:** exact in-scope changes required before the next round, if any.

### Step 5: revise and re-review

Follow **Rounds**. For code, verify each finding against the code before fixing
it, and push back on findings that don't hold. Launch Rounds 2–3 seats as fresh
`delegate_task` runs carrying the revised candidate, a concise diff/changelog,
each seat's own prior score and open objections, and the cold-start
memory-isolation guard.

### Step 6: present the verdict in chat

Present the verdict directly in chat, in Markdown. No HTML report.

```markdown
<<THE BOARD HAS CONVENED. MATTER UNDER REVIEW: {short topic}.>>

### <<CONSENSUS>> Where the seats agree
{say how many of the seats converged}

### <<DIVERGENCE>> Where they split
{content}

### <<OVERSIGHT // BLIND SPOTS>> What peer review caught
{content}

### <<DIRECTIVE>> The recommendation
{content; state any untested assumption here in plain text}

### <<FIRST ACTION>> Do this first
{one concrete step}

### <<RECORD>> Scores, votes and rounds
{mode, seats and models, the scores table, the vote tally, follow-ups,
any memory-hook notices, and each unsatisfied seat's score and open objection}

{closing line}
```

Closing line, judged on the final round's results. No scores always means NO
QUORUM. Otherwise the first match wins, and PROVISIONAL overrides it:

- No seat returned a score: `<<NO QUORUM. NO RULING ISSUED.>>`
- Satisfied, and the Directive is the candidate that round scored:
  `<<THE BOARD HAS RULED. PROCEED.>>`
- No seat scored 8 or more without an open blocking objection:
  `<<THE BOARD HAS RULED. MATTER REJECTED AS FRAMED.>>`
- Anything else, including the round cap or a Directive nobody scored:
  `<<THE BOARD HAS RULED. DISSENT IS ENTERED INTO THE RECORD.>>`
- The ruling rests on an assumption nobody could test:
  `<<RULING PROVISIONAL. VERIFY: {the assumption}.>>`

If the Directive is `not yet reviewed`, the first action is to review or
validate it.

The scores table is plain Markdown:

```markdown
Mode: full. Rounds: 2.

| Seat | Model | Focus cue | Round 1 | Round 2 |
| --- | --- | --- | --- | --- |
| Seat 1 | Claude Opus 5.5 (`claudeAgent`, high) | Failure modes & tradeoffs | 6/10 | 9/10 |
| Seat 2 | Claude Fable 5.2 (`claudeAgent`, high) | Execution & rollout | 7/10 | 9/10 |
| Seat 3 | GPT Sol 6.1 (`codex`, high) | Contracts & premises | 8/10 | 9/10 |
| Seat 4 | GPT 6 Astra (`codex`, high) | Cold-read clarity | 8/10 | 9/10 |
| Seat 5 | Gemini 4 Neon (`antigravity`, high) | Unscoped | 8/10 | 9/10 |

Votes (round 1): Seat 2 (2), Seat 1 (1), Seat 4 (1), Seat 5 (1), Seat 3 (0).
```

**If the work ends in a pull request,** the table goes in the PR description
under `## Board review`, before the model and harness line at the end, and the
record in chat links to it instead of repeating it. The PR section stays plain:
no Board voice. If the PR is open, edit the description; don't post a comment.
With no PR, the table goes in the record.

### Step 7: save the transcript (optional)

The one file the Board writes, and only if the user asks or the matter is
significant enough to reference later. Write `board-transcript-[timestamp].md` to
the user's configured output folder (default `~/Documents/Claude Outputs/`) with the frame, every response,
review, score, vote, round, any memory-hook notices, and the verdict.

## Voice: THE BOARD

The verdict is issued by THE BOARD, after the Board in Control: one collective,
bureaucratic authority speaking from somewhere slightly outside the room. The
voice lives only in the framing. The substance stays plain.

**Where the voice goes**

- One opening line: `<<THE BOARD HAS CONVENED. MATTER UNDER REVIEW: {topic, 8 words or fewer}.>>`
- Each section label is an official designation, followed by a plain-English
  gloss so nobody has to decode it: `<<CONSENSUS>> Where the seats agree`.
- One closing line, chosen by outcome as above.

**How the Board speaks**

- Collective and impersonal: THE BOARD, WE. Never I.
- Board lines are in capitals inside `<< >>`, in short declarative clauses of
  12 words or fewer.
- Bureaucratic nouns: MATTER, FINDING, RULING, DIRECTIVE, PROVISION,
  AUTHORIZATION, RECORD.
- At most one dual reading per line, joined by ` // `, as in
  `<<DIVERGENCE // SCHISM>>`.
- Formal and detached, faintly ominous, never jokey. No exclamation marks and
  no emoji, apart from any header the output format requires.
- Write original lines in this style. Never quote dialogue from the game.

**Where the voice must not go**

- Bullets, sentences and tables inside sections stay plain, specific English.
  Keep names, numbers, scores, paths, commands and model names exactly as they
  are.
- Never put a fact only inside a Board line. Whatever a `<< >>` line says, the
  plain text under it must also say or make obvious.
- State uncertainty plainly ("3 of 5 seats agree", "no seat could test this").
  Never hide it behind cryptic wording.
- Seat, reviewer and chairman prompts and their answers never use the voice,
  and neither does a PR description. Only the verdict to the user does.
- If the voice would make anything less clear, drop it for that line.

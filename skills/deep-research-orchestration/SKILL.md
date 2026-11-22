---
name: deep-research-orchestration
description: Scope and route multi-domain research with evidence.
version: 0.1.0
author: botiejedi, Hermes Agent
license: MIT
platforms: [linux, macos, windows]
metadata:
  hermes:
    tags: [Research, Orchestration, Evidence, Scoping]
    related_skills: [grounded-citations, blocked-page-recovery, arxiv]
---

# Deep Research Orchestration

Use a scope-first, domain-specific method for substantial research. This skill governs the research contract, workstream design, source diversity, synthesis, and durable source-reliability learning. It does not replace specialist retrieval or implementation skills.

## When to Use

Use for:

- broad or ambiguous questions needing refinement;
- multi-source investigations, comparisons, or recommendations;
- code implementation research that must end in a runnable proof;
- political, financial, scientific, legal, historical, or market research;
- mixed-domain questions that need several research methods;
- work worth delegating into independent angles.

Do not use for a simple lookup, a single supplied document, or a bounded task that can be answered directly.

## Scope Contract

Before expensive retrieval, define:

1. **Decision or question:** what the research must resolve.
2. **Intended use and audience:** implementation, purchase, policy brief, personal understanding, executive decision, or another outcome.
3. **Boundaries:** entities, jurisdiction, technical version, date range, geography, and explicit exclusions.
4. **Evidence standard:** exploratory, decision-grade, or high-stakes fact-checking.
5. **Deliverable:** chat brief, report, comparison table, implementation artifact, or vault note.
6. **Budget:** quick, standard, or deep, including whether parallel specialists are justified.

Ask at most five high-information questions when missing answers could materially change the method or waste the budget. Otherwise state assumptions and proceed. Done when a reader could decide whether a candidate source or subquestion is in scope.

## Select Research Modes

Combine modes only when the question genuinely crosses domains.

### Code implementation

- Freeze repository, branch or release, language/runtime, operating environment, constraints, and acceptance test.
- Prefer official documentation, source code, release notes, issue trackers, and maintainer statements.
- Inspect the actual code or API. Pin versions and dates.
- End with a runnable spike, test, or command when implementation feasibility is the question.
- Distinguish documented support, observed behavior, open issues, and inference.

Completion criterion: the recommendation is tied to an exact version and a reproducible verification result, or the blocked layer is named.

### Political and public-policy

- Freeze jurisdiction, period, institutions, actors, and the exact policy or claim.
- Start with legislation, court opinions, regulations, budgets, official statistics, transcripts, and election records as applicable.
- Add independent reporting and institutionally or ideologically varied analysis.
- Attribute rhetoric and allegations to speakers. Separate enacted law, proposal, interpretation, forecast, and opinion.
- Seek meaningful counterevidence without giving unsupported claims artificial parity.

Completion criterion: material factual claims have primary evidence where available, competing interpretations are attributed, and the cutoff date is explicit.

### Financial and business

- Freeze entity or instrument, market, currency, period, accounting basis, and decision context.
- Prefer regulator filings, audited statements, exchange data, official investor materials, and timestamped market data.
- Distinguish GAAP or statutory figures from adjusted metrics, stock from flow, guidance from results, and price from valuation.
- Preserve units, currencies, periods, and observation timestamps.
- Treat company materials as primary for what the company reported, not as independent validation of its interpretation.
- State that research is informational when the output could be read as financial advice.

Completion criterion: every material number carries a period, unit, source, and appropriate timestamp.

### Scientific and medical

- Frame the question by population/system, intervention or exposure, comparator, outcome, and timeframe when applicable.
- Prefer systematic reviews, consensus guidance, peer-reviewed primary studies, and authoritative datasets.
- Treat preprints as provisional and inspect retractions, corrections, sample size, methods, and conflicts of interest.
- Separate statistical significance, effect size, mechanism, and real-world applicability.

Completion criterion: evidence hierarchy and study limitations are visible, with safety or professional-care boundaries where relevant.

### Legal and regulatory

- Freeze jurisdiction and current-as-of date.
- Prefer statutes, regulations, court opinions, regulator guidance, and official dockets.
- Separate binding authority, persuasive authority, guidance, commentary, and unsettled questions.
- Do not present research as legal advice.

Completion criterion: jurisdiction, authority level, and currency are explicit.

### Historical, product, and general research

- Historical: establish chronology, provenance, primary versus secondary accounts, and later reinterpretation.
- Product or market: compare official specifications, independent testing, ownership costs, security, support horizon, and user evidence.
- General: use the source hierarchy that best matches the decision and explain why.

Completion criterion: the method matches the claim type rather than using generic web popularity as authority.

## Build the Research Team

After the scope contract is stable:

1. Split the question into two to five non-overlapping workstreams.
2. Use `delegate_task` in parallel for independent angles, not sequential busywork.
3. Give every specialist the full scope, domain mode, exact questions, preferred primary-source classes, exclusions, cutoff date, and required output fields.
4. For disputed or high-stakes work, assign one workstream to counterevidence or adversarial fact-checking.
5. Require source URLs and verbatim evidence for load-bearing claims. Treat subagent summaries as leads until the orchestrator verifies them.
6. Reconcile overlap and conflicts before drafting. Do not average incompatible claims.

Done when each workstream has a distinct question and the union covers the scope without obvious duplication.

## Grounding and Retrieval

1. Load `grounded-citations` and reset a task-specific citation ledger.
2. Register URLs when retrieved, not after drafting.
3. Prefer direct extraction of the underlying page over search snippets.
4. Use `blocked-page-recovery` once normal retrieval fails; preserve snapshot provenance and date.
5. For high-stakes work, attach verbatim evidence and run the citation evidence gate.
6. Use at least one primary source where one exists, at least two independent discovery queries, and one deliberate counter-query for disputed claims.

Done when every load-bearing external claim is cited, explicitly marked unverified, or identified as an inference.

## Source Reliability Learning

The profile ledger is `$HERMES_HOME/research/source-reliability.md`. Resolve `$HERMES_HOME` before file operations.

At project start:

1. Read entries matching the current domain and topic.
2. Use preferred sources as search seeds, never as an allowlist.
3. Still run independent discovery and counter-queries.

At project end, update only evidence-supported observations:

- **Candidate:** useful once or twice, not yet preferred.
- **Preferred:** accurate and transparent across at least three independent projects in the same domain, with no unresolved material correction.
- **Authoritative by role:** a primary source for a narrow class of claims, such as a regulator for its filings. This does not make its interpretation neutral.
- **Downgraded:** repeated inaccuracies, silent corrections, poor provenance, or material coverage gaps. Preserve the reason and date.

Record domain, source, claim class, validated uses, last checked date, strengths, caveats, confidence, and counterevidence. Reliability is topic-specific and decays with age. User corrections override prior preference and must be recorded with provenance.

Done when the ledger captures only durable source behavior, not a dump of this project's findings.

## Synthesis Contract

Deliver:

1. Scope and assumptions
2. Direct answer or executive synthesis
3. Findings organized by research mode or decision factor
4. Conflicts, counterevidence, and uncertainty
5. Practical implications or implementation result
6. Method and coverage gaps
7. Inline citations and mechanically rendered Sources block
8. Suggested next question only when it materially changes the decision

## Pitfalls

- Researching a noun instead of a decision or falsifiable question.
- Delegating before scope is stable.
- Treating subagent confidence as verification.
- Using political balance as a substitute for evidence quality.
- Reporting financial figures without periods, units, or timestamps.
- Recommending code from current docs against an older installed version.
- Letting preferred sources crowd out discovery.
- Updating source reputation after one pleasing article.
- Spending a deep budget when a bounded lookup answers the question.

## Verification

- [ ] Scope contract is explicit or assumptions are labeled.
- [ ] Domain modes match the question.
- [ ] Workstreams are non-overlapping and justified.
- [ ] Primary, independent, and counterevidence searches ran where applicable.
- [ ] Citations map to retrieved sources and pass the ledger check.
- [ ] High-stakes claims preserve dates, jurisdiction, units, and uncertainty.
- [ ] Source-reliability updates are evidence-based and topic-specific.
- [ ] The deliverable answers the intended decision, not merely the topic.

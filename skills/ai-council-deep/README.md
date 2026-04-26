# AI Council Deep

Interactive variant of the AI Council with three user-in-the-loop checkpoints, designed for high-stakes decisions where one bad assumption can poison the entire council.

## Problem

The fast `ai-council` skill runs five independent advisors, anonymous peer review, and a chairman synthesis in about two minutes. It is a great pressure-test for reversible decisions.

Two failure modes appear when the stakes rise. First, high-stakes choices like term sheets, strategic pivots, and pre-publication strategy memos deserve more than a single fire-and-forget pass. Second, and more dangerous, is assumption fragility: one wrong premise propagates to all five advisors at once, and you do not see it until the verdict lands. By then, the work is spent and you restart from scratch.

The deep council adds three checkpoints at the points where these silent failures happen. The user clarifies the framing before advisors run, corrects assumptions before peer review, and can iterate after the verdict if new context shifts the picture.

## Approach

Same backbone as the fast council: five thinking lenses, anonymous peer review, chairman synthesis. The interactive variant adds three checkpoints at the moments when silent failures happen, plus a small set of design choices that keep advisors sharp at every step.

**Checkpoint 1, before dispatch.** The parent agent (not the advisors themselves) generates a single consolidated list of three to five clarifying questions by simulating what each advisor will struggle with. This avoids five parallel advisors all asking "what's the budget?" while preserving advisor independence on substance.

**Checkpoint 2, before peer review.** Each advisor surfaces the two or three most load-bearing assumptions their analysis depends on. The user reads only the assumption summary (not the full analyses) and corrects any that are wrong. Default behavior on a correction is a full advisor redraft, not a surgical patch on the one who voiced the assumption out loud, because the same misread usually lives latently in other advisors too.

**Checkpoint 3, after the verdict.** Up to two re-run rounds are available. New context propagates upstream as a fresh advisor pass, peer review, and chairman synthesis, not as an appendix tacked onto the original verdict.

Every checkpoint accepts `skip`, `ok`, `proceed`, or empty reply. Bail out whenever the question turns out simpler than expected.

## The Deliberation Process

**Phase 0: Frame the question.** The skill reads workspace context files (CLAUDE.md, memory directories, referenced files) to give advisors grounded specifics. The raw question is reframed as a neutral prompt with relevant context, stakes, and (when analyzing a published source) author credibility and publication context.

**Phase 0.5: Fact-check pass** (only if the council is evaluating source material). Web search verifies the source's load-bearing factual claims. Results categorize as Verified, Inaccurate/misleading, or Unverified, and feed into the framed question so advisors build on verified ground.

**Checkpoint 1: Clarifying questions.** The parent renders three to five high-leverage questions to the user. The user answers what they can and skips the rest.

**Phase 2: First-pass advisor responses.** All five advisors analyze the framed question simultaneously as sub-agents. Each advisor appends an "Assumptions I am making" section listing two to three load-bearing assumptions, plainly stated, no hedging.

**Checkpoint 2: Assumption surfacing.** The user sees per-advisor assumption bullets and a separate "Shared assumptions" view listing assumptions held by three or more advisors. Shared assumptions are the highest-leverage targets because correcting one invalidates multiple analyses simultaneously. The user proceeds, corrects with a full redraft, requests a targeted redraft of named advisors, or asks to see the full analyses inline before deciding.

**Phase 5: Anonymous peer review.** Advisor responses are relabeled A through E using a deterministic session-stable seed, so the same advisor maps to the same letter across all rounds. Five reviewer sub-agents each evaluate all five anonymized responses. Round-to-round comparison is then meaningful: Response B in round 1 and Response B in round 2 are the same advisor's evolution.

**Phase 6: Chairman synthesis.** One agent receives the framed question, all five de-anonymized advisor responses, all five peer reviews, and the annotated transcript of any prior rounds. Synthesis reflects the full arc, not just the final snapshot.

**Checkpoint 3: Post-synthesis iteration.** The user accepts the verdict, requests a full re-run with new context, or requests a targeted re-run of named advisors. Hard cap of two re-run rounds before the council closes.

**Phase 8: Final report and transcript.** The session produces an HTML report (with a checkpoint-history timeline that distinguishes a deep session from a fast one) and a Markdown transcript with the anonymization mapping revealed. If a prior report exists at the target path, it is timestamped and preserved before the new version is written.

## Design Rationale

**Three checkpoints, no more.** Each one targets a specific silent failure mode: framing ambiguity (CP1), assumption fragility (CP2), and post-verdict context gaps (CP3). Adding a fourth checkpoint would add user fatigue without addressing a distinct failure.

**Parent asks clarifying questions, not advisors.** Five parallel advisors generating their own clarifying questions duplicates work and dilutes the user's attention. The parent simulates what each advisor needs and produces one consolidated list.

**Assumption surfacing is additive, not hedging.** At Checkpoint 2, advisors surface the assumptions their analysis rests on without softening their stance. The edge stays sharp; the user, not the advisor, decides which assumptions are wrong.

**Shared assumptions get a separate view.** When three or more advisors hold the same assumption, it is high-leverage to correct: one fix invalidates multiple analyses at once. Surfacing this view explicitly steers user attention to the highest-impact corrections first.

**Default to full redraft on correction.** When the user flags a wrong assumption, the same misread usually lives latently in advisors who did not surface it. Targeted redraft is available, but the default re-runs all five.

**Default to full re-run at Checkpoint 3.** Earlier versions offered a "chairman re-synthesis only" option for new context. Users reported it produced an "appendix" feel: the new context was acknowledged but not actually integrated into how each advisor thinks. Removed in favor of full re-run as the default.

**Explicit approval before Round 2 dispatch.** If the user's re-run clarification implies edits to the source artifact rather than just additional framing context, the parent renders the revised version inline and waits for explicit approval before dispatching. A bare option choice is not sufficient approval for revisions the parent authored on the user's behalf.

**Two-round cap is a feature.** Past two iterations, sessions diverge instead of converge. The cap forces a decision: ship the current verdict or start a fresh council with the cumulative context.

**Deterministic anonymization seed.** Round-to-round diffing is meaningful only if the same advisor maps to the same response letter across rounds. Peer reviewers are still blind by construction (fresh sub-agents each round), so the integrity of peer judgment does not change.

**Backup before overwriting deliverables.** If a prior council report or transcript exists at the target path, it is timestamped and preserved before the new version is written. Re-runs do not silently destroy prior verdicts.

**Resume capability.** A `session_state.json` written after every completed phase lets the user pick the council back up if interrupted, or reopen a completed session days or weeks later when new information arrives.

## Usage

Trigger phrases: `deep council`, `interactive council`, `high-stakes council`, plus `resume council`, `resume the council`, `reopen council` to re-enter an interrupted or completed session.

Good questions for the deep council:
- "Should we take this term sheet?"
- "Which of these three pivots?"
- "Is this strategy memo sound enough to publish?"
- "We think we need X. Is that actually the question we should be asking?"
- "Pressure-test this position paper before I send it to the board."

When NOT to use this skill:

- **Time-sensitive decisions (hours, not days).** A deep council costs roughly 11 sub-agent calls per round and up to 25 across two rounds. Use the fast `ai-council` instead.
- **First drafts.** The council evaluates something coherent enough to peer-review. Write the draft first, then bring it back.
- **Late-stage editing (typos, formatting, line edits).** Advisors rebuild what does not need rebuilding.
- **Highly technical artifacts where domain expertise dominates** (legal contracts, compliance filings, technical specs, code). General-purpose advisor archetypes produce non-expert critique.
- **Hard length-constrained pieces** (haiku, tweet, headline, slide title). Advisors restructure beyond the constraint.
- **Highly emotional or interpersonal communications** (apologies, condolences, family disputes). Advisors handle frame and structure, not emotional register.
- **Decisions already made, where you want validation.** The skill is for genuine deliberation. If your mind is made up, it produces frustration rather than insight.
- **Single-shot creative writing where voice is the product** (poems, fiction passages). Advisors diagnose structure and overwhelm voice.
- **Trivial questions with one right answer** or simple summarization tasks.

Rule of thumb: if "I'll just re-run if it's wrong" feels fine, use `ai-council`. Otherwise, use this skill.

The skill can run standalone or after a prior fact-checking or analysis pass. When running after a prior analysis, include that analysis as context so advisors build on it rather than repeat it.

## Installation

1. Copy `SKILL.md` into `~/.claude/skills/ai-council-deep/SKILL.md`.
2. Restart Claude Code (or start a new session).
3. Trigger with one of the phrases above.

The skill is self-contained. It does not require `ai-council` to be installed, though installing both gives you a fast and a deep variant for matching the cost of the analysis to the stakes of the decision.

## Output

Every deep council session produces files in two locations.

In the working directory:

```
<project_name>-COUNCIL REPORT.html        visual report for scanning
<project_name>-COUNCIL TRANSCRIPT.md      full transcript with anonymization mapping
```

In a session subfolder (`<working_dir>/council-<YYYY-MM-DD-HHMM>/`):

```
framed_question.md
fact_check.md                    (only if Phase 0.5 ran)
session_state.json               (resume marker, written after each phase)
advisor_<n>_first_pass.md        (×5)
advisor_<n>_second_pass.md       (only if redrafted)
peer_review_<n>.md               (×5)
chairman_synthesis.md
chairman_synthesis_v<round>.md   (only if re-run)
```

Intermediate artifacts persist in the session folder so you can diff between rounds, audit specific advisor evolutions, or feed the transcript into a future session as Prior Analysis context.

## Acknowledgments

The `ai-council-deep` skill adapts the **interactive-ai-council** variant by **Freddy Gottesman**, GHP Labs.

- [LinkedIn](https://www.linkedin.com/in/fgottesman/)
- [GHP Labs](https://ghplabs.ai/)

The interactive variant builds on the original LLM Council skill by **John Graff**, Assistant Professor of Instruction, UT Austin McCombs School of Business.

- [LinkedIn](http://linkedin.com/in/johnmgraff/)

The underlying methodology is **Andrej Karpathy's** LLM Council: query multiple models independently, have them peer-review each other anonymously, and synthesize with a chairman agent. Karpathy is the founder of Eureka Labs.

- [GitHub](https://github.com/karpathy)

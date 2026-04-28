# AI Council

Pressure-test decisions with a structured five-advisor deliberation, anonymous peer review, and chairman synthesis.

## Problem

When you ask one AI a question, you get one answer. That answer might be sharp or shallow, and you have no way to tell because you only saw one perspective. Asking the same model multiple times does not help; the responses converge around the same framing.

High-stakes decisions, strategic choices, and important pieces of writing benefit from genuine disagreement, not simulated balance. The council produces that disagreement by design.

## Approach

The skill is adapted from Andrej Karpathy's LLM Council methodology: dispatch the question to multiple independent agents, have them peer-review each other anonymously, then a chairman synthesizes the results into a final verdict.

Rather than using different models, this implementation assigns each agent a distinct thinking lens. The lenses are chosen to create structural tension with each other, which forces the deliberation to cover ground that any single perspective would skip.

## The Deliberation Process

**Step 1: Frame the question.** Before convening, the skill reads workspace context files to give advisors grounded, specific information rather than generic starting points. The raw question is reframed as a neutral prompt with relevant context, stakes, and (when analyzing a published source) author credibility and publication context. For source analysis, a fact-check pass runs before advisors are convened.

**Step 2: Five advisors in parallel.** All five advisors analyze the framed question simultaneously as sub-agents. Parallel execution is required; sequential spawning would allow earlier responses to anchor later ones.

**Step 3: Anonymous peer review.** Advisor responses are collected and relabeled A through E with randomized mapping. Five new reviewer sub-agents each evaluate all five anonymized responses, identifying the strongest contribution, the biggest blind spot, what all five missed collectively, and any claims being treated as established without verification.

**Step 4: Chairman synthesis.** One agent receives everything: the framed question, all five de-anonymized advisor responses, and all five peer reviews. The chairman produces a structured verdict covering points of agreement, genuine disagreements, blind spots surfaced by peer review, an advisor position map with peer-consensus ratings, a clear recommendation, and a single concrete next step.

**Step 5 and 6: Report and transcript.** The session produces an HTML report (clean, scannable, with collapsible advisor sections) and a full Markdown transcript for reference.

## Design Rationale

**Five specific lenses, not five generic opinions.** The Contrarian and Expansionist create downside/upside tension. The First Principles Thinker and Executor create rethink/act tension. The Outsider sits across all four as a check on the curse of knowledge. Each lens was chosen because it catches things the others will systematically miss.

**Anonymous peer review is the core mechanism.** Without anonymization, reviewers defer to thinking styles they find credible rather than evaluating the actual argument. Anonymization forces evaluation on merit. This is Karpathy's key insight.

**The chairman can override the majority.** If four advisors recommend one path but the fifth dissenter has the strongest argument, the chairman should side with the dissenter and explain why. Synthesis is not a vote.

**Parallel execution is not optional.** Sequential advisor spawning lets earlier responses anchor later ones. The independence of thought that makes peer review valuable requires that advisors never see each other's work during Step 2.

**Don't council trivial questions.** The process takes several minutes. Use it for decisions where being wrong is expensive and multiple reasonable paths exist. For questions with one right answer, just answer directly.

## Usage

Trigger phrases: `council`, `council this`, `run the council`, `war room this`, `pressure-test this`, `stress-test this`, `debate this`

Good questions for the council:
- Pricing and positioning decisions
- "Should I do X or Y?" when both options are genuinely reasonable
- Strategic pivots where the stakes are high
- Evaluating published arguments, essays, or white papers before acting on them
- Stress-testing a draft before publishing

Not good questions for the council:
- Factual lookups with a single correct answer
- Content creation tasks ("write me a tweet")
- Simple summarization or processing tasks

The skill can run standalone or after a prior fact-checking or analysis pass. When running after a prior analysis, include that analysis as context so advisors build on it rather than repeat it.

For high-stakes decisions where one wrong assumption can poison the whole council, see the [`ai-council-deep`](../ai-council-deep/) sibling skill. It adds three user-in-the-loop checkpoints (clarify, surface assumptions, iterate) on top of the same five advisors and anonymous peer review.

## Output

Every council session produces two files in the workspace:

```
<project_name>-COUNCIL REPORT.html        visual report for scanning
<project_name>-COUNCIL TRANSCRIPT.md      full transcript for reference
```

The HTML report is the primary deliverable: chairman verdict at the top, collapsible advisor sections, agreement/disagreement visual, and a footer with timestamp. The Markdown transcript preserves the full deliberation record, including the anonymization mapping, for sessions where you want to trace how each advisor's argument was received.

## Installation

1. Copy `SKILL.md` into `~/.claude/skills/ai-council/SKILL.md`.
2. Confirm your environment has API access to the model providers the skill calls. Edit the model list in `SKILL.md` if you want a different lineup than the default.
3. Restart Claude Code (or run `/skills` to reload).
4. Trigger by saying "council this," "pressure-test this," or any other phrase listed under Usage.

For deeper, interactive deliberation on high-stakes decisions, also install the [`ai-council-deep`](../ai-council-deep/) sibling skill.

## Acknowledgments

The AI Council skill is adapted from an original LLM Council skill by **John Graff**, Assistant Professor of Instruction, UT Austin McCombs School of Business.

- [LinkedIn](http://linkedin.com/in/johnmgraff/)

The underlying methodology is **Andrej Karpathy's** LLM Council: query multiple models independently, have them peer-review each other anonymously, and synthesize with a chairman agent. Karpathy is the founder of Eureka Labs.

- [GitHub](https://github.com/karpathy)

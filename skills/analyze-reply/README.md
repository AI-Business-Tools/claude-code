# Analyze & Reply

Fact-check a forwarded article, essay, or email, then draft a reply in your voice.

## Problem

Someone forwards you a piece of writing and asks "what do you think?" or "how should I respond?" You face two separate tasks: evaluate whether the piece is actually right, and produce a reply that sounds like you. Most AI drafts collapse both steps into one, which produces replies that inherit the piece's framing rather than interrogate it, and that read as generic professional politeness rather than your voice.

This skill separates the two tasks so neither contaminates the other.

## Approach

The skill runs in three phases:

1. **Phase 1: Content analysis.** Classify the source (hard news, opinion, newsletter, academic, or personal message). Sort every substantive claim into one of four buckets: factual, not factual, opinion, or speculation. Attach a confidence level to each claim and use web search to verify time-sensitive or high-stakes factual claims before assigning a bucket. Assess attribution quality, engagement with counterarguments, and rhetorical moves.
2. **Phase 2: Reply options.** Present three reply tones (analytical, validating, short and warm) and ask which one fits, plus any specific points to emphasize or push back on.
3. **Phase 3: Draft.** Write the reply in your voice using the chosen tone.

A shortcut skips Phases 2 and 3: trigger with "vet" or "vet this" to run the analysis only. Nothing is drafted and you can decide afterward whether to reply at all.

## The Flow

**Step 1: Source classification.** Note the author's credentials, the publication, and any stated methodology. Flag when reporting blends with editorial framing.

**Step 2: Claim extraction.** Every claim lands in one of four categories:
- **Factual** (verifiable and supported)
- **Not factual** (wrong, outdated, or materially misleading, with correct information supplied)
- **Opinion** (value judgments, narrative framing, loaded language)
- **Speculation** (causal or forward-looking claims that cannot be directly verified)

Each claim gets a confidence level: High, Moderate, Low, or Unverifiable.

**Step 3: Structural assessment.** Attribution quality, counterarguments engaged (or not), connective tissue between events, and any Motte-and-Bailey patterns, appeals to authority, or guilt-by-association moves.

**Step 4: Summary.** A concise overall assessment covering what the piece gets right, where it is weakest, and the strongest counterargument the author does not engage with.

At this point, the vet shortcut stops. The full flow continues to Phase 2 options and Phase 3 draft.

## Usage

**Trigger phrases:** `analyze this`, `fact-check this`, `reply to this article`, `what do you think of this piece`, `draft a reply to this`, `vet`, `vet this`

**Good uses:**
- A colleague forwards an op-ed and asks for your read before you reply
- A client sends a press piece that misrepresents a technical claim and wants a response drafted
- You want to decide whether a piece is worth engaging with before spending time on a reply
- You want the fact-check on record even if you choose not to reply

**Not good uses:**
- Routine email replies with no substantive content to evaluate
- Writing from scratch (use a writing skill instead)
- Simple summarization (use a summary skill instead)

**Tips:**
- Use the vet shortcut first on anything high-stakes. Review the analysis. Then ask for the draft once you know the tone you want.
- Tell the skill what you already believe if it matters. The skill will not assume your position.
- Paste long pieces as a file path rather than the full text.

## Installation

1. Copy `SKILL.md` to `~/.claude/skills/analyze-reply/SKILL.md`.
2. Restart Claude Code (or start a new session).
3. The skill activates on any trigger phrase above.

## Optional: Layering a Writing Voice and Email Style

The skill drafts in "the user's voice" but does not define what that voice is. Out of the box, the draft uses generic drafting principles (density over elaboration, specificity, substantive openers, no flattery). That is usually good enough for the analytical option, sometimes good enough for the validating option, and rarely good enough for the short-and-warm option where tone carries most of the message.

For replies that reliably sound like you, layer two additional skills:

1. **A writing-voice skill.** A single file that defines your editorial principles, prohibitions, and formatting conventions. Every writing skill you have reads this first. See the [writing-voice-guide](../writing-voice-guide/) in this repo for a complete process guide on how to build one, including an eight-step workflow and a full skeleton template.
2. **An email-style skill.** An extension of the voice skill that covers email-specific structure: salutation, opening, body, closing, sign-off, formatting for times and dates, and anything to never include. Sketch below.

### Wiring Them Into `analyze-reply`

Once both skills exist, add a prerequisite section near the top of `SKILL.md`:

```markdown
## Prerequisite

Before drafting in Phase 3, read the `[your-voice-skill-name]` skill for core
editorial principles. For the reply draft, also read the
`[your-email-style-skill-name]` skill for email structure and mechanics.
```

Then in **Phase 3**, add at the top:

```markdown
Write the reply using the voice and email conventions loaded from the
prerequisite skills. Apply their editorial principles and structural rules.
```

The existing Phase 3 content layers on top of whatever the voice skill provides.

### A Minimal Email-Style Skill

If you do not need a full style guide, a short file at `~/.claude/skills/your-email-style/SKILL.md` is enough:

```markdown
---
name: your-email-style
description: Email structure, salutation, and closing conventions. Load before
  drafting any email reply.
---

# Email Style

## Structure
1. Salutation: [for example, "Hi [Name]," for colleagues; "Dear [Name]," for formal]
2. Opening: [for example, "Lead with a substantive first line, no pleasantries"]
3. Body: [for example, "Short paragraphs. Bullets for three or more items."]
4. Closing: [for example, "One-line call to action or next step"]
5. Sign-off: [for example, "Thanks," / "Best," / "[Your name]"]

## Formatting Conventions
- Times: [for example, "3pm CT"]
- Dates: [for example, "Thursday, April 23" near-term; "April 23, 2026" future]
- Links: [inline with descriptive text, not bare URLs]

## Never
- [for example, Email signatures, since the client adds them automatically]
- [for example, Follow-up apologies in the opening line]
```

### Training Both Skills on Your Actual Writing

Gut preferences are a reasonable starting point but rarely capture how you actually sound. Your existing writing does. A practical workflow:

1. **Collect a representative sample.** For the voice skill, 3 to 10 longer pieces (memos, blog posts, reports, substantive threads) that sound like you at your best. For the email-style skill, 15 to 30 sent emails across a range of situations (casual and formal, short and long). Pull from your Sent folder and strip recipient names or confidential content if you plan to share or commit the skill.
2. **Extract patterns with an AI.** Paste the sample into a fresh session with a prompt like:

   > Here are [N] pieces of my writing. Please analyze them and extract my voice as a set of editorial principles, structural conventions, word-choice patterns, and things I appear to deliberately avoid. Be specific and cite evidence from the samples. Output as a markdown file suitable for a Claude Code skill.

   For the email-style skill, the prompt is similar but asks for salutation patterns, opening-line conventions, sign-offs, paragraph length, list usage, and formatting for times, dates, and links.
3. **Review and edit the output.** The AI will name patterns you did not consciously notice. Some are real; some are accidents of the particular samples. Keep the rules that match your deliberate preferences, reword or drop the rest. Add a short **Why:** note to each rule so future-you can judge edge cases.
4. **Save as `SKILL.md`** in the skill folder and start using it.
5. **Refine iteratively.** When the assistant drafts something that feels wrong, add a new rule. When the assistant makes a non-obvious choice you like, capture that too, since silent validation drifts away from approaches that actually worked. After 10 to 15 refinements, both skills should capture most of your voice.

The [writing-voice-guide](../writing-voice-guide/) covers the voice-layer side of this in more depth, including a full skeleton template and example integration patterns.

## Design Rationale

**Four claim buckets, not two.** Most fact-checking collapses everything into "true" and "false." That misses where real arguments actually happen: in the framing (opinion) and in the forward-looking or causal claims (speculation). The four buckets force you to see which part of the piece is doing the persuasive work.

**Confidence levels on every claim.** A claim you cannot verify is not the same as a false claim, and treating them the same produces confident-sounding analysis that is quietly wrong. Unverifiable is its own category.

**Phase 1 before Phase 2.** The analysis is independent of whether you reply. Separating them lets you abandon a reply that is not worth sending, or share the analysis with someone else without the draft attached.

**Three tones, not more.** Analytical, validating, and short-and-warm cover most real-world reply situations. Adding more options creates decision fatigue without producing better replies.

**Draft in the user's voice, not the AI's voice.** The skill avoids coaching cliches, flattery, and moral judgments by default. Coupled with a writing-voice layer, the draft should read as a first-draft human reply rather than AI output requiring extensive editing.

**No political defaults.** The skill never signals agreement or disagreement with a political position unless the user explicitly states a view. This matters for analyzing opinion pieces where the political framing is often the most contested part.

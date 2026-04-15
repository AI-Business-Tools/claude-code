# Writing Voice Guide

How to create a consistent writing voice layer that other AI writing skills build on.

---

## Why a Writing Voice Layer

AI writing tools default to a generic professional register: polished, warm, slightly over-explained, and full of phrases like "I hope this finds you well" and "I wanted to reach out." That default is not your voice.

A writing voice layer is a skill file that defines your specific editorial identity and gives the AI a stable foundation to draw from every time it writes in your name. Without it, each writing session starts from scratch. The AI picks up cues from the current conversation, applies them inconsistently, and reverts to defaults when context runs out.

With a voice layer:

- Every email, blog post, and proposal sounds like the same person wrote it.
- Corrections you make once (remove intensifiers, stop apologizing, cut the filler opener) stay corrected across all future writing.
- Format-specific skills (email, blog, proposal) handle structure and mechanics. The voice layer handles how you think on the page.

The voice layer is not a style guide in the traditional sense. It is a set of executable rules the AI can apply to any draft.

---

## What a Voice Layer Contains

A complete voice layer covers five areas:

**1. Core voice description**
A short paragraph that characterizes the overall register: the relationship between writer and reader, the emotional temperature of the writing, and the implicit contract with the audience. Is your writing warm or cool, dense or expansive, confident or tentative? This is the north star the AI returns to when a specific rule does not apply.

**2. Editorial principles**
Named principles that govern how ideas are presented, not just how sentences are formatted. Common principles to define:

- How much you explain vs. how much you trust the reader to infer
- Whether you "sell" your ideas or state them and let them speak
- How you balance confidence with intellectual honesty
- What qualifications are necessary vs. what qualifications are hedging

**3. Tone rules**
Specific behaviors to prohibit or require. These are the most actionable rules in the voice layer because they are binary: the AI either violates them or it does not. Examples of categories to cover (with placeholder content, not prescriptions):

- Opening conventions (what the first sentence must or must not do)
- Warmth conventions (how warmth is expressed, and what false substitutes to avoid)
- Apology and hedging conventions
- Gratitude conventions

**4. Formatting conventions**
Punctuation, capitalization, date and time formats, and other mechanics that appear consistently in your writing. These are the easiest rules to specify precisely and the easiest for an AI to apply reliably.

**5. Notes for the AI executor**
A section written directly to the AI that translates your principles into an operational checklist. The editorial principles section explains your values. This section explains how to act on them: what to do after drafting, what to watch for, and how to handle edge cases.

---

## How to Build Your Own

**Step 1: Audit your existing writing.**
Collect 10 to 20 samples of writing you consider representative of your best work. Include a range of formats: short replies, longer explanations, formal proposals, casual notes. The goal is enough material to see patterns.

**Step 2: Identify what you always do.**
Read the samples looking for consistent choices. What punctuation do you prefer? How do you open messages? How do you express uncertainty? How long are your sentences and paragraphs? Look for habits you did not consciously choose but consistently exhibit.

**Step 3: Identify what you never do.**
Look for things that are absent from your writing. Do you never use intensifiers? Do you never apologize unnecessarily? Do you never start with pleasantries? Prohibitions are often more useful than prescriptions because they are easier to audit.

**Step 4: Identify what you actively dislike in other writing.**
Think about writing you have edited or read and found weak. What did it do that yours does not? This often surfaces principles you hold implicitly but have not named.

**Step 5: Draft named principles.**
Write out the patterns you identified as named rules. Give each principle a short title (two to four words). Titles make principles memorable and give you vocabulary to reference them when correcting the AI.

**Step 6: Write before and after examples.**
For each principle, write one example of writing that violates it and one that follows it. The contrast makes the rule concrete for both you and the AI. Use real sentences from your own writing or corrections you have made to AI output.

**Step 7: Test against new samples.**
Give the AI a writing task using only the voice layer as context. Compare the output to your audit samples. Where the output diverges from your voice, identify which rule is missing or poorly specified and revise.

**Step 8: Iterate.**
A voice layer is a living document. Add rules when you find new failure modes. Tighten rules when the AI finds loopholes. Remove rules that generate false positives (where the rule fires on correct writing and breaks it).

---

## Integration with Other Skills

The voice layer is a foundation, not a standalone tool. It does not know how to structure an email, format a blog post, or organize a proposal. That work belongs to format-specific skills.

The integration pattern is simple: every format-specific writing skill reads the voice layer first, then applies its own structural rules. The voice layer handles how you sound; the format skill handles what goes where.

**Reading order:**

1. Voice layer (always first for any writing in your voice)
2. Format-specific skill (email, blog, proposal, forum reply)
3. Any domain-specific context (course materials, client background, topic notes)

**Practical consequence:** When you update a voice layer rule, the change propagates automatically to every format-specific skill that reads it. You fix a problem once at the foundation and it does not reappear in any format.

**Skills that typically read a voice layer first:**

- Email drafting skills
- Blog and newsletter writing skills
- Consulting proposal and SOW skills
- Forum and comment reply skills
- Any skill that produces writing attributed to a specific person

---

## Example Structure

The following is a skeleton showing how a voice layer SKILL.md should be organized. Replace bracketed placeholder text with your own content.

```markdown
---
name: [your-handle]-writing-voice
description: [Your name]'s writing voice and editorial principles. Foundation layer
  for all writing in [your] voice. Read this skill before any format-specific writing
  skill.
triggers: write in [my] voice, apply [my] voice, [my] writing style
---

# [Your Name] Writing Voice

[One paragraph describing the overall register. Cover the writer-reader relationship,
the emotional temperature, and the core values the writing expresses. This is the
north star for cases where no specific rule applies.]

---

## Core Voice

[Two to four sentences. Direct characterization of voice: what it is and what it is
not. Example dimensions to address: formal vs. casual, warm vs. cool, expansive vs.
dense, assertive vs. tentative.]

---

## Editorial Principles

### [Principle Name 1]

[One paragraph explaining the principle. What does it require? What does it prohibit?
When does it apply?]

**[Your name] writes:** "[Example sentence that follows the principle]"

**Not:** "[Example sentence that violates the principle]"

[One sentence explaining the difference between the two examples.]

### [Principle Name 2]

[Repeat pattern. Aim for four to six principles total.]

---

## Tone Rules

### [Tone Rule Category 1: e.g., Openers]

[State the rule clearly. List specific phrases or patterns to prohibit if applicable.]

### [Tone Rule Category 2: e.g., Warmth]

[State how warmth is expressed in your writing and what false substitutes to avoid.]

### [Tone Rule Category 3: e.g., Hedging and Qualification]

[State what level of qualification is appropriate and what crosses into excessive
hedging.]

---

## Formatting Conventions

### [Convention 1: e.g., Punctuation preference]

[State the rule. Example: "Always use the Oxford comma."]

### [Convention 2: e.g., Time format]

[State the rule with a concrete example: "Use [format]: [example]."]

### [Convention 3: e.g., Date format]

[State the rule.]

### [Convention 4: e.g., Emoji policy]

[State the rule.]

---

## Notes for the AI Executor

When writing as [your name]:

1. **[Checklist item 1]:** [Operational instruction. What should the AI do after
   drafting to check compliance with the principles above?]

2. **[Checklist item 2]:** [Operational instruction. What patterns should the AI
   watch for and remove?]

3. **[Checklist item 3]:** [Operational instruction. What is the default when the
   AI must choose between a longer and shorter version?]

4. **[Checklist item 4]:** [Operational instruction. What is the primary failure
   mode to guard against?]

5. **[Checklist item 5]:** [Operational instruction. How should the AI calibrate
   to the audience's intelligence and background?]
```

---

## Notes on Scope

A voice layer should cover writing principles, not content expertise. It tells the AI how you write, not what you know. Domain knowledge belongs in separate context files or knowledge base entries that skills load alongside the voice layer.

Keep the voice layer focused on rules that apply across all writing contexts. If a rule only applies to one format (for example, a blog post convention that does not belong in email), put it in the format-specific skill instead of the voice layer.

The goal is a voice layer short enough to read in two minutes and precise enough that the AI produces recognizably correct output on the first pass.

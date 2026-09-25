# Skill template

Copy this as the SKILL.md skeleton for a new skill. Replace every `[PLACEHOLDER]`. Delete the conditional sections that do not apply (see `references/house-style.md` section 3 for which apply).

---

```markdown
---
name: [name]
description: [Single flat line. Third person. Name the artifact produced, the trigger conditions in outcome language, and at least one negative trigger naming the skill that should fire instead. Every phrase that must route goes here. A wrong fire costs what a missed fire costs, so buy discrimination with negative triggers, not with length. Target about 400 chars, 500 ceiling, 1536 hard limit.]
when_to_use: [One to three sentences of prose: when to pick this skill, and how it differs from the sibling it is most often confused with.]
allowed-tools: Read, Write, Edit, Glob, Grep, Agent
---

# [Skill Display Name]

[One-sentence purpose.]

[If adapted from third-party material: a one-line provenance and license note.]

## Prerequisite

[Only if the skill produces prose in your voice. Otherwise delete.]
Before drafting any [output type], read the **[your writing-voice skill]** skill for your core editorial and voice principles. That skill governs how you sound on the page. This skill adds [format]-specific structure on top.

## Output contract

- **Produces:** [artifact type, format, destination]
- **Does not produce:** [boundaries]
- **Enables:** [the outcome it serves]
- **Hands off to:** [what consumes the output next]

## Step 1: [First step]

[What the agent does.]
[WHY: the reasoning principle, so the skill generalizes past foreseen cases.]

[Read `references/[file].md` for [what it provides], if used.]

## Step 2: [Human decision point]

Present [three to five] options and wait for a selection before continuing:
- Option A: [description]
- Option B: [description]
- Option C: [description]

## Step 3: [Irreversible action, if any]

**Approval required before proceeding.** Summarize the planned action and ask the user to confirm before executing.

## [Independent quality audit: only if the skill produces rendered or quality-sensitive output]

After producing the output, hand it plus a checklist to an independent agent that applies the checklist and reports defects. The generating agent cannot reliably audit its own output.

Then fix and, where a second round is warranted, re-audit. **The first audit is always full. Everything after it follows these rules, written out here because this template is copied into a new skill:**

- **Scope the re-audit to what changed**, decided mechanically rather than from memory of the edit. **A skill that cannot diff cannot scope:** give it a snapshot at each round start and diff against that, or say plainly that its loop stays full. Name here any check that must stay whole-document, whole-batch, or whole-layout every round.
- **One round is the plan; state a cap.** Run a second round only where the first returned a finding that changes a claim, a number, or a rendered geometry; a finding of wording alone is fixed and shipped. A loop with a human gate at every round needs no cap.
- **The auditor does not spawn sub-agents.** One agent reads what the brief names. A brief wide enough to need fanning out is too wide. If this skill's audit is deliberately multi-agent, say so here, because callers inherit it.
- **Put a cheap deterministic check in front** and tell the agent what it already covers.
- **Fix with targeted edits, never a whole-file rewrite**, because the rewrite is what generates the next round's findings. A rewrite that replaces audited text re-triggers the audit for the text that changed, and that run does not count against the round limit.

**Escalate back to a full pass** when the output was restructured rather than corrected, or when a fix adds content rather than removing it. That run does not count against the cap.

## Gotchas

[Recommended, not required. At least two entries, each grounded in a real or predicted failure.]
- **Symptom:** [what is seen when this fails]. **Cause:** [one line]. **Fix:** [what to do instead].
- **Symptom:** [...]. **Cause:** [...]. **Fix:** [...].

## Rules

- [Rule from predicted failure mode]
- [Rule from predicted failure mode]
- Never proceed past an irreversible action without explicit approval.
- For an execute step, invoke the script in scripts/; do not improvise inline code.

## Session Log

[Only if the skill does project-folder work. Otherwise delete.]
After substantive work, append a session log entry to `CLAUDE.local.md` in the working directory per [your session-log protocol]. Offer a handoff only when the session involved multiple rounds of iteration.
```

---

## Directory layout

```
[name]/
├── SKILL.md
├── references/
│   └── [topic].md      # one level deep; over 100 lines starts with a table of contents
├── scripts/            # only genuinely mechanical steps; start from scripts/archetypes/
└── assets/             # templates and examples
```

Recommended but optional: a small `evals/evals.json` with three or more cases, each a prompt plus a verifiable assertion. The independent audit-agent gate is the primary quality mechanism, so this is an offer, not a requirement.

For a session-log format, the handoff and resume protocol published alongside this skill (`handoff-resume/` in the same repository) defines one.

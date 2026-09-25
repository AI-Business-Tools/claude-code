# Skill design framework

The design principles for building a skill. Load during Phase 2 (design). For the house-style mechanics (frontmatter fields, conditional sections, routing), use `references/house-style.md`; this file covers the design judgment.

Adapted from `skill-engineer-master` by Antony Evans (edge-brain-lite, https://github.com/antonyevans/edge-brain-lite, CC BY 4.0). Modified: removed the public-marketplace prior-art search, the librarian domain-research and eval-rubric phases, and the Active-vs-Library tier model; replaced marketplace search with a survey of your own skill suite; demoted the always-mandatory evals, Gotchas, learnings, and edge-cases requirements to recommendations.

## Table of contents
1. Survey first
2. Naming
3. Description (the highest-leverage element)
4. Progressive disclosure
5. Process-step design
6. Human-in-the-loop
7. Reason vs execute (ship scripts)
8. Quality gate: the independent audit agent
9. Anti-patterns
10. Skill debt and deletion

---

## 1. Survey first

Before designing, survey `~/.claude/skills/` (and your skill index, if you keep one) for an existing or overlapping skill. If one exists, extend it instead of building a new skill. A near-duplicate drifts from its twin and creates routing ambiguity. This is the cheapest possible design decision: the skill not built.

## 2. Naming

- 1 to 64 characters, lowercase letters, numbers, and hyphens only.
- Matches the parent directory exactly.
- Follow your suite's naming convention, if it has one (a shared prefix, for example); `references/house-style.md` records it. `<verb>-<noun>` or `<noun>` both read well (`skill-audit`, `diagram`).
- Avoid vague names (`helper`, `utils`, `tools`).
- Check for trigger collisions against the existing suite before committing to a name.

## 3. Description (the highest-leverage element)

The description is the only text read before the skill fires, and it is a routing signal for the agent, not a label for a human. Invest most of the design effort here, and draft it with a prompt-writing step.

- Single flat line, never YAML folded. A wrapped description is read only to its first line, and the skill misfires.
- Third person. Name the artifact produced. State trigger conditions in outcome language. Include at least one negative trigger.
- Every phrase that must route goes in the description. A `triggers:` frontmatter key is never read by Claude Code, so a phrase that lives only there does nothing at fire time. Use `when_to_use` for one to three sentences of prose on when to pick this skill over its nearest sibling.
- Weigh over-firing against under-firing. In a suite with several skills that produce similar artifacts, a wrong fire costs what a missed fire costs: a deck builder claiming a request meant for a sibling that files the source first does not produce a near miss, it produces the wrong deliverable in the wrong place. Buy discrimination with negative triggers, not with length.
- Target about 400 characters; 500 is the working ceiling and 1536 the hard limit, where the skill listing truncates silently.

## 4. Progressive disclosure

Skills load in layers, so only what is needed reaches the context window:
- Frontmatter (name, description, when_to_use): always loaded.
- SKILL.md body: loaded on trigger. Keep it a routing layer of steps and pointers, under 500 lines and ideally under 150.
- Reference files: loaded on demand when SKILL.md points to them. One level deep, never chained. Files over 100 lines start with a table of contents.

Every line in SKILL.md costs tokens on every invocation. Push dense rules, templates, and domain knowledge into references.

## 5. Process-step design

Write steps for agent execution, but include the reasoning, not just the procedure. Linear step lists break on cases you did not foresee; the principle behind a step lets the skill generalize.

- Numbered steps with explicit decision points.
- Third-person imperative ("Extract the...", not "I will..." or "You should...").
- State the why alongside the what.
- One word per concept throughout; never vary the term for the same thing.
- For choices, give one default and at most one named fallback.

## 6. Human-in-the-loop

- At each human decision point, produce multiple options (typically three to five), not a single output. This is the highest-impact interaction design choice: it turns autocomplete into co-creation.
- Any irreversible action (send, publish, delete, pay, modify shared state) gets an explicit approval gate before it runs. Never auto-proceed past one.
- Define each handoff: the artifact passed, the check that proves it is correct, and the recovery path if it is wrong.

## 7. Reason vs execute (ship scripts)

For every step, decide whether the agent reasons (weighs context, judges, produces options) or executes (runs a deterministic operation). Ship a script for every execute step. A step is an execute step if any of these hold:
- it makes an HTTP or API call,
- it reads, writes, or transforms a file in a repeatable format,
- it loops over more than about three items,
- it produces an exactly-formatted output (JSON, CSV, a specific markdown schema),
- it touches credentials, secrets, or environment-dependent paths,
- it validates or scores against a schema or rubric, or
- it logs, appends to, or consolidates a state file.

Prose is correct only when the step produces a judgment, generates options for a human, composes reasoning across context a script cannot access, or is genuinely one-shot. Default to a script and argue your way to prose.

Start every script from an archetype in `scripts/archetypes/` (`fetch_and_cache.py`, `validate_output.py`, `log_run.py`, `pick_from_options.py`, `search_and_rank.py`); copy the closest and adapt. Prefer small single-purpose scripts that chain over a monolithic runner. Error messages name the symptom, the cause, and the next action. Document every config constant inline. In an unattended or headless skill, write file operations as literal-path calls, never loops or variable-expanded globs, which trigger fresh permission prompts that stall the run; and adapt `pick_from_options.py` to use AskUserQuestion.

## 8. Quality gate: the independent audit agent

For a skill that produces rendered or quality-sensitive output, the quality mechanism is an independent audit agent, not an evals folder. After the output is produced, hand it plus a checklist to a separate agent that applies the checklist and reports defects, then fix and re-audit. The generating agent cannot reliably audit its own output; it sees what it intended, not what rendered. A skill that says launch an agent must launch one, never self-inspect.

**Design the loop, not just the first pass.** The design decision it forces is what this skill can diff.
- The first audit is always full.
- A re-audit is scoped to what changed **by a mechanism the skill actually has**. A skill with nothing to diff either gains a snapshot at each round start or states that its loop stays full.
- A second round needs a finding that changes a claim, a number, or a rendered geometry. A finding of wording alone is fixed and shipped.
- The auditor does not spawn sub-agents unless the skill says its audit is deliberately multi-agent, because callers inherit that.

Decide all of this when the step is written. A loop specified as "re-audit up to a round cap" and nothing more re-reads the whole deliverable every round, which is expensive and rarely finds anything the first round missed.

A small `evals/evals.json` and a `## Gotchas` section are good complements and worth offering, but they are recommendations, not requirements; the audit-agent gate is the primary quality mechanism.

## 9. Anti-patterns

- Domain knowledge embedded in SKILL.md instead of a reference file.
- Nested reference chains; partial reads miss the content.
- Five or more options with no default.
- Time-sensitive conditionals ("Before version X, do Y"); use an `## Old patterns` section instead.
- A first-person, vague, or timid description; it causes undertriggering and discovery failures.
- A multi-line or YAML-folded description; only the first line is read.
- Trigger phrases kept only in a `triggers:` key, which Claude Code never reads.
- Steps with no reasoning principle; they break on unforeseen cases.
- Prose for an execute step; the agent improvises differently every run.
- A CHANGELOG.md in the skill root (a README.md is fine in a published copy, where it documents the skill for people; Claude Code does not read it).
- The same agent implementing and self-certifying quality-sensitive output.

## 10. Skill debt and deletion

Every skill is a maintenance obligation. When a workflow changes materially, rewrite the skill from the design rather than patching. A skill that needs more than two or three fixes in a week has drifted from its design; rebuild from Phase 1. Deletion is a valid outcome: a retired workflow should have its skill removed, not left to misroute.

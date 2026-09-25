# Skill Build

Design and build a new Claude Code skill from a blank page, in the house style your existing skills already follow, and check it with a preflight script before it ships.

## Problem

Asking Claude to "make a skill for X" usually produces something that works once and fits nothing. The description is too vague to fire reliably, or so broad it steals requests from a neighboring skill. Trigger phrases end up in a frontmatter key Claude Code never reads. Mechanical steps are written as prose, so the agent improvises them differently on every run. And the new skill looks nothing like the rest of your suite: no session log where your other skills keep one, no independent quality check where your other skills run one.

The cost shows up later, as a skill that never fires, a near-duplicate that drifts from its twin, or a deliverable nobody checked.

## Approach

The skill treats building a skill as a design problem with an approval gate, not a writing task. It surveys what you already have before designing anything, because the cheapest skill is the one not built. It presents the full design (identity, output contract, steps with their reasoning, a script inventory, and which optional sections apply) and builds nothing until you approve.

It works from your conventions, not a generic template. `references/house-style.md` ships as a template: on first use, the builder reads a few of your existing skills and records how they are built (frontmatter, section headings, when a skill gets a session log or an audit step, how you name things). Every later build follows that record, so new skills match old ones.

Validation is split in two. A script checks what can be checked mechanically, and a checklist covers the judgment calls a script cannot make.

## The Flow

1. **Survey the suite.** Look for an existing skill that already covers the request, and recommend extending it if one does. On the first run, fill in the house-style template from your own skills.
2. **Intake.** Ask only the questions whose answers change the design: the task, what should and should not trigger it, tools, human decision points, output, how Claude fails at the task today, and whether to pin a model.
3. **Design, then wait.** Present the name, description, output contract, steps, script inventory, and applicable sections. Nothing is written until you approve.
4. **Build.** Generate the folder from `assets/skill-template.md`, keeping SKILL.md a routing layer and pushing dense material into reference files. Every mechanical step gets a script, started from one of the bundled archetypes.
5. **Validate.** Run `scripts/preflight.py` and fix every hard fail, then apply `references/preflight-checklist.md`.
6. **Register.** Most skills need nothing here, because the description is the routing signal. If you keep a skill index or a routing table in your CLAUDE.md, the builder drafts the change and waits for approval before touching either.
7. **Test and hand off.** A cold-start test plan for a fresh session, then an offer to hand the skill to [`skill-audit`](../skill-audit/) once it has been used.

## Usage

Ask for it in your own words: "build a skill", "create a skill for...", "make a new skill", "scaffold a skill", "engineer a skill".

**Good uses**
- A workflow you repeat often enough that Claude should follow the same steps every time
- A task Claude gets wrong in a consistent way that a written procedure would fix
- A multi-step job with mechanical steps that belong in scripts

**Not good uses**
- Editing or auditing an existing skill (edit it directly, or use [`skill-audit`](../skill-audit/))
- Publishing or sharing a skill
- Writing a one-off prompt or an agent brief

**Tips**
- Let the first run fill in `references/house-style.md` properly. Point it at the skills you consider best built, including at least one that writes prose, one that transforms files, and one that only advises.
- If your suite uses a shared name prefix, set `REQUIRED_NAME_PREFIX` near the top of `scripts/preflight.py` so a new skill without it is flagged.
- Expect the builder to recommend extending an existing skill sometimes. That is the survey working.

## Installation

This skill needs more than one file. Copy the whole folder to `~/.claude/skills/skill-build/`:

```
~/.claude/skills/skill-build/
  SKILL.md
  references/skill-design-framework.md
  references/house-style.md
  references/preflight-checklist.md
  assets/skill-template.md
  scripts/preflight.py
  scripts/archetypes/README.md
  scripts/archetypes/fetch_and_cache.py
  scripts/archetypes/log_run.py
  scripts/archetypes/pick_from_options.py
  scripts/archetypes/search_and_rank.py
  scripts/archetypes/validate_output.py
```

This file, `README.md`, is documentation for you rather than something the skill reads, so copying it alongside is optional. The preflight script needs only Python 3 and its standard library. The archetypes are templates to copy into new skills; two of them name optional packages (`requests`, `jsonschema`) that only a skill built from them needs. Restart Claude Code after copying.

Two related pieces are optional. For a skill that writes in your voice, the builder adds a prerequisite that reads your writing-voice skill; if you do not have one, the [`writing-voice-guide`](../writing-voice-guide/) explains how to build one. For a skill that keeps a project session log, the [`handoff-resume`](../handoff-resume/) protocol defines one format.

## Output

- A new skill folder at `~/.claude/skills/<name>/`: SKILL.md, plus `references/`, `scripts/`, and `assets/` where the design calls for them
- A preflight report printed to the terminal, listing hard fails, warnings, and passes
- On the first run, a filled-in `references/house-style.md` recording your conventions
- Where you keep them, drafted (not applied) changes to your skill index and CLAUDE.md routing table, applied only on approval

## Design Rationale

**Survey before design.** A near-duplicate skill drifts from its twin and makes routing ambiguous. Checking the existing suite first is the cheapest decision in the process.

**The description gets most of the effort.** It is the only text Claude reads before deciding whether to load a skill. Trigger phrases belong there, not in a custom frontmatter key Claude Code ignores. A wrong fire costs as much as a missed one, so the builder buys precision with negative triggers ("Not X") rather than with length.

**Conventions are recorded, not guessed.** The house-style file is a template the first run fills in from your own skills. Inferring conventions fresh on every build produces skills that each look slightly different.

**Mechanical steps ship as scripts.** Anything that calls an API, loops over many items, produces an exact format, or validates against a schema is a script, because prose for a deterministic step gets improvised differently every run. The archetypes cover the hard parts (retries, caching, crash-safe appends, structured choices) so a new script does not start from a blank file.

**Quality comes from an independent audit agent, not self-review.** For a skill whose output is rendered or quality-sensitive, the design adds a step where a separate agent checks the output against a checklist. The agent that produced the output sees what it intended, not what it made. The audit loop is designed up front, including what a re-audit is scoped to and when a second round is justified, so it does not re-read the whole deliverable every round.

**The preflight is strict only where it has to be.** It hard-fails on what stops a skill from loading or being read (a folded description, a name that does not match its folder, a description past the listing's truncation point). Everything that is a convention rather than a requirement, such as a Gotchas section or a line-count target, is a warning.

**Approval gates sit before writes to shared context.** The builder never writes skill files before the design is approved and never edits CLAUDE.md without showing the diff first, because both affect every later session.

**No real clients or private people, anywhere.** Examples, fixtures, and test data are fictitious. The rule names the ways it usually breaks: a fixture built from a real delivered file, or a rule explained by naming the engagement that prompted it.

## Acknowledgments

The Skill Build skill is adapted from `skill-engineer-master` by **Antony Evans**, part of edge-brain-lite, licensed CC BY 4.0. The preflight script and the five script archetypes derive from the same work.

- [GitHub](https://github.com/antonyevans/edge-brain-lite)

This version is decoupled from the edge-brain research and persistence layer and the public skill marketplaces, re-targeted to a house style recorded from your own skills, and demotes the original's mandatory evals, Gotchas, learnings, and edge-cases files to recommendations.

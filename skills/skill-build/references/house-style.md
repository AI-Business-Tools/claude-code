# Skill house style (template)

How your skills are actually built. This file is the re-targeting layer: it replaces a generic skill template with the conventions your own suite already follows. Load it during Phase 2 (design) and Phase 3 (build).

**It ships as a template.** The first time the builder runs, Phase 0 fills it in: read three to five of your existing skills (pick ones you consider well built, and at least one of each kind you write: a prose producer, a file transformer, an advisory skill) and record their conventions under the headings below, replacing each "Record here" prompt with what you found. Keep the general guidance; it applies whatever your conventions are. If you have no existing skills yet, keep the defaults stated in each section and revise them after your first few builds.

Why record instead of infer on every build: a convention inferred fresh each time drifts from build to build, and a skill built from the generic template looks and behaves unlike the rest of your suite.

## Table of contents
1. Frontmatter fields and order
2. The description (the routing signal)
3. Conditional sections by skill type
4. The writing-voice prerequisite
5. Writing standards (apply to every skill and its output)
6. File and folder conventions
7. Routing registration checklist
8. Preflight invariants (HARD vs WARN)
9. Skills that touch project folders

---

## 1. Frontmatter fields and order

Claude Code recognizes these frontmatter keys: `name`, `description`, `when_to_use`, `model`, `allowed-tools`, `argument-hint`, and `effort`, plus invocation-control keys such as `disable-model-invocation` (check the Claude Code documentation for your version). Any other key is ignored. Only `name` and `description` are required.

The default this builder emits, in order:

```yaml
---
name: <name>                    # lowercase, hyphens, matches the directory exactly
description: <single flat line>  # see section 2; the highest-leverage field
when_to_use: <one to three sentences of prose>   # when to pick this skill, and how it differs from its nearest sibling
allowed-tools: Read, Write, Edit, Glob, Grep, Agent   # scope to what the skill needs
# model: sonnet                 # optional; omit to inherit the session model (the default)
# effort: high                  # optional; pairs with model
argument-hint: [what to pass]   # optional; for skills that take an argument
---
```

- **`name`:** 1 to 64 characters, lowercase letters, numbers, and hyphens only, no underscores, and it must match the directory name exactly.
- **`when_to_use`:** prose, not a phrase list. Its main value is the distinction from a sibling the skill is commonly confused with.
- **No `triggers:` key.** Claude Code never reads it, so a phrase that lives only there does nothing at fire time. Every phrase that must route belongs in `description`. If your own tooling (a skill index generator, for example) reads a custom key, it may stay for that tooling, but record that nothing routes from it.
- **`description` quoting:** leave it bare unless you have a reason. An unquoted description containing a colon followed by a space has loaded correctly in testing, and an always-quote rule forces the doubled-apostrophe form (`user''s`) on every description with an apostrophe, which is its own way to break the block. If a skill ever stops appearing in the skill listing at all, check quoting first.
- **`model` / `effort`:** optional and ask-once. The default is to omit them and inherit the session model.
- **`allowed-tools`:** emit a scoped list by default (good practice), but its absence is not a defect.

**Record here:** which of these keys your skills actually carry, in what order, and any custom keys your own tooling reads (and what reads them). Note which skills pin `model` or `effort`, and why, so the builder can tell a deliberate pin from habit. *Why it matters:* a new skill whose frontmatter differs from its siblings is harder to scan, and a custom key someone believes routes is a silent failure.

## 2. The description (the routing signal)

The description is the only thing read before the skill fires. It is a routing signal for the agent, not a label for a human. Invest most of the design effort here, and draft it with a prompt-writing step.

- It must stay on a **single flat line**. If a formatter wraps it onto two lines, Claude reads only the first line and the skill misfires. Never use YAML folded syntax (`description: >`).
- Third person ("Generates...", "Audits..."), not "I can..." or "You can...".
- Name the **specific artifact** the skill produces.
- State the **trigger conditions** in the outcome language an agent would have in its goal.
- State at least one **negative trigger** (when NOT to fire), usually cross-referencing the skill that should fire instead.
- **Weigh over-firing against under-firing; do not assume undertriggering is the only failure.** In a suite with several skills that produce similar artifacts, a wrong fire costs what a missed fire costs. Buy discrimination with negative triggers, not with length.
- **Length:** target about 400 characters, 500 as a working ceiling, 1536 as the hard limit. 1536 is Claude Code's default skill-listing description limit, past which the listing truncates the description silently and with no error; it is the point where text stops being read, not an allowance. Over 500, either cut it or record why the length is needed in the Phase 2 design summary.

**Record here:** the negative-trigger form your descriptions use (for example "Not X", or "Does NOT fire for X"), so new skills match it and the preflight's negative-trigger detection recognizes it. *Why it matters:* a consistent form is easier to audit across the suite.

## 3. Conditional sections by skill type

Apply the sections that match the skill being built.

- **Session log** (skill does project-folder work that should leave a record): add a `## Session Log` section that appends a short entry (date, skill, a one-line summary, status) to the project's session log after substantive work, and offers a handoff only when the session involved multiple rounds. One published format for that log is the handoff and resume protocol in [`../handoff-resume/`](../../handoff-resume/).
- **Independent audit agent** (skill produces rendered or quality-sensitive output): add a step that hands the output to an independent agent which applies a checklist and reports defects, then a fix-and-re-audit loop. Use it in place of an `evals/` folder. The generating agent cannot reliably audit its own output, and a skill that says launch an agent must launch one, never self-inspect. **The loop's shape:** the first audit is full; a re-audit is scoped to what changed, by a mechanism the skill actually has; a second round needs a finding that changes a claim, a number, or a geometry; and the auditor does not spawn sub-agents. A skill that cannot diff says its loop stays full rather than claiming a scope it cannot compute. `assets/skill-template.md` carries the full rule list for pasting.
- **Writing-voice prerequisite** (skill produces prose in your voice: emails, posts, proposals, summaries, analyses, slide content): add the prerequisite fragment in section 4.
- **Report-only contract** (advisory skill that recommends but should not edit): state plainly that the skill proposes and never edits, and omit Edit and Write from `allowed-tools`. The published [`skill-audit`](../../skill-audit/) is an example.

**Record here:** for each section, which of your existing skills carry it, the exact heading they use, and any wording they share. *Why it matters:* these are what make a new skill behave like the rest of your suite, and they are the sections a generic template omits.

### Shorthand-triggered skills

A skill you fire with a short token (for example `ho` for a handoff) needs a trigger definition in `~/.claude/CLAUDE.md`, not just skill frontmatter, because a two-letter token does not match any description. Use the leanest form that works: a single routing-table row stating the token, any selector grammar, and the complete-message rule ("only as a complete message, never the letters inside a sentence"). Keep the full spec in the skill's SKILL.md; duplicating it into always-loaded context is the anti-pattern.

**Never set `disable-model-invocation: true` on a shorthand-triggered skill.** It removes the skill from Claude's context entirely, so a typed shorthand can never reach it and the trigger silently does nothing; the only way in becomes the full slash command. If the concern is that a skill must not fire on Claude's own judgment, the mechanism is the complete-message rule plus an in-skill approval gate, not the frontmatter field.

**Record here:** the tokens you already use, so a new one does not collide.

Recommended but not required (offer, do not force): a `## Gotchas` section with at least two real symptom, cause, and fix entries, and a small `evals/evals.json`.

## 4. The writing-voice prerequisite

For any skill that produces prose in your voice, place a prerequisite section directly under the H1 that reads your writing-voice skill before drafting. If you do not have one yet, create it first: the [`writing-voice-guide`](../../writing-voice-guide/) explains how to build a voice layer from your own prior writing. A default fragment:

```markdown
## Prerequisite

Before drafting any [output type], read the **[your writing-voice skill]** skill for your core editorial and voice principles. That skill governs how you sound on the page. This skill adds [format]-specific structure on top.
```

When the output is an email, chain your email-style skill after the voice skill, if you keep one.

**Record here:** the name of your voice skill, any format-specific skills that chain after it, and the exact prerequisite wording your skills use. *Why it matters:* the voice layer is the one place corrections to your writing accumulate; a prose skill that skips it undoes them.

## 5. Writing standards (apply to every skill and its output)

General guidance that holds in any suite:

- **Descriptive, factual headings.** No intensifiers, superlatives, or urgency.
- **Never write a derived fact as a literal.** A count of a list, a position in one ("the last four are..."), or a tally of what uses a thing is derived from something that changes, and the written number does not change with it. Name the list, not its length. A number stays only where it is the rule itself: a cap, a floor, or a required quantity.

**Record here:** the standards from your global CLAUDE.md or voice skill that apply to skill files and to what they generate: punctuation rules (Oxford comma, dashes), citation format, affirmation openers, and anything specific to slides or emails. Note whether skill files themselves are held to the same standard as the deliverables they produce, or treated as internal content with looser rules. *Why it matters:* a skill passes its standards on to every output, so a gap here repeats in every run.

## 6. File and folder conventions

```
<name>/
├── SKILL.md                  # routing layer: steps and pointers, under 500 lines, ideally under 150
├── references/               # one level deep only; dense rules, templates, domain knowledge
│   └── <topic>.md            # files over 100 lines start with a table of contents
├── scripts/                  # only genuinely mechanical steps; start from scripts/archetypes/
└── assets/                   # templates and examples
```

- References are one level deep; never chain `references/a.md -> references/b.md`.
- No CHANGELOG.md in the skill root. A README.md is not read by Claude Code; it is fine in a published copy, where it documents the skill for people.
- Forward slashes in all paths. MCP tools always in fully-qualified `ServerName:tool_name` form.
- In an unattended or headless skill, write file operations as literal-path calls, never loops or variable-expanded globs, which trigger fresh permission prompts that stall the run.

**Record here:** your naming convention (a shared prefix, verb-noun order), where shared references used by several skills live (for example a `~/.claude/skills/references/` folder), and where build or output folders go. *Why it matters:* a shared reference restated inside one skill drifts from the original.

## 7. Routing registration checklist

A new skill is discoverable through its description alone. The items below apply only if you keep them, and any edit to `~/.claude/CLAUDE.md` touches always-loaded context, so it goes through the Phase 5 approval gate (present the diffs, wait, then apply):

- [ ] **Skill index, if you keep one.** If it is generated from frontmatter, set the field the generator reads and regenerate; never hand-edit a generated index, because the next regeneration wipes a hand-added row. If it is maintained by hand, add the row.
- [ ] **Routing row, if you keep a routing table in your CLAUDE.md:** only for what the description cannot carry (a command word you type, a tie-break, a default). Most skills need none.
- [ ] **Headless variant** only if the skill is batch-run.

**Record here:** whether you keep an index or a routing table, where each lives, and how each is updated. *Why it matters:* this is the step most often skipped, and a skill nobody can find is a skill that does not exist.

## 8. Preflight invariants (HARD vs WARN)

What `scripts/preflight.py` enforces.

**HARD fail (must fix):**
- SKILL.md exists and is at most 500 lines.
- Frontmatter has `name` and `description`.
- `name` matches the directory name and is lowercase letters, numbers, and hyphens, at most 64 characters.
- `description` is a single flat line (not YAML folded) and at most 1536 characters.
- No nested reference chains under `references/`.
- No CHANGELOG.md in the skill root.

**WARN (review, not a blocker):**
- Description over 500 characters.
- Description starts with "I" or "You", or contains no negative trigger.
- No `when_to_use`.
- A `triggers:` or `category:` key, which Claude Code does not read.
- SKILL.md over 150 lines.
- No `## Gotchas` section.
- A README.md in the skill root.
- A name without the required prefix, only if you set `REQUIRED_NAME_PREFIX` in the script (off by default).

**Record here:** if your suite uses a shared name prefix, set `REQUIRED_NAME_PREFIX` in `scripts/preflight.py` and note it here.

## 9. Skills that touch project folders

For any skill that creates, populates, or writes rules into a project folder:

- **Keep one standard for what a project folder contains, and point at it; never restate it.** A restated copy drifts from the original and then contradicts it.
- **A skill that stands up a project folder creates it to that standard.** Check the standard rather than copying whichever existing skill is nearest, since two skills that both stand up folders can disagree.
- **Writing project conventions into a SKILL.md silently makes that skill the project's standards home.** That turns an ordinary convention edit into a skill edit, and it lands in every folder that runs the skill. Decide that placement deliberately; do not arrive at it by adding one convenient rule.
- **A guardrail whose only home is a skill file is invisible to any session in that folder that does not invoke the skill.** So the design names the one sentence the project's own `CLAUDE.md` needs, and leaves the rest in the skill.

**Record here:** where your project-folder standard lives, if you keep one.

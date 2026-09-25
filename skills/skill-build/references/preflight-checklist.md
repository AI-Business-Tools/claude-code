# Skill preflight checklist (semantic)

The judgment checks the preflight script cannot make. Run after `scripts/preflight.py` passes, before handing the skill to `skill-audit`. Fix gaps immediately.

## Discovery and routing
- [ ] The description names the specific artifact the skill produces.
- [ ] The description states trigger conditions in the outcome language an agent would have in its goal.
- [ ] The description includes at least one negative trigger, usually naming the skill that should fire instead.
- [ ] The description is neither timid nor greedy: name the case it should lose to a neighboring skill, and check that a request belonging to that neighbor would not match this description. In a large suite, a wrong fire costs what a missed fire costs.
- [ ] The description is around 400 characters, at most 500 unless the length is justified in the Phase 2 design summary, and never over 1536, where the listing truncates it silently.
- [ ] Every phrase that must route appears in the description. No routing phrase lives only in a `triggers:` key, which Claude Code never reads.
- [ ] `when_to_use` is one to three sentences of prose and says how this skill differs from the sibling it is most likely to be confused with.
- [ ] The name has no trigger collision with an existing skill in the suite.

## Structure
- [ ] SKILL.md is a routing layer: steps and pointers, with dense material in references.
- [ ] Reference files are one level deep; files over 100 lines open with a table of contents.
- [ ] Terminology is consistent: one word per concept throughout.
- [ ] Steps carry their reasoning principle, not only the procedure.
- [ ] Where choices exist, one default is given with at most one named fallback.
- [ ] No time-sensitive conditionals; old behavior, if any, sits in an `## Old patterns` section.

## Output contract
- [ ] What the skill produces is stated (artifact type, format, destination).
- [ ] What the skill does NOT produce is stated.
- [ ] For an agent-called skill, the contract states what goal it enables and what consumes the output.

## House-style sections (apply the ones that fit)
- [ ] Session log section present if the skill does project-folder work.
- [ ] Independent audit agent step present if the skill produces rendered or quality-sensitive output, with the loop's re-audit scope and round cap stated.
- [ ] Writing-voice prerequisite present if the skill produces prose in your voice.
- [ ] Report-only contract stated, and Edit and Write omitted from `allowed-tools`, if the skill is advisory.

## Human-in-the-loop
- [ ] Human decision points produce multiple options (three to five), not a single output.
- [ ] Every irreversible action (send, publish, delete, pay, modify shared state) has an explicit approval gate.
- [ ] Each handoff defines the artifact passed, the verification check, and the recovery path.

## Scripts (if any)
- [ ] Every execute step from the inventory has a script; any execute-looking step left as prose is justified in one sentence.
- [ ] Scripts started from an archetype, are single-purpose, and chain rather than forming a monolith.
- [ ] Error messages tell the agent what to try next.
- [ ] Every config constant has an inline rationale comment.
- [ ] Each script's docstring states purpose, usage, stdout format, and error taxonomy.
- [ ] SKILL.md says whether to execute or read each script.
- [ ] In an unattended or headless skill, file operations use literal-path calls.

## Writing standards
- [ ] The skill follows the writing standards recorded in `references/house-style.md` section 5.
- [ ] Headings are descriptive and factual, with no intensifiers or urgency.
- [ ] No fixture, example, comment, or stated provenance names a real client or a real private person.

## Readiness
- [ ] Routing registration drafted for Phase 5, pending approval, where it applies: if you keep a generated skill index, the frontmatter field it reads is set so a regeneration picks the skill up (the index itself is never hand-edited); if you keep a routing table in your CLAUDE.md, a row is drafted only for what the description cannot carry.
- [ ] A cold-start test plan is prepared: a fresh session (one that did not build the skill) runs it on two or three real tasks.
- [ ] If the skill was adapted from third-party material, the license attribution (for example CC BY 4.0) is carried into the skill.

---
name: skill-audit
description: Audit recent Claude Code session transcripts for recurring friction (repeated corrections, routing misfires, repeated reprompts, enforcement gaps, post-upgrade regressions) and recommend conservative changes to your personal skills, CLAUDE.md, protocols, or settings. Report-only: it proposes, it never edits. Prefers no change. Triggers on "skill audit", "audit my skills", "audit recent sessions".
triggers: skill audit, audit my skills, audit recent sessions, audit skills, skill opportunities, audit recent work
allowed-tools: Bash, Read, Glob, Grep, Agent
model: sonnet
argument-hint: [days, default 7]
---

# Skill Audit

Audit recent Claude Code session transcripts for recurring friction and recommend conservative changes to your personal configuration. This skill **proposes only; it never edits anything** (it has no Edit or Write tool). Prefer no change. "Recommend nothing" is a valid and common result.

## Argument
- No argument: scan the last **7 days**.
- A number: scan that many days (for example, `14`).

## Model
Runs on a mid-tier model by default, which is sufficient given the report-only design and the mandatory verification step below. For the run right after a model upgrade, when catching regressions is the point, invoke under the strongest available model.

## Report-only contract
This skill reads transcripts and configuration and produces a report. It does not change any file. After you rule on the findings, the actual edits and the two log updates (below) are made as a separate, deliberate step outside this skill.

## State files (in this skill's folder)
- `declined.md`: findings you have ruled "do not pursue." **Read this first, every run.** Do not re-recommend a matching item. If the friction still recurs, note it as "previously declined, still occurring," without re-proposing the fix.
- `changes.md`: the ledger of changes prior audits have driven. **Read this too.** Do not re-flag something already fixed; if it recurs despite a fix, say so, because the fix may not have held.

Both files start empty. Create them on the first run if they do not exist.

## Procedure

### Phase 0: Read state
Read `declined.md` and `changes.md` in this skill's folder so the run knows what has been declined and what has already been fixed.

### Phase 1: Enumerate transcripts
Session transcripts are JSONL files under `~/.claude/projects/<encoded-project-dir>/`. List the ones in the window:
```bash
find ~/.claude/projects -maxdepth 2 -name "*.jsonl" -mtime -<days> -type f -printf '%TY-%Tm-%Td %10s %p\n' | sort -r
```
Scan **top-level** session files. Files under a `/subagents/` subfolder are internal agent transcripts and low signal; skip them unless a main thread points at one. **Skip the current active session's own transcript** to avoid self-reference. Group the files by their project directory and gauge total volume.

### Phase 2: Extract and scan
If the volume is small (a few small files), read and scan directly. If it is large (several files, or more than a few MB), **fan out one read-only subagent per project cluster**: merge directories that hold only tiny stubs, and split any single directory whose files exceed about 15 MB across two agents. Give each agent the friction schema below and this extraction recipe:
```bash
# human-authored turns only; sample `head -1 <file> | jq 'keys'` first and adapt the jq path
jq -rc 'select(.type=="user") | (.message.content // .content) | if type=="string" then . else (map(select(.type?=="text")|.text)|join("\n")) end' <file> 2>/dev/null
```
Ignore noise: tool results, and lines beginning with `<command-`, `<system-reminder`, `<local-command`, `Caveat:`, or `[Request interrupted`. Also grep skill invocations and permission denials to assess routing. Each agent returns structured findings with verbatim user quotes (under about 25 words each), tagged with the file basename.

### Phase 3: Synthesize
Pool the findings. The strongest signal is friction that **recurs across multiple sessions or clusters**. Dedup, rank by evidence, and drop one-offs. A single unusual correction is noise, not a skill opportunity.

### Phase 4: Verify before recommending (mandatory)
For every candidate fix, open the relevant skill, CLAUDE.md, protocol, or settings file and confirm the current state **before** proposing anything. Decide which case each finding is:
- The rule does not exist: a genuine gap; an edit may help.
- The rule already exists but was not followed: an **adherence or enforcement gap**, not a content edit. Do not propose re-adding a rule that is already there.
- The plumbing is broken or misconfigured (wrong path, stale config): a config fix.

This step is what keeps the audit from manufacturing busywork. Skipping it is not allowed.

### Phase 5: Filter against declined.md and changes.md
Remove from the recommendation list anything matching a `declined.md` entry (note the recurrence instead) or already fixed per `changes.md` (note if it recurred anyway).

### Phase 6: Report and stop
Present a ranked report. For each finding: title, type, frequency (which sessions, by file basename), one to three verbatim evidence quotes, the active skill if any, the recommended action class, and confidence. Cap the recommendations: at most one or two new-skill ideas and a short list of updates per run; if a run wants more, say what was held back. End by asking which to act on. **Do not edit anything.**

### Post-report (outside this skill, after you rule)
- For each finding you decline, append a row to `declined.md` (date, finding, category, reason).
- For each change actually made, append a row to `changes.md` pointing at the changelog entry that holds the diff.

## Friction categories
- **repeated-correction**: you repeat an instruction or preference across or within sessions.
- **routing-misfire**: the wrong skill or no skill fired and you redirected, or you had to name a skill that should have been automatic.
- **repeated-reprompt**: you re-issue the same request because the output missed.
- **repeated-workflow-explanation**: you re-explain the same procedure.
- **tool-permission-friction**: the same command or tool repeatedly denied or re-prompted.

Give special weight to **regressions**: an established rule or workflow that quietly stopped being followed. That is where a model upgrade does its damage, and it is the case that most often maps to enforcement rather than to a new rule.

## Action classes
Map each surviving finding to exactly one:
- `promote-to-memory`: a cross-project preference worth a persistent memory entry.
- `update-skill:<name>`: a specific personal skill needs tightened or added text.
- `update-claude-md`: a routing or global-rule gap.
- `config-fix`: settings.json, a path, a hook, or other plumbing.
- `no-action`: recurring but already governed, or not worth a change.

## Scope guardrails
- Your own personal skills (the `~/.claude/skills/` directory), CLAUDE.md, protocols, settings, hooks, and memory only. **Never skills you installed from a shared or third-party repo**, and never propose changes to a project's own code or repo configuration.
- Prefer no change. Narrow beats broad. If a recommendation sounds like "a skill for all of X," shrink it or drop it.
- Read-only throughout. The skill has no Edit or Write tool by design.

## Session log
This is a utility audit. Do not write a project session log. The report is the output; the changelog (for any change later made) and the two state files are the durable record.

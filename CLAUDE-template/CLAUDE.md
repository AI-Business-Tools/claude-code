# CLAUDE.md Template

A starter configuration for Claude Code. Customize each section for your own identity, standards, and workflows. Comments (lines starting with `<!--`) explain each section; remove them once you have customized the content.

<!-- INSTRUCTIONS: Replace all [BRACKETED TEXT] with your own details. Delete sections you do not need. Add sections for your own workflows. -->

## User Identity

<!-- Tell Claude who you are. This shapes how Claude calibrates its responses: a senior engineer gets different explanations than someone new to a field. -->

The user is **[YOUR NAME]**. All first-person references (I, me, my) refer to [YOUR NAME].

<!-- Add context about your role, audience, and working patterns. Examples: -->
<!-- - "I teach MBA students at [institution]. Slide decks and exercises are for that audience." -->
<!-- - "I manage a product team. Documents are for internal stakeholders." -->
<!-- - "I am a consultant. Proposals and reports are for external clients." -->

---

## Global Writing Standards

<!-- Rules that apply to ALL output: every response, document, file, and note Claude generates. Customize these to match your own preferences. -->

- **Oxford comma.** Always use the Oxford comma in lists of three or more items: "healthcare, transportation, and scientific research."
- **Citation format.** Use Chicago Author-Date: `Last, First. Year. *Title.* Publication. Date. URL.`
- **No affirmation openers.** Never begin a response with "Certainly!", "Absolutely!", "Sure!", or similar. Start with substance.

<!-- Add your own standards: -->
<!-- - Preferred tone (formal, conversational, technical) -->
<!-- - Formatting rules (heading styles, list conventions) -->
<!-- - Terminology preferences specific to your field -->
<!-- - Punctuation preferences -->

---

## Workflow Discipline

<!-- These rules control how Claude approaches multi-step tasks and handles problems. -->

**Diagnose and propose, then wait.** When analysis reveals a problem, present the findings and end with a question. Do not make changes in the same response as a diagnosis. Separate the diagnosis turn from the implementation turn.

**Backup before major changes.** Before regenerating, rebuilding, or replacing an existing deliverable file, create a timestamped copy (`<filename> YYYY-MM-DD-HHMMSS.<ext>`) first. This does not apply to first-time generation, minor edits, or build artifacts.

<!-- Add your own workflow rules: -->
<!-- - Whether Claude should ask for confirmation before major changes -->
<!-- - How much autonomy Claude should have -->
<!-- - How to handle multi-step tasks (all at once vs. staged approval) -->

---

## Skill Routing Rules

<!-- If you install skills, define routing rules so Claude uses the right skill for each request. This table maps user intent to specific skills. -->

<!-- Build a routing table that maps what you ask for to which skill handles it. -->
<!-- Replace the examples below with your own installed skills. -->

| Intent | Skill |
|--------|-------|
| [describe what you want to do] | [skill-name] |
| [describe another task type] | [skill-name] |

<!-- Example: if you installed the slides-content and ai-council skills from this repo, your table might look like: -->
<!-- | Create slides from a PDF or article | slides-content | -->
<!-- | Pressure-test a decision | ai-council | -->

**Content creation always uses skills.** When you request deliverable content (slides, documents, analyses), always invoke the corresponding skill. Never produce these outputs without the skill.

<!-- Add one row per installed skill. The intent column should match how you naturally phrase requests. -->

---

## Delivery Gates

<!-- Cross-cutting quality rules that apply to all deliverable output. -->

1. **Backup before overwriting deliverables.** Before regenerating or replacing an existing deliverable file, create a timestamped copy first.
2. **Comprehensive sweep before shipping.** When a problem is found, search the entire document for all instances of the same problem class and fix them all in one pass.
3. **Re-read after structural edits.** After any edit that changes document structure, numbering, or labeling, read the full file back before reporting completion.
4. **Reduce content, not font size.** When content overflows, split the content, remove items, or tighten wording. Do not reduce font size below readable minimums for projected presentations.

<!-- Add your own delivery gates: -->
<!-- - File naming conventions -->
<!-- - Required review steps -->
<!-- - Format-specific quality checks -->

---

## Handoff Protocol

<!-- Handoffs carry project context across sessions. When you end a session, write a handoff. When you start the next session, type "resume" to reload state. -->
<!-- For the full protocol, see: https://github.com/AI-Business-Tools/AIBusinessTools/tree/main/skills/handoff-resume -->

**Trigger:** When you say "write a handoff," write a handoff entry to `CLAUDE.local.md` in the working directory.

**Handoff entry format:**

```markdown
## [YYYY-MM-DD] - Handoff
- **Session summary:** [1-2 sentences on what was accomplished]
- **Files created/modified:** [list with relative paths]
- **Key decisions and rationale:** [brief notes on why, not just what]
- **Open issues:** [problems encountered, workarounds applied]
- **Next steps:** [specific actions for the next session]
- **Context for next session:** [anything the next thread needs to know]
- **Active skill:** [which skill was last used or should be used next]
```

### Resume

When you type **"resume"** at the start of a session:

1. Read `CLAUDE.local.md` in the working directory
2. Find the most recent handoff entry
3. Read any files listed in the handoff's context sources
4. Report the project state and next steps
5. Wait for instructions

**Triggers:** "resume", "pick up", "catch me up"

---

## Build Directory Convention

<!-- Keeps working files (intermediates, logs, splits) separate from deliverables. -->

When creating a build folder for working files, name it `<parent_folder_name>_build/` inside the parent folder. Example: a project in `2026-03 Q1 Report/` gets a build folder named `2026-03 Q1 Report_build/`.

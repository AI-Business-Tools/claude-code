# Handoff and Resume Protocol

Add the sections below directly to your `CLAUDE.md`. They define two complementary behaviors: **handoff** (capture session state at the end of a session) and **resume** (reconstruct that state at the start of the next session). A third variant, **context** (full load), extends resume with automatic folder scanning.

---

## Handoff Protocol

A handoff is a structured summary written to `CLAUDE.local.md` that captures session state for the next thread. It is different from a raw conversation export, which dumps the full transcript. A handoff is concise, structured, and optimized for a new session to pick up where this one left off.

**Manual trigger:** When you say "write a handoff," write a handoff entry to `CLAUDE.local.md` in the working directory.

**Auto-trigger (optional):** If your skills have Session Log sections, configure them to ask whether to write a handoff when a session involved multiple rounds of edits, troubleshooting, or content iteration. A clean single-pass run does not prompt for a handoff.

**Handoff entry format:**

```markdown
## [YYYY-MM-DD] - Handoff
- **Session summary:** [1-2 sentences on what was accomplished]
- **Files created/modified:** [list with relative paths]
- **Key decisions and rationale:** [brief notes on why, not just what]
- **Open issues:** [problems encountered, workarounds applied]
- **Next steps:** [specific actions for the next session]
- **Context for next session:** [anything the next thread needs to know that is not obvious from the files themselves]
- **Context sources:** [folders and files the next session should read at startup, ordered by priority. Name specific paths relative to the project folder. Prefer digested files over raw sources.]
- **Pre-digested:** [list any _text.md, _summary.md, _notes.md, or other processed files that exist and are current. These are cheaper to read than re-processing source material.]
- **Active skill:** [which skill was last used or should be used next, so the next session routes correctly without asking]
- **Todos:** [tasks to be reminded about on resume. Only present when the handoff was triggered with "todo" items. Each todo is a separate bullet.]
```

**Todo variant:** When the trigger includes "todo" followed by one or more tasks (e.g., `ho todo run backup, update index`), parse the tasks and include them in the **Todos** field. Multiple tasks can be comma-separated or on separate lines. If no "todo" follows the trigger, omit the Todos field entirely.

**Dual write:** Every handoff writes two entries to `CLAUDE.local.md`:

1. **Session log entry** (permanent history). Uses the standard session log format with a **Skill:** field set to the last skill used, or `ad-hoc` if no skill was invoked. This entry is never deleted.
2. **Handoff entry** (rotating snapshot). Uses the handoff format above with context sources, pre-digested files, and active skill fields. This entry rotates per the retention rule below.

Write the session log entry first, then the handoff entry. If the session's work was already logged by a skill's Session Log section, skip the session log entry (no duplicate) and write only the handoff.

**Retention rule:** Keep at most two handoff entries in `CLAUDE.local.md` (current + previous). Before appending a new handoff, scan for existing `## [date] - Handoff` sections. If there are already two, delete the older one so only the most recent remains, then append the new one. Session log entries (non-handoff) are never deleted; they accumulate normally.

**Triggers:** "handoff", "write a handoff", "save a handoff", "handoff for next session", "ho", "ho todo [tasks]", "handoff todo [tasks]"

---

### Resume

When you type **"resume"** at the start of a session, follow this protocol:

1. **Read `CLAUDE.local.md`** in the working directory. Find the most recent handoff entry and scan all `## [date] - [description]` session log entries for a project timeline.
2. **Read context sources.** Follow the **Context sources** field in the handoff, reading each listed file or folder in the order specified. For folders, list contents first and read the most relevant files (prioritize `_text.md`, `_summary.md`, `_notes.md`, outlines, and index files over raw source PDFs or large data files). For files, read them directly.
3. **Read pre-digested files.** Read any files listed in the **Pre-digested** field that were not already covered in step 2.
4. **Report.** Respond with a brief status:

   > **Resumed from [date] handoff.**
   > - Session history: [one-line-per-entry timeline of all session log entries, format: `YYYY-MM-DD: description (skill)`]
   > - Read: [list of files/folders read]
   > - Project state: [1-2 sentence summary from the handoff]
   > - Next steps: [from the handoff]
   > - Active skill: [from the handoff, or "none specified"]
   > - **Todos:** [if the handoff has a Todos field, list each item here prominently. If no todos, omit this line.]
   >
   > Ready to continue.

5. **Wait for instructions.** Do not begin work until you confirm or redirect.

If no handoff entry exists in `CLAUDE.local.md`, read the most recent session log entry instead and report what was found, including the full session history timeline. If `CLAUDE.local.md` does not exist, say so and ask what you want to work on.

**Triggers:** "resume", "pick up", "catch me up"

---

### Context (Full Load)

When you type **"context"**, run the full Resume protocol above (steps 1-5), then additionally:

6. **Scan for context folders.** List the working directory and check for any immediate subfolder whose name matches (case-insensitive): `context`, `content`, `content for context`, or any name starting with `aa context`. Also check for names containing "context for this" (e.g., "aa context for this course").
7. **Read context folders in full.** For each matching folder found, read every file in it (not recursively into sub-subfolders). For PDFs over 4 pages, read the first 4 pages only and note that the remainder was skipped. For binary files (images, .pptx, .xlsx), note their presence but do not read them.
8. **Amended report.** Add to the step 4 report:
   > - Context folders read: [list of folder names and file counts]

If no context folders are found, report that and proceed normally.

**Triggers:** "context", "full context", "load context"

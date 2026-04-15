# Handoff and Resume Protocol

Carry project context across Claude Code sessions without losing state.

---

## Problem

Every Claude Code session starts with an empty context window. On a single-session project this is fine. On a multi-session project, it creates a recurring tax: re-explaining what was built, what decisions were made, what remains to be done, and which tools or conventions are in use. The longer a project runs, the higher this tax becomes.

Raw conversation exports exist but are the wrong solution. A full transcript is large, unstructured, and expensive to re-read. It gives equal weight to productive exchanges and dead-ends, and it cannot be summarized without another round of processing.

The handoff protocol solves this by capturing exactly what the next session needs: a concise structured snapshot written at the end of each session, reconstructed at the start of the next one.

---

## How It Works

At the end of a session, you say "handoff" (or one of the trigger phrases). Claude Code writes a structured entry to `CLAUDE.local.md` in the working directory. The entry records what was done, what files changed, what decisions were made, what is still open, and what context the next session should load.

At the start of the next session, you say "resume." Claude Code reads `CLAUDE.local.md`, follows the context sources listed in the handoff, reads pre-digested summaries, and reports back with a brief status before waiting for instructions.

The protocol is file-based: `CLAUDE.local.md` travels with the project. Every session in the same directory shares the same history.

---

## The Handoff Entry

Each handoff entry has nine fields. Every field serves a specific purpose.

**Session summary** captures what was accomplished in 1-2 sentences. This is what you scan when you forget what you were working on.

**Files created/modified** lists every file touched, with relative paths. The next session can read these directly without searching.

**Key decisions and rationale** records why, not just what. This is the most commonly skipped field and the most valuable one. Implementation choices that seemed obvious in the moment are not obvious three days later.

**Open issues** captures problems that were identified but not resolved, workarounds that were applied, and anything that is still broken or fragile.

**Next steps** lists specific actions for the next session, ordered by priority. These become the work queue when you resume.

**Context for next session** holds anything the next thread needs to know that is not visible from the files themselves: conventions adopted, tools installed, external dependencies, decisions pending.

**Context sources** tells the resume protocol exactly what to read and in what order. This is how the next session avoids both under-loading (missing critical context) and over-loading (reading everything in the directory).

**Pre-digested** lists any processed summary or notes files that exist and are current. Reading a `_summary.md` is cheaper than re-processing the raw source, and the resume protocol uses these preferentially.

**Active skill** records which skill was last used or should be used next. This prevents routing errors where the next session defaults to the wrong workflow.

**Todos** (optional) captures tasks to be surfaced prominently on resume. Only included when the handoff trigger includes "todo" items.

---

## The Resume Protocol

When you type "resume," Claude Code executes a five-step sequence before doing anything else.

1. Read `CLAUDE.local.md`. Find the most recent handoff entry. Scan all session log entries to reconstruct the project timeline.
2. Read context sources. Follow the **Context sources** field in order. For folders, read index and summary files first; for raw sources, prefer `_text.md` and `_summary.md` variants over original PDFs.
3. Read pre-digested files. Read anything in the **Pre-digested** field not already covered in step 2.
4. Report. Output a brief status block covering session history, files read, project state, next steps, active skill, and todos if present. End with "Ready to continue."
5. Wait. Do not begin work until you confirm or redirect.

If no handoff exists, Claude Code reads the most recent session log entry and reports what it found. If `CLAUDE.local.md` does not exist at all, it says so and asks what you want to work on.

The **context** trigger (instead of "resume") runs the same five steps, then additionally scans the working directory for folders named `context`, `content`, `aa context`, or similar, reads every file in each matching folder, and adds a context folders summary to the report.

---

## Design Rationale

**Why a structured file instead of a conversation export?**

A structured file is written by the model that has full context of the session. It compresses what matters and discards what does not. A conversation export preserves everything equally and requires the next session to re-read and re-interpret. The handoff file is already interpreted.

**Why dual write (session log + handoff)?**

The session log is permanent history. It accumulates across sessions and provides a timeline of the project. The handoff is a rotating snapshot optimized for reconstruction. They serve different purposes. Combining them into one entry would either bloat the snapshot or truncate the history.

**Why a two-entry retention limit on handoffs?**

Handoffs are snapshots, not archives. Keeping more than two adds noise: old handoffs describe a state that has been superseded multiple times and may mislead a new session. The session log entries (which are never deleted) preserve the full history for cases where you need to trace back further.

**Why list context sources explicitly rather than reading the whole directory?**

Projects accumulate files that are not all equally relevant. Reading everything in a directory on every resume is slow and wastes context window. Explicit context sources let the session that wrote the handoff (which knows what matters) tell the next session exactly where to look.

**Why the "wait for instructions" step?**

The resume report is a status, not a proposal. Beginning work automatically based on the "next steps" field would be presumptuous: you may want to redirect, add new constraints, or ask questions before work starts. The protocol surfaces state and then stops.

---

## Installation

Copy the contents of `protocol.md` into your `CLAUDE.md`. The protocol is self-contained and does not depend on any other skills in this repository. It works in any Claude Code project where `CLAUDE.local.md` can be written to the working directory.

The triggers ("handoff", "resume", "context", "ho", "ho todo", "pick up", "catch me up") are plain text phrases. No special configuration is required.

If you use skills that have their own Session Log sections, you can configure them to ask whether to write a handoff at the end of multi-round sessions. See the **Auto-trigger** note in `protocol.md` for the opt-in pattern.

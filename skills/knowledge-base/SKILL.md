---
name: knowledge-base
description: Personal knowledge base manager. Processes inbox files (PDF, MD, DOCX, RTF, TXT, HTML, PNG, URL), extracts metadata, renames with citation conventions, generates summaries, maintains a searchable index, answers questions grounded in indexed sources, performs full-text keyword search, moves pipeline output into topic folders, and builds slide decks from indexed or external content via a slides skill.
triggers: kb, process inbox, kb ask, kb move, kb search, kb find, kb slides, slides from kb, build slides from, knowledge base
allowed-tools: Bash(python*), Bash(pip*), Bash(ls*), Bash(mv*), Bash(cp*), Bash(mkdir*), Bash(find*), Bash(wc*), Bash(file*), Bash(export*), Read, Write, Edit, Glob, Grep, WebFetch, WebSearch, Agent, Skill
model: opus
effort: high
---

# Knowledge Base Manager

## Knowledge Base Location

Set your knowledge base root path in your environment or adapt the paths below. The default convention used throughout this skill is:

```
~/knowledge-base/
```

All paths in this skill are relative to this root unless otherwise specified. Adjust to match your actual knowledge base location.

## Directory Structure

The knowledge base supports two document storage patterns:

### Pattern A: Per-document subfolder (content skill output)

When a slides or summary skill processes a document, it creates a per-document subfolder containing the source, text extraction, summary, slides, and build artifacts. This is the structure produced by pipeline skills.

```
knowledge-base/
├── AI-articles/
│   ├── 2026-01-28 Payrolls to Prompts.../     <- per-document subfolder
│   │   ├── Payrolls to Prompts...2026-01-28.pdf
│   │   ├── Payrolls to Prompts...2026-01-28_text.md
│   │   ├── Payrolls to Prompts...2026-01-28_summary.md
│   │   ├── Payrolls to Prompts...2026-01-28_slides.pdf
│   │   └── Payrolls to Prompts...2026-01-28_build/
│   └── 2026-02 Chaining Tasks.../
```

### Pattern B: Flat files (simple drops, inbox output)

For documents that do not need slides or heavy processing, the source, text, and summary sit side by side in the topic folder. Pattern B is the default for knowledge-base-only processing. When a downstream slides skill later generates slides for a Pattern B item, that skill promotes the item to Pattern A by creating a per-document subfolder and moving the existing files into it. The promotion is performed by the slides skill, not by this skill.

```
knowledge-base/
├── AI-teaching/
│   ├── 2026-03-18 Ipeirotis. Scalable Oral Assessments.pdf
│   ├── 2026-03-18 Ipeirotis. Scalable Oral Assessments_text.md
│   ├── 2026-03-18 Ipeirotis. Scalable Oral Assessments_summary.md
│   └── AI-teaching_build/
│       └── split_2026-03-18 Ipeirotis/
```

### Full structure

```
knowledge-base/
├── aa-inbox/                     <- Drop files here for processing
├── aa-blog/                      <- Drop your own blog posts here for processing
├── AI-articles/                  <- Topic folders (create as needed)
├── AI-teaching/                  <-   names are examples, not a fixed list
├── other-articles/               <-   the knowledge-base-update skill discovers all folders
├── index.md                      <- Auto-maintained document index
├── topics.md                     <- Auto-maintained topic descriptions
└── kb.md                         <- How the system works (human-readable reference)
```

**Topic folders are dynamic.** The skill does not maintain a hardcoded list. Any immediate subdirectory of `knowledge-base/` (other than `aa-inbox/`, `aa-blog/`, `aa-recents/`, an optional full-text search folder such as `aa-search/`, an optional documentation folder that describes the system itself, and `*_build/`) is treated as a topic folder. Adding a new folder requires no skill or config changes; running the [knowledge-base-update](../knowledge-base-update/) skill will discover it automatically.

**Conventions:**
- Both patterns are valid; the index treats them identically.
- When scanning for documents, search both `<topic-folder>/*_summary.md` (flat) and `<topic-folder>/*/*_summary.md` (subfolder). Also check for `_text.md` files as the engagement artifact.
- The `aa-inbox/` folder is the ingestion point for new unprocessed content.
- Summary or slides skills can run directly in topic folders; they do not need to go through inbox.
- Topic folders are created by the user; the skill suggests but does not create them without approval.

## Modes

**Index-first gate (lookups and membership questions).** Any request to find, locate, recall, or check whether something is in the knowledge base (whether phrased as `kb ask`, `kb search`, "is X in my kb?", "what do I have on X?", or an informal question) must begin by consulting the index before reading or scanning topic folders directly. Read or `grep index.md`, and run a full-text search if you maintain one (Mode 4). Direct folder browsing is a fallback only, used after the index returns nothing relevant. Never answer a lookup from a folder scan you ran before checking the index.

### 1. Process Inbox (`/kb` or "process inbox")

Scan `aa-inbox/` and `aa-blog/` for new files. Build a list of items with file types and page counts (for PDFs). Items from `aa-blog/` are processed with blog-specific overrides (see Blog Post Processing below).

**Processing levels:**

| Level | What it reads | Outputs | When to use |
|-------|-------------|---------|-------------|
| **full** | All pages via split-pdf agents | `_text.md` + `_summary.md` | Default for all items |
| **triage** | Pages 1-4 only (no splitting) | `_summary.md` only (no `_text.md`) | When prompted: "triage", "first pages only", "triage the big ones" |
| **lite** | Nothing in the PDF | `_summary.md` from companion `.txt` | Automatic when a companion `.txt` file exists |

**Companion .txt convention:** If a PDF has a matching-name `.txt` file (e.g., `Report.pdf` + `Report.txt`), the system uses lite processing automatically: the `.txt` content provides the citation and description for `_summary.md`, and the PDF is filed unread. The `.txt` can contain a citation, description, URL, or any content to base the summary on. If the `.txt` contains a URL (line starting with `http`), fetch the URL for additional content.

**Agent-per-item architecture:** Every inbox item is processed in its own subagent, regardless of file type. This is mandatory for all items, not just PDFs. The subagent architecture serves two purposes: (1) context isolation prevents image and content accumulation that can hit API request size limits, and (2) the agent prompt formulation step forces the parent to read and inline the correct summary skill format before launching the agent, which prevents improvised summaries that do not match the knowledge base's format standards.

**Before launching any agent, the parent must:**
1. Read the appropriate summary skill in full: your academic summary skill (for academic content) or your general summary skill (for non-academic content). If the batch contains both types, read both.
2. Inline the summary format instructions into each agent's prompt. Do not tell the agent to read skill files; include the format template directly.

**Flow:**

1. **Parent:** Scans aa-inbox, lists items, checks for duplicates against `index.md`, detects companion `.txt` files.
2. **Parent:** Reads the appropriate summary skill(s) for the batch (academic and/or general). For items from `aa-blog/`, the blog summary template (see Blog Post Processing) replaces the academic/general template.
3. **Parent:** For each item, launches an Agent to handle Steps 1-4 below. The agent prompt must inline the relevant instructions (file type routing, naming convention, summary format template from the summary skill) and specify the processing level. Do not tell the agent to read other skill files; include the instructions directly in the prompt.
4. **Agent:** Processes the item at the specified level: full (split, read all, `_text.md` + `_summary.md`), triage (read pages 1-4 only, `_summary.md`), or lite (use companion content, `_summary.md`).
5. **Agent returns:** New filename, one-line content summary, content type (academic/general), any errors.
6. **Parent:** After all agents complete, reads each `_summary.md` to determine topic assignments, then presents the batch summary (Step 5).

For each item, the agent follows Steps 1-4:

#### Step 1: Identify file type and route

| Type | Extensions | Processing |
|------|-----------|------------|
| PDF | .pdf | full: split-pdf extraction. triage: read pages 1-4 only. lite: use companion `.txt` |
| Text-based documents | .md, .txt, .rtf | Read directly; generate `_summary.md` |
| Word documents | .docx, .doc | Extract text via python-docx or textutil; generate `_summary.md` |
| HTML files | .html, .htm | Extract via trafilatura; generate `_summary.md` |
| Images | .png, .jpg, .jpeg | Read image; extract text/data/context; generate `_summary.md` |
| URL list | .urls | For each URL, fetch and convert, then process the resulting text |
| URL file (persistent) | `urls.txt` (exact name) | Same as .urls, but **clear the file** after processing instead of moving it. This file stays in aa-inbox/ as a persistent drop target. |
| LaTeX | .tex | Read directly; generate `_summary.md` |

#### Step 2: Extract citation metadata

For each file, attempt to identify:
- **Date** (publication date, not file date)
- **Author(s)** (last name of first author for filename; full citation for extract)
- **Title**

Search order:
1. Explicit citation block in the document (bibliography entry, header metadata, DOI)
2. Document headers, title page, or first paragraph
3. Filename (if already in `YYYY-MM-DD Author. Title` format, preserve it)
4. Web search using title and author keywords to find the canonical citation
5. If still ambiguous, ask the user

#### Step 3: Rename

Rename to: `YYYY-MM-DD Last. Title.ext`

- Date: publication year and month if available; year only if month unknown (use `YYYY-01-01`)
- Author: first author's last name only
- Title: shortened to approximately 60 characters if needed; no special characters except hyphens
- Preserve the original extension

If the file is already correctly named, skip renaming.

#### Step 4: Generate text and summary

For each file, generate two artifacts:

**4a. Full-text extraction (`_text.md`)** (PDF sources only)

During the split-read process, write the full text content to `<filename>_text.md` alongside the source file. Format:

```markdown
--- Page 1 ---

[Full text content of page 1]

[Figure 1: caption or description of figure]

--- Page 2 ---

[Full text content of page 2]

[Table 1: caption or description of table]
```

Include page markers (`--- Page N ---`), all body text, and annotations for images, figures, and tables (`[Figure N: caption]`, `[Table N: caption]`). This is a faithful transcription, not analysis. Non-PDF sources (markdown, text, HTML) do not need `_text.md` because the source file is the text.

For PDFs, use split-pdf to deep-read. For shorter documents (under 5 pages), read directly. Delete the split build folder after writing `_text.md`.

**4b. Structured summary (`_summary.md`)**

Generate a full structured summary following the format template inlined in the agent prompt by the parent (see Flow steps 2-3 above). The format comes from one of:
- Your academic summary skill for academic papers, research articles, preprints, and working papers
- Your general summary skill for news articles, blog posts, reports, videos, and podcasts

The agent does not read these files itself; the parent reads them before launch and inlines the format. Follow the inlined template exactly.

Save as `<filename>_summary.md` alongside the source file. The summary is the analytical reference artifact; the index entry is derived from it.

#### Step 5: File items and report

**This step runs in the parent conversation** after all item agents have completed.

Read `topics.md` (if it exists) and `index.md` to understand existing categories, then determine the best-fit topic folder for each item. **Do not pause for confirmation.** File each item into its best-fit folder immediately, update the index, recents, and search, and then report what was filed and invite redirection. The user corrects after the fact rather than approving before; see "Correcting a filing" below.

**Folder selection:**
- If an item clearly fits an existing topic folder, file it there.
- If no existing folder is a clear fit, file it into your overflow folder (for example, `other-articles/`) and flag it in the report so the user can redirect (including to a new folder). **Never auto-create a topic folder.** A new folder is created only when the user names one in a redirect.
- If an item was flagged as a likely duplicate during the scan (flow step 1), do **not** auto-file it. Leave it in `aa-inbox/`, report it as a probable duplicate of the existing entry, and wait for direction (file anyway, or discard).

**File each item:** move the source file, its `_text.md`, and its `_summary.md` to the target folder. **Update `index.md` immediately after each item is moved** (not deferred to a later sync). Each new entry gets a one-line summary derived from the `_summary.md`. The index must stay current as items are processed so that subsequent Q&A and topic decisions reflect the latest state.

**Report (after filing).** Present all filed items with the folder each landed in and the reason:

> **Filed 3 items from inbox:**
>
> | # | Renamed file | Type | Filed to | Why |
> |---|---|---|---|---|
> | 1 | `2026-03-15 Autor. The Labor Market Impacts of AI.pdf` | 24pp PDF | **AI-employment/** | labor economics, AI impact on wages |
> | 2 | `2026-02-28 Mollick. Why Students Need AI Tutors.pdf` | 8pp PDF | **AI-teaching/** | AI in education, pedagogy |
> | 3 | `2025-12-01 Cowen. Economic Growth in 2026.md` | markdown | **other-articles/** | no clear existing-folder fit; filed to overflow (flagged) |
>
> Filed as above. To move any, say "move `<item>` to `<folder>`" and I will re-file.

**Always use the full renamed filename** (with date prefix) in the report table. The date prefix is essential for sorting and identification.

**Rate usage report:** After presenting the batch summary table, always include a rate usage report. This is mandatory regardless of whether items were processed by subagents or directly in the parent conversation.

Report each agent's item name, page count, token usage, and wall-clock time:

> **Rate usage:**
>
> | Agent | Item | Size | Tokens | Time |
> |-------|------|------|--------|------|
> | 1 | Core Memory Podcast | md | 42k | 2m |
> | 2 | Enterprise AI Market | 35pp | 99k | 9m |
> | 3 | Isik. Three Obstacles RAI | md | 28k | 1m |
> | | **Total** | | **169k** | **9m wall** |

Token counts come from the agent task notification `total_tokens` field. Wall time is the elapsed time from launch to the last agent completing (parallel agents share wall time). All items go through subagents, so this format applies to every run.

**Update `aa-recents/`** after all moves are complete. This folder contains symlinks to the 10 most recently added items (by date added, not publication date). Numbered `01` through `10`, most recent first. Each symlink points to the item's `_summary.md` (or source `.md` if no separate summary exists).

Rebuild procedure (overwrite all symlinks each time):
1. `rm -f knowledge-base/aa-recents/*`
2. For each of the 10 most recent items, create: `ln -sf <absolute_path_to_summary> knowledge-base/aa-recents/NN Author. Short Title_summary.md`
3. Use short, readable names (no date prefix needed since the number provides recency order).

**Refresh the full-text search index** (if you maintain one; Mode 4) after all moves and the recents rebuild, so the new items become findable. Best-effort; do not block the user-visible report on a reindex failure.

#### Correcting a filing

When the user redirects an item after it was auto-filed ("move `<item>` to `<folder>`", "that belongs in `<folder>`", or equivalent):

1. Move the item's files (source, `_summary.md`, and `_text.md` if present; for a Pattern A item, the whole per-document subfolder) into the named topic folder. If the named folder does not exist, create it (the user naming it is the approval) and add a one-line scope description to `topics.md`.
2. Edit the **Topic cell of the existing `index.md` row** for that item; do not add a new row.
3. Rebuild `aa-recents/` and refresh the full-text search index if you maintain one (same procedures as above).

Sources are never deleted, so re-filing is fully reversible.

### Blog Post Processing (aa-blog/)

When processing items from `aa-blog/`, apply these overrides to Steps 1-5:

**Step 2 override (metadata):** Author is always the user. Extract the title and publication date from the content. If the publication date cannot be determined, use the file modification date. Blog posts may arrive in any format (md, html, pdf, docx, txt, etc.); apply the same file type routing as Step 1.

**Step 3 override (rename):** Use the naming convention `YYYY-MM-DD AuthorName (blog). Title.ext`

The `(blog)` tag is mandatory. It distinguishes the user's own writing from external sources in topic folders and makes blog posts greppable across the entire knowledge base (`grep -r "(blog)" knowledge-base/`).

**Step 4 override (summary):** Use this lighter template instead of the full academic/general summary. Blog posts are already condensed writing; a full structured summary would be redundant.

```
# [Title]

**Author:** [Your name]
**Published:** YYYY-MM-DD
**URL:** [URL if known]
**Type:** blog

## Thesis
[1-2 sentences: the central argument or claim]

## Key Claims
- [claim 1]
- [claim 2]
- [claim 3-5]

## Sources Cited
- [source 1, Chicago Author-Date]
- [source 2]

## Context
[1-2 sentences: what prompted this post, what it responds to]
```

Do not use the academic or general summary skill for blog posts. Inline this template into the agent prompt instead.

**Step 5 override (index):** Add `[blog]` after the summary text in the index entry. Blog posts are filed into existing topic folders alongside external sources, using the same topic suggestion process. They are not stored in a separate blog-only folder.

**No `_text.md` for blog posts.** The source file is the text. Only generate `_summary.md`.

### 2. Q&A (`/kb ask [question]` or "kb ask")

Answer questions grounded in the indexed knowledge base.

#### Step 1: Consult the index first (mandatory)
Per the index-first gate above, start here before any folder scan. Read `index.md` for the full document inventory with topics and one-line summaries. If you maintain a full-text search index (Mode 4), also run `kb search <terms>` to surface body-text hits the one-line summaries miss. Only then proceed to Step 2.

#### Step 2: Identify relevant sources
Based on the question, select the 5-15 most relevant documents. Read their `_summary.md` files.

#### Step 3: Synthesize answer
Write a grounded answer that:
- Cites sources by author and date (Chicago Author-Date)
- Distinguishes between what sources say and inference or synthesis
- Distinguishes between the user's published positions (`[blog]` entries) and external sources when both are relevant
- Notes gaps (aspects of the question not covered by any indexed source)
- Flags contradictions between sources

#### Step 4: Optionally save the answer
Offer to save the answer as a `.md` file in the knowledge base:
> "Save this answer to the knowledge base? It will be indexed for future queries."

If accepted, save as `YYYY-MM-DD Query. [Short description].md` in the most relevant topic folder and update `index.md`.

### 3. Move Project (`kb move <source_dir> <topic>`)

Move all artifacts from a source directory into a knowledge base topic folder. Use this when a content skill (a slides skill, summary skill, etc.) has already processed a document outside the knowledge base, and the output needs to be filed.

**Triggers:** `kb move`, `move to [topic]`, `file this in [topic]`, or any request to move pipeline output into a topic folder.

#### Step 1: Inventory the source directory

List all files in the source directory. Classify each file against the artifact pattern list:

| Pattern | Examples | What it is |
|---------|----------|------------|
| Source file | `.pdf`, `.md`, `.docx`, `.html`, `.tex`, `.rtf` | Original document |
| `*_summary.md` | `paper_summary.md` | Structured summary |
| `*_text.md` | `paper_text.md` | Full-text extraction |
| `*_slides.pdf` | `paper_slides.pdf` | Slide output |
| `*_build/` | `Downloads_build/` | Build artifacts (LaTeX intermediates, splits, notes) |
| `*-analysis.md` | `paper-analysis.md` | Companion analysis |
| `*_notes.md` | `paper_notes.md` | Reading notes |

Ignore `.DS_Store` and other OS metadata files.

Present the inventory:

> **Source directory:** `/path/to/source/`
>
> | # | File | Pattern | Action |
> |---|------|---------|--------|
> | 1 | `paper.pdf` | source | rename + move |
> | 2 | `paper_summary.md` | summary | rename + move |
> | 3 | `paper_slides.pdf` | slides | rename + move |
> | 4 | `Downloads_build/` | build | move as subfolder |
>
> **Target:** `knowledge-base/relationships/`
> **Storage pattern:** A (subfolder) -- slides and build folder present
>
> Proceed?

Wait for confirmation before moving.

#### Step 2: Determine storage pattern

- **Pattern A (subfolder):** Use when slides, build folder, or 4 or more artifacts exist. Creates `<topic>/<date> <Author>. <Title>/` containing all files.
- **Pattern B (flat):** Use when only source and summary (and optionally text) are present. Files go directly in the topic folder.

#### Step 3: Rename artifacts

Apply the knowledge base naming convention (`YYYY-MM-DD Last. Title`) to all artifacts:

- Source file: `YYYY-MM-DD Last. Title.ext`
- Summary: `YYYY-MM-DD Last. Title_summary.md`
- Text: `YYYY-MM-DD Last. Title_text.md`
- Slides: `YYYY-MM-DD Last. Title_slides.pdf`
- Analysis: `YYYY-MM-DD Last. Title-analysis.md`
- Notes: `YYYY-MM-DD Last. Title_notes.md`
- Build folder: `YYYY-MM-DD Last. Title_build/` (or `<topic>_build/` for Pattern B)

If a `_summary.md` exists, extract citation metadata from it. Otherwise, extract from the source file using the same rules as Mode 1 Step 2.

If the source file is already in citation format, preserve its name and derive artifact names from it.

#### Step 4: Move all artifacts

Use `mv` (not `cp`) for every file. After moving:

1. **Verify** all files arrived at the destination (ls the target).
2. **Check** the source directory is empty (ignoring `.DS_Store`).
3. **Report** what was moved and what remains.

If the source directory is empty after the move, offer to remove it. If files remain, list them explicitly.

#### Step 5: Update index and recents

- Update `index.md` with a new entry derived from `_summary.md`.
- Rebuild `aa-recents/` symlinks (same procedure as Mode 1).
- If you maintain a full-text search index (Mode 4), reindex so the moved item becomes findable. Best-effort; do not block the move report on a reindex failure.

### 4. Search (`kb search <query>`)

Keyword search over the full body of every indexed `_summary.md` and `_text.md`, ranked by relevance. Use this when the request is "find me everything that touches X" rather than "answer this question." Q&A synthesis is not invoked.

**Triggers:** `kb search <query>`, `kb find <query>`, `search kb for <query>`.

This mode assumes a full-text index over the body content of the knowledge base. It is optional: if you have not set one up, fall back to `grep -r` over `_summary.md` and `_text.md` files, or use Q&A (Mode 2) instead. The reference implementation is a SQLite FTS5 database built from every `_summary.md` and `_text.md` and queried with BM25 ranking; any equivalent full-text indexer works. Wire your own indexer behind two commands:

- **search** `<query>`: returns ranked hits, each with date, topic, author, title, type, a snippet with the matched terms highlighted, and the absolute path to the source file.
- **reindex**: walks every topic folder and rebuilds the index from current `_summary.md` and `_text.md` content. It should run in well under a minute at a few hundred documents.

Run the search, then relay the ranked output to the user verbatim, plus a one-line interpretation if the top hit is not obvious. Do not synthesize an answer from the snippets; that is Q&A's job.

**When the index is empty or stale:** if the search returns nothing and the query terms are common, rebuild the index (reindex) from current source content and retry.

**The index is authoritative; the full-text database is not.** `index.md` is the complete, append-maintained inventory of every document. The full-text database is a derived accelerator that may cover only a subset of the corpus (it typically skips build folders, hidden folders, and `materials/`). A document can be catalogued in `index.md` yet absent from the full-text index. Treat a search miss as "not in the full-text index," never as "not in the knowledge base."

**Membership questions ("is X in the kb?") consult `index.md` directly.** Before concluding a document is absent, `grep index.md` for the title, author surname, or concept terms. The authoritative check is the `index.md` grep, not the full-text result.

### 5. Slides (`kb slides <target>`)

Build a slide deck from a knowledge base item, an inbox item, an external file path, or a URL. The skill resolves `<target>` to a single source file, runs the inbox flow if needed to produce `_summary.md` and `_text.md`, then hands off to your slides skill (which handles Pattern B to Pattern A promotion and reuses existing artifacts). This mode requires a slides skill that accepts a source path; if you do not have one, file the item with Mode 1 and run your slides workflow separately.

**Triggers:** `kb slides <target>`, `slides from kb <target>`, `build slides from <target>`.

`<target>` is one of:
- A URL (starts `http://` or `https://`)
- A filesystem path (absolute or relative) that exists
- A name fragment (everything else)

Any structure or style argument is passed through verbatim to your slides skill (for the slides skills in this repository, that is `structure=` and `register=`, with `audience=` as a deprecated alias).

#### Step 1: Resolve `<target>` to a single source file

Resolve in this order:

1. **URL** -> write a staging file at `aa-inbox/slides-YYYY-MM-DD-HHMMSS.urls` containing just that URL (one line). Continue at Step 2 (treated as an inbox item).
2. **Existing path** -> use directly. Continue at Step 2.
3. **Name fragment** ->
   a. Search the corpus for the fragment (full-text search if you have one, otherwise `grep -r` over `_summary.md` files and `index.md`).
   b. Independently `ls aa-inbox/` for filenames containing the fragment (case-insensitive substring match).
   c. Combine results:
      - **0 hits:** report not found and exit.
      - **1 hit:** use that path; continue at Step 2.
      - **2 or more hits:** present a numbered list (path, topic, one-line snippet) and wait for the user to pick.

#### Step 2: Determine the case

- **Case A: source is in `aa-inbox/`:** invoke the Mode 1 (Process Inbox) flow on this single item, with two overrides: (1) the deep-read agent retains the split build folder (do not delete it after writing `_text.md`, because the slides skill may re-extract from it); (2) the Step 5 file-then-report behavior applies as a single row: the item is auto-filed into its best-fit folder with no confirmation pause, exactly as in Mode 1, and the "Correcting a filing" path is available if the user redirects. After the item is auto-filed, fall through to Case B with the new in-topic path.
- **Case B: source is in a topic folder:** skip processing. Continue to Step 3.
- **Case C: source is outside the knowledge base and outside the inbox:** skip processing. Continue to Step 3.

#### Step 3: Existing-slides check

Compute the prospective output directory per your slides skill's naming: `<parent>/<content_name>/`, where `<content_name>` is the source filename without extension. Check whether `<output_dir>/<content_name>_slides.pdf` exists. (For an item still at Pattern B, also check `<topic_folder>/<content_name>_slides.pdf`.)

If a slide PDF is found, ask whether to rebuild (timestamp a backup of the existing PDF, then regenerate) or skip. On skip, exit without touching any file. If no slides exist, continue.

#### Step 4: Hand off to your slides skill

Invoke your slides skill, passing the resolved absolute source path and any audience or style argument. The slides skill is expected to reuse `_text.md` and `_summary.md` if present, promote Pattern B to Pattern A, and run its own compile and audit cycle.

#### Step 5: Post-build sync

After the slides skill reports completion, run the index-update hook (see Integration section): read `index.md`, search for the document by filename, append an entry if missing. The slide artifact does not get its own index entry; the source document's entry covers it. If Case A ran, the inbox flow already refreshed recents and the full-text index; if Case B or C ran, the source was already in the corpus, so no additional reindex is needed.

## Index Format

`index.md` is a markdown table, one row per document:

```markdown
| Date | Author | Title | Topic | Summary |
|------|--------|-------|-------|---------|
| 2026-03-18 | Ipeirotis | Scalable Oral Assessments Using Voice AI | AI-articles | Voice AI oral exams at $0.42/student with multi-model deliberation achieving alpha=0.86 |
| 2026-02-18 | AuthorName (blog) | Did an Autonomous AI Write a Hit Piece | AI-safety | Analysis of an autonomous agent incident and implications for AI governance [blog] |
```

The index must stay small enough to fit in a single context window read (approximately 200 entries at current scale). If it grows beyond this, add a `topics.md` summary layer that the Q&A mode reads first to narrow which topic folders to search.

## Topics File

`topics.md` describes each topic folder:

```markdown
# Knowledge Base Topics

## AI-articles
AI's impact on labor markets, productivity, organizational design, and business strategy. Papers and reports analyzing economic and operational effects of AI adoption.

## AI-teaching
AI in education: assessment, tutoring, pedagogy, and curriculum design. How AI changes teaching and learning.

## other-articles
Non-AI articles on diverse topics. Overflow for content that does not fit a specific AI category.
```

Updated by the [knowledge-base-update](../knowledge-base-update/) skill. The user's folder organization choices over time teach the system what belongs where.

## Integration with Other Skills

### Skills that feed into knowledge-base
- **split-pdf**: Used by inbox processing for PDF extraction
- A web-to-text conversion skill for URL ingestion (web page to extracted text)

### Skills that consume knowledge-base data
- **Your summary skills (academic/general)**: The user can request a full summary of any indexed document; the extract is not a substitute.
- **Your blog writing skill**: Q&A mode can find relevant sources for post research.
- **Your slides skill**: Indexed extracts can feed slide generation without re-reading source PDFs. Mode 5 (`kb slides`) is the direct invocation path: it resolves a name fragment, path, or URL, runs the inbox flow if needed, then hands off to your slides skill.
- **Your analyze-and-reply skill**: Q&A can identify relevant indexed sources to support or challenge forwarded content.
- **Your chart skill**: Q&A answers involving data comparisons can generate charts.
- **Your diagram skill**: System architecture and topic maps can be generated as standalone diagrams.

### Index-update hook for content skills

When any content skill (slides, summary, etc.) completes work inside the `knowledge-base/` directory tree, it should check whether the document it processed is in `index.md`:

1. Read `knowledge-base/index.md`.
2. Search for the document by filename or title.
3. If not found, read the document's `_summary.md` and append an index entry.
4. If found, no action needed.

This is a lightweight check (read index, grep, optionally append one row). It does not require invoking the knowledge-base-update skill. Content skills should perform this check as a final step after writing their deliverables.

**Where to run content skills:** Run them directly in the topic folder where the document lives. Do not route through inbox for documents that are already organized. The skill creates its subfolder and build artifacts in place. The index-update hook ensures the index stays current regardless of where processing happens.

## Constraints

- **Never delete original source files.** The skill renames and moves but never deletes.
- **Never overwrite extracts.** If an extract already exists, skip unless the user explicitly asks to regenerate.
- **Index is append-only during processing.** Entries are only removed by the [knowledge-base-update](../knowledge-base-update/) skill when source files are confirmed missing.
- **Topic folders are user-created.** The skill suggests new folders but waits for approval before creating them.

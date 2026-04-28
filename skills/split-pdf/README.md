# Split-PDF

Download, split, and deeply read academic PDFs without crashing your context window.

## Problem

Academic papers are long. Reading a 40-page PDF in a single Claude Code session reliably produces one of two failure modes: a fatal "prompt too long" error that destroys all session context, or a shallow summary that hallucinates details because the model compressed too much into too little attention.

The temptation is to just pass the whole PDF to the Read tool and ask for a summary. This works on short papers and fails unpredictably on longer ones. When it fails on a long paper, it fails badly: the session becomes unrecoverable, and any work done before the read is lost.

## Approach

Split-PDF breaks the problem into small, recoverable pieces:

1. **Download or locate** the source PDF (from a URL or a local path)
2. **Split** the PDF into 4-page chunks using PyPDF2, stored in a `<foldername>_build/` directory alongside the original
3. **Read in batches of 3 chunks** (~12 pages per batch), pausing after each batch so the user can confirm before continuing
4. **Write structured notes** incrementally as each batch completes, tracking 8 dimensions: research question, audience, method, data, statistical methods, findings, contributions, and replication feasibility
5. **Save a persistent extract** (`<basename>_text.md`) in the same folder as the source PDF, so future sessions can skip the re-read entirely

The original PDF is never modified or deleted. The splits are working copies. If anything goes wrong at any step, re-splitting from the original takes seconds.

## Design Rationale

**Why 4-page chunks?** Four pages is small enough that each chunk loads quickly and produces clear image data from the Read tool. Larger chunks (8-12 pages) can still overload context on figure-heavy papers. Smaller chunks (2 pages) generate excessive file counts without meaningful benefit.

**Why read only 3 chunks at a time?** Each PDF page rendered by the Read tool adds image data to the conversation context permanently. Reading all chunks at once in a long paper can add 10-20MB of image data, pushing the session past the API request size limit. Three chunks (~12 pages) keeps each batch well within safe limits while making meaningful progress per round.

**Why structured notes rather than a summary?** A summary compresses a paper into its conclusions. A structured extraction captures what a reader needs to build on or replicate the work: the actual data sources with URLs, the sample sizes, the specific econometric specifications, the coefficient estimates and standard errors. Summary-style output is easier to produce but harder to act on. The 8-dimension extraction schema comes directly from what researchers need to evaluate a paper for relevance, quality, and reproducibility.

**Why a persistent `_text.md` extract?** The reading process is expensive in time and API calls. Saving the notes alongside the source PDF means any future session on the same paper skips straight to using the extract. The skill checks for an existing extract before splitting and offers to reuse it.

**Why subagent isolation for programmatic use?** When another skill (such as a slides or knowledge-base workflow) calls split-pdf as part of a larger pipeline, reading PDFs in the parent conversation contaminates the context with image data that can make the rest of the session unusable. Running the read phase in a subagent keeps the image data isolated. The parent receives only the plain-text notes file.

## Usage

**Installation:**

```bash
# Install the PyPDF2 dependency
pip install PyPDF2
```

Place this skill's `SKILL.md` in `~/.claude/skills/split-pdf/SKILL.md`.

**Invoking the skill:**

```
/split-pdf ~/Documents/papers/smith_2024.pdf
```

```
/split-pdf "Gentzkow Shapiro Sinkinson 2014 competition local newspapers"
```

You can provide either a local file path or a search query identifying the paper. If you provide a search query, the skill uses web search to locate and download the PDF before splitting.

**Triage mode:** To read only the abstract and introduction without committing to a full read, say so explicitly. The skill will read only the first split (pages 1-4) and stop.

**Subagent use:** If you are building a workflow skill that calls split-pdf programmatically, run the split step in your parent context (lightweight) and delegate the read step to a subagent using the prompt template in the Agent Isolation Protocol section of SKILL.md.

## Output

After a complete read, the skill produces two files:

- `<foldername>_build/split_<basename>/notes.md`: the working notes file, updated incrementally after each batch. This file is the running record of what has been read so far.
- `<basename>_text.md`: the final structured extract, written alongside the source PDF when all batches are complete. This is the persistent, reusable artifact for future sessions.

The extract covers 8 dimensions: research question, audience, method, data (sources, sample size, time period, unit of observation), statistical methods, findings, contributions, and replication feasibility. It contains specific variable names, equation references, coefficient estimates, and standard errors, not a narrative summary.

## Installation

1. Copy `SKILL.md` into `~/.claude/skills/split-pdf/SKILL.md`.
2. Install the PyPDF2 dependency: `pip install PyPDF2`.
3. Restart Claude Code (or run `/skills` to reload).
4. Trigger by saying "read this paper," "summarize this PDF," or by passing a path or search query directly: `/split-pdf <path-or-query>`.

## Acknowledgments

The split-pdf approach originated in [MixtapeTools](https://github.com/scunning1975/MixtapeTools), a repository of research workflow utilities developed by **Scott Cunningham**, Professor of Economics, Baylor University. His work on practical tools for applied econometrics researchers informed the extraction schema and the batch-read discipline that this skill formalizes.

- [LinkedIn](https://www.linkedin.com/in/scott-cunningham-7788912/)
- [GitHub](https://github.com/scunning1975)

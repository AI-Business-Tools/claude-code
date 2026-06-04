# Academic Paper Summary

Turn an academic paper into a structured, citation-backed summary with a consistent section layout every time.

## Problem

Research papers are dense, and ad-hoc summaries come out shaped differently every time: sometimes a wall of prose, sometimes a citation with no methodology, sometimes a confident gloss that quietly drops the population studied or the effect sizes. When you summarize many papers, that inconsistency makes them hard to compare and hard to file. You also want the summary to read as direct exposition, not as a book report about "what the authors argue."

This skill fixes the shape. Every paper comes out with the same nine sections, a correct Chicago Author-Date citation, and an expository voice that states findings as facts rather than narrating the source.

## Approach

The skill enforces a fixed output contract. The structure is the same for every paper, so a stack of summaries is directly comparable, and sections that do not apply (population for a theoretical paper, issues when there are none) are skipped cleanly rather than padded.

Two design choices carry most of the value. First, the expository-style rule bans "the author," "the paper," and "the study argues," which forces the summary to commit to the content instead of hedging behind attribution. Second, the citation block is format-aware: published articles, preprints, and working papers each get the correct Chicago Author-Date form, so the summary is ready to cite without rework.

A quick variant trades depth for speed: citation, one-sentence thesis, a handful of key points, and a short summary paragraph.

## The Flow

1. **Read the source.** A PDF of 4 pages or fewer is read directly. A longer PDF is split into 4-page chunks and read in a subagent that writes notes, which keeps the full document out of the main context window and avoids a shallow skim. Text, web links, and pasted content are read in place. If a prior text extract exists, it is read instead of re-processing the PDF.
2. **Compose the citation.** Chicago Author-Date, with the correct variant for a published article, a preprint, or a working paper.
3. **State the thesis.** One sentence, with explicit handling for literature reviews, meta-analyses, and exploratory studies that have no single thesis.
4. **Fill the fixed sections.** Key points, conclusions with quantified effects, population and methodology, implications, undergraduate-level concepts, and any factual errors, fallacies, or strong unaddressed counterarguments. Inapplicable sections are skipped.
5. **Write the summary paragraph.** 100 to 300 words, neutral, scaled to the complexity of the conclusions.
6. **Save.** Written to `<project_name>_summary.md` in the project folder.

## Usage

**Trigger phrases:** `summarize this paper`, `summarize this research`, `academic summary`, `/academic-summary`, `quick academic summary`, `brief paper summary`, `/academic-summary quick`

**Good uses:**
- Building a comparable library of paper summaries you will revisit or cite
- Getting the methodology, population, and effect sizes pulled out cleanly, not just the headline
- A fast read on whether a paper is worth a full read (use the quick variant)

**Not good uses:**
- News, blog posts, videos, or podcasts (use the summary-general skill)
- A reading you intend to quote at length (read the source; a summary is not a substitute)

**Tips:**
- Pass a file path rather than pasting a long paper.
- If you have already extracted the text once, keep the `<basename>_text.md` file next to the PDF; the skill reads it instead of re-splitting.
- Use the quick variant for triage, the full variant for papers you will actually use.

## Installation

1. Copy `SKILL.md` to `~/.claude/skills/summary-academic/SKILL.md`.
2. Restart Claude Code (or start a new session).
3. The skill activates on any trigger phrase above.

This skill pairs with the [split-pdf](../split-pdf/) skill for long PDFs and with the [summary-general](../summary-general/) skill for non-academic content. Install those too if you want the full set.

## Output

A single markdown file, `<project_name>_summary.md`, written to the project folder. `<project_name>` resolves to a name you specified, otherwise the source filename without its extension, otherwise the folder name.

## Design Rationale

**A fixed nine-section contract.** Comparability is the point. When every paper has the same sections in the same order, a folder of summaries becomes a dataset you can scan, not a pile of differently-shaped notes.

**Expository voice, no source references.** Banning "the author argues" forces the summary to assert the content. A summary that hides behind attribution on every line is harder to use and quietly less accountable for whether the claim is right.

**Format-aware citations.** A preprint is not a published article and a working paper is not either. Encoding the three Chicago Author-Date variants means the citation is correct on the first pass.

**Skip, do not pad.** Theoretical papers have no population; many papers have no factual errors. The skill omits those sections entirely rather than writing "not applicable," which keeps the summary honest about what it actually contains.

**A quick variant for triage.** Deciding whether to read a paper is a different task from summarizing one you have committed to. The quick variant serves the first without pretending to do the second.

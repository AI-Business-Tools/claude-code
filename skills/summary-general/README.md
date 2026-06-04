# General Content Summary

Turn a news article, blog post, video, or podcast into a structured, citation-backed summary with the numbers kept in.

## Problem

Most summaries of general content drift in two directions. They go vague, dropping the statistics and concrete figures that were the whole point of the piece, or they go credulous, restating the source's framing as if it were settled fact. You want the opposite: a tight summary that keeps the numbers, reads as direct exposition rather than "the article says," and flags where the piece is actually weak.

This skill produces that. It is the non-academic counterpart to the academic-paper summarizer, tuned for the shorter, more argumentative, more numbers-light-but-numbers-matter content you read every day.

## Approach

The output is deliberately lean: a citation, a one-sentence thesis, a themes list, an optional issues section, and a short summary paragraph. No section headings except "Issues:", because general content does not need the scaffolding that a research paper does.

Two rules do the heavy lifting. The themes list is required to carry the specific numerical data, so percentages, ratios, and comparative figures survive the compression instead of being smoothed into adjectives. The issues section appears only when there is something real to flag: a factual error, a logical fallacy, or a strong counterargument the piece never engages. When the content is clean, the section is omitted rather than filled with manufactured criticism.

A quick variant trims to a citation, thesis, a few themes with the key statistics, and a 50-to-100-word summary.

## The Flow

1. **Read the source.** A short PDF is read directly; a long one is split into 4-page chunks and read in a subagent that writes notes, keeping the document out of the main context window. Web pages, transcripts, and pasted text are read in place. An existing text extract is read instead of re-processing.
2. **Compose the citation.** Chicago Author-Date, with variants for a standard byline, three or more authors, a video or podcast, or content with no clear author.
3. **State the thesis.** One sentence, with explicit handling for news reports, interviews, opinion pieces, and explainers.
4. **List the themes.** 5 to 12 bullets that keep the statistics, percentages, and comparative figures.
5. **Flag issues, if any.** Factual errors, fallacies, or strong unaddressed counterarguments, with quoted text. Omitted entirely when the piece is clean.
6. **Write the summary paragraph.** 75 to 200 words, neutral, scaled to complexity.
7. **Save.** Written to `<project_name>_summary.md` in the project folder.

## Usage

**Trigger phrases:** `summarize this`, `summarize this article`, `general summary`, `/general-summary`, `quick summary`, `brief summary`, `/general-summary quick`

**Good uses:**
- Capturing the substance and the numbers from an article or report you will reference later
- Getting a fast, neutral read on an opinion piece before deciding whether to engage with it
- Summarizing a long video or podcast from its transcript

**Not good uses:**
- Academic papers, preprints, or dissertations (use the summary-academic skill)
- Drafting a reply to the piece (use an analyze-and-reply skill instead)

**Tips:**
- Pass a file path or URL rather than pasting long content.
- For a podcast or video, supply the transcript if you have it; the summary is only as good as the text it can read.
- Use the quick variant when you only need the gist and the headline numbers.

## Installation

1. Copy `SKILL.md` to `~/.claude/skills/summary-general/SKILL.md`.
2. Restart Claude Code (or start a new session).
3. The skill activates on any trigger phrase above.

This skill pairs with the [split-pdf](../split-pdf/) skill for long PDFs and with the [summary-academic](../summary-academic/) skill for scholarly content. Install those too if you want the full set.

## Output

A single markdown file, `<project_name>_summary.md`, written to the project folder. `<project_name>` resolves to a name you specified, otherwise the source filename without its extension, otherwise the folder name.

## Design Rationale

**Keep the numbers.** General content compresses badly because the figures are the first thing a loose summary drops. Making the themes list explicitly responsible for statistics and comparative figures is what keeps the summary useful rather than impressionistic.

**Issues only when real.** A summary that always finds something wrong is as useless as one that never does. The section is conditional by design: present when there is a genuine error, fallacy, or unaddressed counterargument, absent otherwise.

**Minimal scaffolding.** A blog post is not a research paper. Dropping every heading except "Issues:" matches the lighter structure of the content and keeps the summary fast to read.

**Expository voice.** Banning "the article says" forces the summary to assert the content directly, which is both more readable and more honest about what is being claimed.

**A separate academic skill.** Scholarly papers need methodology, population, and effect-size handling that general content does not. Splitting the two skills keeps each one tuned to its material instead of compromising on a single format.

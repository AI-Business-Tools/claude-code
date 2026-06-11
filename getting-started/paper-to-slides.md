# From Academic Paper to Slides

This guide walks the full path from an academic paper (or any substantial document) to a finished slide deck, using the skills in this repository. One request does the whole job once the pieces are installed; this page shows what to install, what to say, what happens during the run, and where everything lands.

The flow is the same whether the source is a PDF on your machine, a Word document, a markdown file, or a URL: resolve the source, reuse any work that already exists, build the deck, and keep every artifact in one folder per paper.

## What you get

A run produces a per-paper folder containing:

- **`<paper>_slides.pdf`**: the compiled slide deck (the deliverable)
- **`<paper>_summary.md`**: a structured summary of the paper (a deliverable in its own right)
- **`<paper>_text.md`**: a full-text extraction, reused by any later rebuild so the paper is never deep-read twice
- **`<paper>.pptx`**: a native PowerPoint version (optional, generated only if you ask)
- **`<paper>_build/`**: working files (LaTeX source, split chunks, figures, reading notes)

## Install once

| What | Why | How |
|---|---|---|
| TeX Live (MacTeX on macOS) | Compiles the Beamer deck; `pdflatex` must be on your PATH | `brew install --cask mactex` on macOS; OS-specific steps in [beamer](../skills/beamer/) Step 0 |
| Python 3 with PyPDF2 | Splits long PDFs into readable chunks | `pip install PyPDF2` |
| python-pptx | Only needed for the optional PowerPoint conversion | `pip install python-pptx` |
| [split-pdf](../skills/split-pdf/) | Deep-reads the paper in 4-page chunks | Copy per its README |
| [summary-academic](../skills/summary-academic/) and [summary-general](../skills/summary-general/) | Produce the structured summary (auto-detected by source type) | Copy per their READMEs |
| [beamer](../skills/beamer/) + [Beamer style guide](../style-guides/beamer/) | Generates, compiles, and audits the deck | Copy the whole skill directory and the style guide |
| [slides-content](../skills/slides-content/) | The orchestrator that chains all of the above | Copy per its README |
| [PPTX style guide](../style-guides/pptx/) | Only needed for the optional PowerPoint conversion | Copy per its README |

Each skill's README carries its own install steps; the table is the shopping list. After copying, restart Claude Code (or run `/skills`).

## The one-request path

Start Claude Code in the folder containing the paper and say:

> make slides from this paper

That triggers `slides-content`, which runs the chain end to end: split and deep-read the PDF, write the structured summary, generate and compile the Beamer deck, run the quality audit, and place the deliverable. It pauses once, after the PDF is done, to ask whether you also want PowerPoint.

Two optional arguments tune the deck:

- `structure=` picks the deck skeleton: `mba` (the default; a research-paper shape that opens with the methodology and a preview of the conclusions), `teaching`, `faculty`, `professional`, `consulting`, or `working`.
- `register=` picks the language level: `business` (the default; the paper's jargon is translated or glossed for a non-specialist audience) or `technical` (the paper's vocabulary is kept for a specialist room).

So `make slides from this paper structure=teaching register=technical` builds a lecture-shaped deck that keeps the source terminology.

If your papers live in a document library managed by the [knowledge-base](../skills/knowledge-base/) skill, there is a one-step wrapper for all of this; see "If you keep a document library" below.

## What happens, step by step

1. **Resolve the source.** A PDF is split into 4-page chunks and read inside a subagent; Word and RTF files are text-extracted; markdown, text, and LaTeX are read directly; a URL is fetched. The reading produces structured notes in the build folder.
2. **Reuse before re-reading.** If a `_text.md` extraction or a `_summary.md` already exists for this paper (from an earlier run or a knowledge-base pipeline), the skill reuses it and skips the expensive step. This is automatic; delete the file if you want a fresh pass.
3. **Summarize.** The skill detects whether the source is academic or general and applies the matching summary skill. The summary is both a standalone deliverable and the input that gives the deck its thematic structure.
4. **Generate and compile the deck.** The beamer skill plans the slide sequence from the structure skeleton, prefers charts and diagrams over bullet walls, compiles with two `pdflatex` passes, and fixes every layout warning.
5. **Audit.** An independent agent reads the compiled PDF and the LaTeX source against a published checklist: overlapping labels, clipped chart annotations, ugly hyphenation, years rendered as "2,024", citation placement, slide density. Findings are fixed and the deck recompiles before delivery.
6. **Deliver.** The deck lands in the paper's folder as `<paper>_slides.pdf`, with all working files in `<paper>_build/`. If you said yes to PowerPoint, the PPTX conversion follows the PPTX style guide and runs its own quality check.

## Time and cost

The deep read scales with the paper: a 90-page paper means roughly two dozen chunk reads inside the reading agent, and the audit agent reads every slide of the finished deck. A long paper is a long run; start it and let it work. Rebuilds are much cheaper, because the `_text.md` and `_summary.md` reuse rules skip the reading and summarizing entirely.

## If the first run fails to compile

The most common first-run failure is TeX: not installed, or installed but not on the PATH. The beamer skill checks for `pdflatex` before doing anything and stops with the install commands if it is missing; after installing TeX, restart Claude Code and rerun. Compile warnings and layout defects inside the run are the skill's job, not yours: the compile-fix-audit cycle resolves them before the deck is delivered.

## Rebuilds and edits

Running the flow again on a paper that already has a deck does not silently overwrite it: the existing PDF is backed up first, and the existing extraction and summary are reused.

For changes to a finished deck (reword a slide, fix a chart, add a finding), do not hand-edit the LaTeX source on your own. Say "edit the beamer slides" in the paper's folder: the beamer skill's edit mode loads the deck's context, takes your changes, recompiles, re-audits, and preserves each delivered version as a numbered snapshot (`v01`, `v02`, ...) so you can always go back.

## If you keep a document library

The [knowledge-base](../skills/knowledge-base/) skill wraps this entire flow in one command for a managed library: `kb slides <target>` takes a name fragment, a file path, or a URL; files a new item into the library first if needed; reuses the library's existing extraction and summary; hands off to the slides pipeline; and updates the library index afterward. If you read a lot of papers, the combination (inbox in, indexed library, slides on demand) removes every manual step between receiving a paper and presenting it.

## The manual path

The orchestrated path is the default, but each stage also runs on its own:

| Stage | Skill | Output |
|---|---|---|
| Deep-read the PDF | [split-pdf](../skills/split-pdf/) | reading notes, full-text extraction |
| Structured summary | [summary-academic](../skills/summary-academic/) | `<paper>_summary.md` |
| Build the deck | [beamer](../skills/beamer/) | `<paper>_slides.pdf` |

Use the manual path when you want only one of the artifacts (just a summary, say), or when you want to review the notes before any slides exist.

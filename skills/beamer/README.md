# Beamer Slide Generator

Generate production-quality LaTeX Beamer presentations from source content. The skill handles the complete workflow: audience triage, outline checkpoint, code-first figure generation, `.tex` authoring, compilation, and multi-agent quality audit.

---

## Problem

Converting research, reports, or structured notes into slides requires three things that are hard to do consistently at the same time: visual quality, narrative structure, and technical correctness (clean compilation, no layout defects). Ad-hoc Beamer generation produces decks that compile but look wrong (TikZ overlaps, year values formatted as "2,024", sourcecite citations displaced, bars not centered over labels). The audit checklist exists because these defects recur and are not reliably caught by visual inspection alone.

A second problem is mechanism selection. When everything is a TikZ diagram, the diagrams become harder to maintain and are no better looking than a well-styled booktabs table. This skill applies a decision matrix to route each slide to the right LaTeX mechanism before any `.tex` content is written.

---

## Approach

The skill follows a staged pipeline that separates planning from execution:

1. **Audience triage:** match the request to a domain pattern (teaching, faculty, professional, consulting, or working) that defines rhetoric balance, slide count range, density level, and which optional elements (Devil's Advocate slides, transition slides, code blocks) to include.
2. **Outline checkpoint:** produce a complete slide sequence with assertion titles and a figure plan before writing any `.tex` content. Wait for approval.
3. **Code-first figure generation:** for any figures identified as needing matplotlib (per the decision matrix in `figure_generation.md`), write and run standalone Python scripts before authoring the `.tex` file. pgfplots figures are authored inline.
4. **Figure extraction:** for figures that must be pulled from source PDFs, render, verify, and crop before writing any `.tex` content.
5. **`.tex` authoring:** copy the preamble verbatim from the style guide's Quick Reference section. Apply the visual mechanism decision table. Compute TikZ box heights from source before writing overlay text (do not rely on post-compilation visual inspection).
6. **Compilation cycle:** run `pdflatex` at least twice (required for `\sourcecite` overlay positioning). Fix all hbox/vbox warnings before proceeding.
7. **Quality audit:** launch one audit agent that reads the style guide, the audit checklist, the compiled PDF, and the `.tex` source, then checks every slide against every checklist item. Fix all findings and recompile.
8. **Deliverable placement:** copy `slides.pdf` to the parent folder as `<base_name>_slides.pdf`.

---

## Design Rationale

**Why pdflatex only:** The preamble uses `pdflatex`-compatible packages (`pgfplots`, `booktabs`, `colortbl`). Switching to lualatex or xelatex requires a font system incompatible with the `fontspec`-free setup, and the `\sourcecite` overlay uses `remember picture,overlay` which is sensitive to engine differences.

**Why two pdflatex passes:** The `\sourcecite{}` macro positions citations using a TikZ overlay with `remember picture,overlay`. This mechanism writes absolute page coordinates to the `.aux` file on the first pass and reads them back on the second. A single pass places the citation at coordinates from the previous run (or nowhere on a first compile), producing displaced citations.

**Why the empty-box-plus-overlay pattern:** Putting text inside a TikZ node with `minimum height` causes the node to expand beyond the minimum when content is tall enough. This produces non-uniform box heights in sibling groups. Drawing empty box nodes and overlaying text with a separate `\node[anchor=north west]` guarantees uniform box sizes regardless of content length. The pattern requires pre-computing content height before writing, which is why the checklist includes mandatory vertical arithmetic rather than visual inspection.

**Why `axis lines=left` with `axis on top`:** The default pgfplots axis draws a box (all four sides). On projected slides, this box reads as an unwanted border. `axis lines=left` draws only the left y-axis and bottom x-axis (L-shape). `axis on top` ensures bars do not visually cover the axis lines.

**Why no `symbolic x coords`:** Symbolic x coordinates prevent `xmin`/`xmax` padding from working correctly, making it impossible to ensure bars are fully contained within the chart boundary. Numerical coordinates with `xticklabels` produce reliable containment.

**Why `bar shift=0pt` per `\addplot`:** When multiple `\addplot` commands each draw a single bar at a different x-position (per-bar coloring), pgfplots treats each `\addplot` as a grouped series and applies a positional offset. Each bar shifts left or right of its label. `bar shift=0pt` forces each bar to render centered on its coordinate, overriding the grouped-series offset. The axis-level `ybar=0pt` option does not do this.

**Why the circuit breaker:** After three failed fix attempts on the same defect, the state of the `.tex` file degrades. Each attempt introduces side effects that obscure the original error. Stopping at three and reporting produces a recoverable state; continuing typically does not.

**Why one merged audit agent:** The former pipeline ran three separate agents (deck evaluation, graphics verification, quality checklist). Each agent had to load the full PDF and `.tex` source into context independently. A single agent reads the same files once and applies all three audit domains in one pass, producing equivalent findings at lower token cost.

---

## The Compilation Cycle

```
export PATH="/Library/TeX/texbin:$PATH"

# First pass: write .aux coordinates
pdflatex slides.tex

# (Optional) For Dropbox-synced directories, use a temp jobname:
# pdflatex -jobname=slides_tmp slides.tex

# Fix ALL hbox/vbox warnings before continuing.

# Second pass: read .aux and stabilize \sourcecite overlay positions
pdflatex slides.tex

# If bibtex/biber is used:
bibtex slides
pdflatex slides.tex
pdflatex slides.tex

# Recompile again if log reports "Label(s) may have changed"
```

The two-pass minimum is non-negotiable for any deck using `\sourcecite{}`.

---

## Usage

**From within Claude Code:**

```
beamer [content source] [audience=teaching|faculty|professional|consulting|working]
```

Provide one or more of:
- A `notes.md` file from a deep reading workflow (see `../split-pdf/SKILL.md`)
- A `summary.md` file from a summarization workflow
- Raw text or pasted content

If no audience is specified, defaults to **teaching lecture** (Logos 45% / Ethos 15% / Pathos 40%, 10-18 slides).

**Standalone invocation:** If invoked without source content, the skill asks what to build slides from.

**As part of a larger workflow:** If notes and a summary already exist in the working subdirectory (produced by an upstream skill), the skill reads them directly without prompting.

### Build directory convention

The skill expects a `_build/` subdirectory inside the project folder. Name it `<parent_folder_name>_build/`. For example, a project in `2026-03-ai-energy/` gets a build folder at `2026-03-ai-energy/2026-03-ai-energy_build/`. The deliverable PDF is placed in the parent folder as `<base_name>_slides.pdf`.

---

## Output

| File | Location | Description |
|---|---|---|
| `slides.tex` | `_build/` | Beamer source (authoritative) |
| `slides.pdf` | `_build/` | Compiled Beamer output |
| `outline.md` | `_build/` | Approved outline from checkpoint |
| `figures/` | `_build/` | Extracted and matplotlib-generated figures |
| `figures/originals/` | `_build/` | Full-page PDF renders at 300 DPI (for re-cropping) |
| `scripts/` | `_build/` | Standalone Python scripts for matplotlib figures |
| `<base_name>_slides.pdf` | Parent folder | Deliverable PDF (auto-placed) |

Build intermediates (`.aux`, `.log`, `.nav`, `.out`, `.snm`, `.toc`) remain in `_build/` and are not moved.

---

## Style Guide

Visual design is defined in `../../style-guides/beamer/style-guide.md`. Key specifications:

- **Document class:** `\documentclass[aspectratio=169,10pt]{beamer}`
- **Theme:** `\usetheme{default}` with all colors overridden (no other theme)
- **Font:** Beamer default sans-serif (Computer Modern Sans Serif); no `fontspec`, no `FiraSans`, no `lmodern`
- **Color palette:** 13 named colors including SlateNavy, DeepTeal, CyanBlue, DustyPlum, CharText, and MedGray (reserved for `\sourcecite` text and chart reference lines only)
- **Preamble:** copy verbatim from the Quick Reference section; do not reconstruct from memory
- **Citations:** `\sourcecite{}` macro with Chicago Author-Date format; no ad-hoc "Source: X" text
- **Overflow rule:** never use `[shrink=N]` on frames; never drop below `\small` for primary TikZ content; reduce content instead

The audit checklist in `audit-checklist.md` covers all style guide compliance checks, plus TikZ geometry checks, pgfplots axis containment checks, and narrative arc checks.

---

## Installation

1. Copy the entire `skills/beamer/` directory (which includes `SKILL.md`, `audit-checklist.md`, `domain_patterns.md`, and `figure_generation.md`) into `~/.claude/skills/beamer/`. All four files are needed; the audit checklist runs in the quality audit step, domain patterns drive audience triage, and figure generation guides matplotlib output.
2. Install TeX Live (or MacTeX on macOS) so `pdflatex` is on your `PATH`. The skill checks for `pdflatex` at the start of every run and stops if it is missing. Install instructions for each OS are in `SKILL.md` Step 0.
3. Copy `style-guides/beamer/style-guide.md` into the matching path on your system, or update the reference in `SKILL.md` to point at your own Beamer style guide.
4. Restart Claude Code (or run `/skills` to reload).
5. Trigger by saying "build a deck," "make a beamer presentation," or any other phrase listed under Usage.

## Acknowledgments

The code-first figure generation approach, audience-aware rhetoric patterns, Devil's Advocate slides, and transition slide conventions in this skill are adapted from **Scott Cunningham's** `beautiful_deck` skill. Scott Cunningham is Professor of Economics, Baylor University, and the author of *Causal Inference: The Mixtape*. His original work is available in the [MixtapeTools](https://github.com/scunning1975/MixtapeTools) repository.

- [LinkedIn](https://www.linkedin.com/in/scott-cunningham-7788912/)
- [GitHub](https://github.com/scunning1975)

The `\sourcecite{}` overlay macro, color palette, and quality audit checklist are original additions.

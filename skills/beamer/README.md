# Beamer Slide Generator

Generate production-quality LaTeX Beamer presentations from source content. The skill handles the complete workflow: structure and register triage, citation strategy decision, outline checkpoint with content inventory, code-first figure generation, `.tex` authoring, compilation, and a merged quality audit agent.

---

## Problem

Converting research, reports, or structured notes into slides requires three things that are hard to do consistently at the same time: visual quality, narrative structure, and technical correctness (clean compilation, no layout defects). Ad-hoc Beamer generation produces decks that compile but look wrong (TikZ overlaps, year values formatted as "2,024", sourcecite citations displaced, bars not centered over labels). The audit checklist exists because these defects recur and are not reliably caught by visual inspection alone.

A second problem is mechanism selection. When everything is a TikZ diagram, the diagrams become harder to maintain and are no better looking than a well-styled booktabs table. This skill applies a decision matrix to route each slide to the right LaTeX mechanism before any `.tex` content is written.

---

## Approach

The skill follows a staged pipeline that separates planning from execution:

1. **Structure and register triage:** match the request to a domain pattern (`structure=`: mba [default], teaching, faculty, professional, consulting, or working) that defines rhetoric balance, slide count range, density level, and which optional elements (Devil's Advocate slides, transition slides, code blocks) to include; and resolve the language level (`register=`: business [default] translates the source's domain jargon for a non-specialist reader, technical keeps it).
2. **Citation strategy decision:** state up front whether the deck is single-source (one paper or report drives 80 percent or more of slides; title-slide attribution, no per-slide citations) or multi-source (per-slide `\sourcecite{}` everywhere). Locks the strategy before slide writing so per-slide citations do not drift onto a single-source deck.
3. **Outline checkpoint:** produce a complete slide sequence with assertion titles, a figure plan, a source content inventory (Render / Compress / Drop per major table or figure with a reason for each Compress and Drop), and a citation strategy recap before writing any `.tex` content. Wait for approval.
4. **Code-first figure generation:** for any figures identified as needing matplotlib (per the decision matrix in `figure_generation.md`), write and run standalone Python scripts before authoring the `.tex` file. pgfplots figures are authored inline.
5. **Figure extraction:** for figures that must be pulled from source PDFs, render, verify, and crop before writing any `.tex` content.
6. **`.tex` authoring:** copy the preamble verbatim from the style guide's Quick Reference section. Apply the visual mechanism decision table. Compute TikZ box heights from source before writing overlay text (do not rely on post-compilation visual inspection).
7. **Compilation cycle:** run `pdflatex` at least twice (required for `\sourcecite` overlay positioning). Fix all hbox/vbox warnings before proceeding.
8. **Quality audit:** launch one audit agent (general-purpose, on a strong model) that reads the style guide, the audit checklist, the compiled PDF, and the `.tex` source, then checks every slide against every checklist item including deck-level checks (citation strategy consolidation, Limitations format). Fix all findings and recompile.
9. **Deliverable placement:** copy `slides.pdf` to the parent folder as `<base_name>_slides.pdf`.

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

**Why the audit runs on a strong model:** The audit is exhaustive rule application: scan every slide for every applicable pattern. Smaller models have been observed to spot-check rather than exhaustively apply, shipping defects the checklist had explicit rules for. A smaller tier is acceptable only for small decks (under 10 slides) with no TikZ boxes or charts.

**Why the outline checkpoint requires a source content inventory:** The most common information-loss pattern in this skill is silently collapsing two information-dense tables (for example, a "rises" table and a "falls" table, each with per-row magnitudes) into one categorical slide that strips the magnitudes. Requiring an explicit Render / Compress / Drop decision per major table or figure at outline time, with a one-line reason for each Compress and Drop, makes that decision visible and reviewable before any `.tex` is written.

**Why the citation strategy decision is its own step:** Single-source decks with `\sourcecite{}` repeated on every slide carry the same citation 15 times. The visual noise is significant. The audit can catch the pattern after the fact, but consolidating 14 of 15 slides post-audit forces a re-audit cycle. Deciding up front and pinning the choice into the approved outline prevents the drift.

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
beamer [content source] [structure=mba|teaching|faculty|professional|consulting|working] [register=business|technical]
```

Provide one or more of:
- A `notes.md` file from a deep reading workflow (see `../split-pdf/SKILL.md`)
- A `summary.md` file from a summarization workflow
- Raw text or pasted content

If no structure is specified, the skill defaults to **MBA / Executive** (Logos 50% / Ethos 25% / Pathos 25%, 8+ slides): the research-paper-to-slides skeleton that opens Title then Methodology then Summary and closes with Limitations, Conclusions, and Key Takeaways, each when appropriate. If no register is specified, it defaults to **business** (domain jargon translated or glossed for a non-specialist reader). The legacy `audience=` parameter still works as a deprecated alias for `structure=`.

**Standalone invocation:** If invoked without source content, the skill asks what to build slides from.

**As part of a larger workflow:** If notes and a summary already exist in the working subdirectory (produced by an upstream skill), the skill reads them directly without prompting.

### Working on an existing deck (edit, audit, and PPTX modes)

Generating a deck is the default. The skill also works on a deck it produced earlier through three additional modes:

- **Edit** (`mode=edit`, an edit/revise/fix trigger, or auto-detected when the working directory already contains a `*_build/slides.tex`): loads the existing source and context, presents a menu (edit, run the quality audit, or convert to PPTX), applies your changes, and runs the full compilation and audit cycle. If you report a visual defect, the skill reads the relevant slides, proposes a fix, and waits for approval before editing. Each delivered edit round is preserved as a numbered `vNN` version snapshot (PDF plus its paired `.tex`), so every version remains recoverable without Git.
- **Audit** (`mode=audit` or an audit trigger): re-runs the quality audit against an already-compiled deck and applies fixes, without other content changes. Useful for revisiting a deck after a pause.
- **PPTX** (`mode=pptx` or "convert to pptx"): converts the compiled PDF to a styled PowerPoint via the PPTX style guide workflow.

After any PPTX conversion, the skill offers an optional **PDF-vs-PPTX conversion audit**: a slide-by-slide comparison that flags text, numeric, table, chart, image, and citation divergences between the Beamer PDF and the saved PPTX, then asks how to handle each finding. This is report-and-ask, not auto-fix, because conversion divergences are often judgment calls.

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

1. Copy the entire `skills/beamer/` directory (which includes `SKILL.md`, `audit-checklist.md`, `domain_patterns.md`, and `figure_generation.md`) into `~/.claude/skills/beamer/`. All four files are needed; the audit checklist runs in the quality audit step, domain patterns drive the structure triage, and figure generation guides matplotlib output.
2. Install TeX Live (or MacTeX on macOS) so `pdflatex` is on your `PATH`. The skill checks for `pdflatex` at the start of every run and stops if it is missing. Install instructions for each OS are in `SKILL.md` Step 0.
3. Copy `style-guides/beamer/style-guide.md` into the matching path on your system, or update the reference in `SKILL.md` to point at your own Beamer style guide.
4. Restart Claude Code (or run `/skills` to reload).
5. Trigger by saying "build a deck," "make a beamer presentation," or any other phrase listed under Usage.

## Acknowledgments

The code-first figure generation approach, audience-aware rhetoric patterns, Devil's Advocate slides, and transition slide conventions in this skill are adapted from **Scott Cunningham's** `beautiful_deck` skill. Scott Cunningham is Professor of Economics, Baylor University, and the author of *Causal Inference: The Mixtape*. His original work is available in the [MixtapeTools](https://github.com/scunning1975/MixtapeTools) repository.

- [LinkedIn](https://www.linkedin.com/in/scott-cunningham-7788912/)
- [GitHub](https://github.com/scunning1975)

The `\sourcecite{}` overlay macro, color palette, and quality audit checklist are original additions.

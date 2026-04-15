---
name: beamer
description: Beamer slide generation with code-first figures, outline checkpoint, audience-aware rhetoric, Devil's Advocate slides, code blocks, and transition slides. Adapted from Scott Cunningham's beautiful_deck approach.
triggers: beamer, beamer slides, deck
allowed-tools: Bash(pdflatex*), Bash(xelatex*), Bash(lualatex*), Bash(latexmk*), Bash(bibtex*), Bash(biber*), Bash(python*), Bash(pip*), Bash(pdftoppm*), Bash(cd*), Bash(mkdir*), Bash(ls*), Bash(cp*), Bash(mv*), Bash(rm*), Bash(which*), Bash(type*), Bash(kpsewhich*), Bash(tlmgr*), Bash(texhash*), Bash(mactex*), Bash(mktexlsr*), Bash(fmtutil*), Bash(updmap*), Bash(brew*), Bash(find*), Bash(system_profiler*), Bash(fc-list*), Bash(sudo*), Bash(eval*), Bash(export*), Bash(cat*), Bash(grep*), Bash(head*), Bash(tail*), Bash(wc*), Read, Write, Edit, Glob, Grep, Task, Agent
argument-hint: [content-notes-or-summary] [audience=teaching|faculty|professional|consulting|working]
---

# Beamer Slide Generator

Generate an original Beamer presentation from source content (structured notes, summaries, or raw material). This skill handles the full cycle: audience triage, outline checkpoint, code-first figure generation, design, authoring the `.tex` file, compilation, and verification through multi-agent review.

Six additions from Scott Cunningham's beautiful_deck approach are integrated: code-first figures (matplotlib), an outline checkpoint, audience-aware rhetoric, Devil's Advocate slides, code blocks, and transition slides.

## Input

This skill expects one or more of:
- A `notes.md` file with structured extraction from a deep reading (for example, from `../split-pdf/SKILL.md`)
- A `summary.md` file with a structured summary
- Raw content, pasted text, or other source material

An optional `audience` parameter selects a domain pattern from `domain_patterns.md`: teaching (default), faculty, professional, consulting, or working. When omitted, defaults to teaching lecture.

If invoked standalone, ask the user what content to build slides from. If invoked as part of a slides workflow, notes and summary files will already exist in the working subdirectory.

## Working Directory

Save all output files in the current working subdirectory. If no subdirectory has been established, create one named after the source material (for example, `slides_smith_2024/`).

If figures are extracted from the source PDF, save them to `figures/` inside the working subdirectory, with original full-page renders in `figures/originals/`.

---

## Step 0: Verify LaTeX Installation

Before doing anything else, confirm that LaTeX and Beamer are installed and available in the PATH.

### Set up PATH for TeX

MacTeX installs to `/Library/TeX/texbin`. Claude Code sessions may not have this in the PATH by default. Always run this first:

```bash
export PATH="/Library/TeX/texbin:$PATH"
```

Then verify:
```bash
which pdflatex && pdflatex --version | head -1 && kpsewhich beamer.cls
```

### If pdflatex is still not found

Check alternate locations:
```bash
ls /Library/TeX/texbin/pdflatex 2>/dev/null
ls /usr/local/texlive/*/bin/*/pdflatex 2>/dev/null
```

If TeX binaries exist at a different path, add that path to PATH instead.

If no TeX installation is found at all, stop and tell the user:

> "LaTeX/MacTeX is not installed on this machine. Please install it by running these commands in your terminal:
> ```
> /bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
> brew install --cask mactex
> ```
> Then restart and try again."

Do not attempt to install MacTeX from within the agent because it requires `sudo` and interactive password entry.

### If everything is already installed

Proceed silently. Do not report to the user unless there was a problem.

---

## Step 0.1: Pre-flight Deliverable Check

Before writing any `.tex` file or compiling, check for existing deliverable PDFs that would be overwritten:

1. Check the parent directory (one level above the build directory) for any `*_slides.pdf` file.
2. Check the build directory for existing `slides.pdf` or `slides_tmp.pdf`.

If any deliverable PDF already exists, create a timestamped backup (`cp "<file>" "<file_without_ext> YYYY-MM-DD-HHMMSS.pdf"`) before proceeding, and report: "Backed up existing deliverable: [filename]"

If no deliverables exist, proceed silently.

**This step is non-negotiable.** Overwriting a deliverable without backup destroys work from previous sessions that may not be recoverable.

---

## Step 0.5: Audience Triage

Read `domain_patterns.md` (in this skill's directory).

If the user specified an `audience` parameter, load the matching pattern:
- `teaching` or `lecture` maps to **Teaching Lecture**
- `faculty` maps to **Faculty Development**
- `professional` maps to **Professional Audience**
- `consulting` or `workshop` maps to **Consulting Workshop**
- `working` maps to **Working Deck**

If no audience was specified, default to **Teaching Lecture**.

Report to the user which pattern is active:

> "Audience: [pattern name]. [One-line summary of rhetoric balance and slide count range from domain_patterns.md]."

For example:
> "Audience: Teaching Lecture. Logos 45% / Ethos 15% / Pathos 40%, targeting 10-18 slides."

Apply the audience-specific guidelines from the matched pattern throughout all subsequent steps: structural template, rhetoric balance, density, Devil's Advocate inclusion, code block inclusion, and transition slide inclusion.

---

## Design Requirements

**First action: use the Read tool to read these four files now, in order:**

1. `../../style-guides/writing-voice-guide.md` (or equivalent) -- slide-specific tone rules (factual titles, no over-narration, no selling the session, takeaway discipline)
2. `../../style-guides/beamer/style-guide.md` -- visual design: colors, fonts, templates, macros, chart styling, TikZ patterns, table formatting, slide type patterns, and the complete LaTeX preamble to copy verbatim from its Quick Reference section
3. `audit-checklist.md` (in this skill's directory) -- the quality audit checklist used in Step 3
4. `domain_patterns.md` (in this skill's directory) -- audience-specific guidelines for the active pattern

Do not write any `.tex` content before completing all four reads. Do not reconstruct the preamble from memory. The style guide is the single source of truth for visual design. Do not deviate from its color definitions, font settings, or template configurations.

Apply the audience-specific guidelines from the matched domain pattern throughout generation: structural template, rhetoric balance (logos/ethos/pathos), slide count range, density level, Devil's Advocate inclusion, code block inclusion, and transition slide inclusion.

---

## Step 0.7: Outline Checkpoint

**This checkpoint is mandatory.** Write a brief outline and present it to the user before proceeding. The outline must include:

1. **Audience and rhetoric balance:** The active domain pattern name and its logos/ethos/pathos percentages.
2. **Slide sequence with assertion titles:** One line per slide showing the slide number, assertion title, and slide type (for example: title, hook, finding, chart, table, diagram, code, Devil's Advocate, transition, takeaway, closing). Follow the structural template from the active domain pattern.
3. **Figure plan:** For each planned figure, indicate whether it will be:
   - **pgfplots** (inline in .tex)
   - **matplotlib** (standalone script, included as PDF)
   - **TikZ diagram** (inline in .tex)
   - **Extracted from source** (cropped from source PDF)

   Reference the decision matrix in `figure_generation.md` to determine which path each figure takes. Default to pgfplots; use matplotlib only when the figure exceeds pgfplots' comfortable range per the matrix.
4. **Devil's Advocate slide:** Whether included or omitted, and why (per the active domain pattern's rules).

Save the outline as `outline.md` in the build directory.

Show the outline to the user and **wait for approval** before proceeding. If the user requests changes, revise the outline, update `outline.md`, and re-present. Do not begin writing `.tex` content or generating figures until the user approves.

---

## Step 0.8: Code-First Figure Generation

Read `figure_generation.md` (in this skill's directory).

For each figure identified in the approved outline as needing **matplotlib**:

1. Create the `scripts/` directory in the build directory if it does not exist:
   ```bash
   mkdir -p scripts
   ```
2. Write a standalone Python script to `scripts/` following the conventions in `figure_generation.md`:
   - All imports at the top
   - Palette dict at the top (copy from `figure_generation.md`)
   - Data defined or loaded at the top
   - Figure construction in the middle
   - `plt.savefig()` at the bottom, saving to `../figures/<figname>.pdf`
   - Standalone: a reader can run it with `python3 scripts/<figname>.py` and reproduce the figure
3. Create the `figures/` directory if it does not exist:
   ```bash
   mkdir -p figures
   ```
4. Run the script to generate the figure PDF:
   ```bash
   python3 scripts/<figname>.py
   ```
5. Verify the figure renders correctly by reading the output PDF with the Read tool. Check:
   - Colors match the deck palette
   - Labels are legible at projection size
   - Axes match the slide background (white)
   - No chartjunk (unnecessary gridlines, borders, or axis marks)
   - If the figure has curved arrows with `connectionstyle='arc3'`, the Bezier helper functions from `figure_generation.md` are used for label placement

If any figure fails verification, fix the script and regenerate.

For figures that stay in **pgfplots**, proceed as normal (they will be authored inline in the .tex file during the content writing step). The decision matrix from `figure_generation.md` determines which path each figure takes.

If the approved outline has **no matplotlib figures**, skip this step entirely. No `scripts/` directory is needed.

---

## Content Requirements

The deck must cover the **key themes from all parts** of the source material. Do not skip or underweight any major section.

If the source material has an **Issues section** with substantive limitations, include a **"Limitations and Critique"** slide near the end of the deck (in Act III, before the closing). Present 2-3 of the strongest objections using the format: what a skeptic would say, why the concern is reasonable, and how it is addressed or acknowledged. The active domain pattern determines whether this slide is required, optional, or omitted:

- **Teaching Lecture:** Include when the source has an Issues section.
- **Faculty Development:** Include (faculty audiences are skeptical by nature).
- **Professional Audience:** Optional (depends on whether the talk makes a claim or reports findings).
- **Consulting Workshop:** Built into the exercise debrief framing; do not add a standalone slide.
- **Working Deck:** Not needed.

---

## Visual Mechanism Selection

**Before writing any slide content, classify each planned slide's content and select the appropriate LaTeX mechanism.** Do not default to TikZ for everything. The goal is beautiful, graphical slides, and the right mechanism for the content type produces better visuals than forcing everything into freeform TikZ placement.

### Decision rule

Every TikZ diagram must contain at least one element that cannot be represented as a list item or table cell: an arrow showing causation, a spatial position conveying meaning, a data-driven axis, or a geometric relationship between elements. If the slide content is a list of items rendered as labeled boxes without meaningful spatial relationships between them, use a table or formatted list instead.

### Mechanism by content type

| Content type | Signal | Mechanism | Example |
|---|---|---|---|
| **Spatial** (flows, timelines, cycles, hierarchies, cause-effect) | "A leads to B", process steps, directional relationships | TikZ diagram | Process flow, technology adoption lifecycle |
| **Quantitative** (data series, distributions, comparisons by magnitude) | Numbers, percentages, trends over time | pgfplots chart | Agreement rates by round, ROI comparison bars |
| **Tabular** (structured comparisons, multi-attribute data, problem/solution pairs) | Rows and columns, parallel structure across items | booktabs table with colored cells, `\rowcolor`, `$\to$` arrows | Failure modes with fixes, feature comparison matrix |
| **Sequential** (ranked items, numbered priorities, key takeaways, lessons learned) | "Five priorities", "three lessons", ordered list without spatial relationships | enumerate/itemize with styled formatting (colored numbers, bold lead text, `\itemsep` for rhythm) | Five priorities, key takeaways |
| **Mixed** (explanatory text alongside a visual) | Description plus diagram, narrative plus chart | Two-column: text column uses the appropriate text mechanism, visual column uses TikZ or pgfplots | Case study description plus calculation chain |
| **Code** (API calls, scripts, prompts, tool configurations) | Code in the source content, programming examples, API usage | listings environment (from style guide) | Skill structure, Python API call, prompt template |

### What "graphical" means for non-TikZ mechanisms

Tables and formatted lists are visual representations when properly styled:
- A booktabs table with alternating `PaleBlue` row shading, colored header cells, and icon-like symbols (`$\to$`, `$\checkmark$`, `$\times$`) is graphical.
- An enumerate list with `DeepTeal` numbered items, `SlateNavy` bold lead text, and generous `\itemsep` spacing is graphical.
- A two-column layout with a styled text block and a chart is graphical.

"Graphical" means the slide communicates visually, not that every slide contains a TikZ diagram. Five colored boxes stacked vertically with no arrows or spatial relationships is not more graphical than a well-formatted table; it is a table that is harder to maintain and more likely to render with non-uniform heights.

---

## Number Formatting

**Years must never have comma separators.** "2024" not "2,024". This is a common LaTeX problem that occurs in multiple contexts. Apply all of the following preventive measures:

- **pgfplots axis labels:** Always disable thousand separators on any axis that displays years:
  ```latex
  /pgf/number format/.cd, set thousands separator={}
  ```
  Or per-axis: `xticklabel style={/pgf/number format/1000 sep={}}`

- **siunitx:** If using `siunitx`, configure it to not group year-like numbers. Prefer writing years as plain text (`2024`) rather than `\num{2024}`.

- **Tables and text:** Never wrap years in `\num{}` or any number-formatting macro. Write years as literal text.

- **pgfplotstable:** If using `pgfplotstable`, set `columns/year/.style={int detect, 1000 sep={}}` or similar.

This applies to all four-digit years anywhere in the deck: axis labels, table cells, slide text, figure annotations, and captions.

---

## Quality Standards

- **Consistent narrative flow** with technical rigor maintained throughout
- **Optimal cognitive density:** distribute content evenly across slides so that no individual slide is overloaded, but the deck as a whole covers the material thoroughly
- **Right mechanism for the content:** use the Visual Mechanism Selection table above (TikZ for spatial relationships, pgfplots for data, booktabs for structured comparisons, enumerate for sequential items); every slide should fill its available space effectively
- **Beautiful figures:** create high-quality TikZ diagrams, charts, and visual representations; use appropriate chart types (bar, line, scatter, etc.) for the data being presented
- **Beautiful tables:** well-formatted tables with clean typography and appropriate spacing
- **Images from the source:** include figures or images from the source material when they are informative and reproducible
- **Data visualization:** prioritize clear, accurate visual representation of quantitative findings

---

## Figure Extraction

**Complete this step before writing any `.tex` content.** Review the notes and source material to inventory every figure that will appear in the deck, decide how each will be handled, then extract any that require it.

Note: This step handles figures pulled from source documents. Code-first figure generation (Step 0.8) handles newly created matplotlib figures. Both may apply to the same deck.

### Decision Criteria

| Figure type | Handling |
|---|---|
| Simple chart (bar, line, scatter, box plot) with data extractable from the source | **Recreate in pgfplots** (matches deck palette, fully editable, projects well) |
| Multi-panel figure where each panel is a simple chart | **Recreate if 1-2 panels; extract if 4+** (diminishing returns on recreation effort) |
| Complex chart (choropleth map, many overlapping visual elements) | **Extract from source PDF** |
| Figure where the paper's own color encoding carries the meaning (party-line colors, heatmaps, categorical color maps) | **Extract from source PDF** (color encoding must be preserved) |
| Photograph (person, place, object, interface screenshot, physical phenomenon) | **Always extract** (cannot be recreated in TikZ) |
| Time series with annotations (reference lines, labeled periods, event markers) | **Recreate in pgfplots** (annotations need deck-palette colors and readable font sizes) |

**Color trade-off:** Extracted figures retain the paper's own color scheme, which typically will not match the deck palette. When color consistency matters more than exact reproduction, prefer pgfplots recreation. When the paper's visual encoding must be preserved, extract and accept the color mismatch.

**Projection readability:** Extracted figures were designed for printed pages (letter/A4, read at arm's length). When projected on a screen, axis labels, legends, and annotations are often too small to read. This is the strongest reason to prefer recreation for simple charts: pgfplots charts use the deck's font sizes and are legible when projected.

### If No Figures Need Extraction

If all figures in the deck will be recreated in TikZ/pgfplots or generated by matplotlib scripts (Step 0.8), skip this step and proceed to the Compilation Cycle. No `figures/` directory is needed unless matplotlib scripts already created one.

### Chart Recreation from Source

When recreating a paper's chart in pgfplots:

**Data extraction:** Academic papers typically provide enough information to approximate key data points: tables with exact values, text describing specific numbers, or axis ranges visible in the original figure. Use these to construct coordinate lists. Label approximated values with a comment: `% approximated from figure`.

**Annotation patterns for labeled periods or generations:**
- Use short dashed line segments spanning only the relevant time window, not full-width lines. Full-width dashed lines create visual clutter, especially when multiple reference levels are close together.
- Color each segment and label to match the deck palette's semantic assignment for that category.
- Position labels to avoid crossing the main data line. Use `anchor=south` for labels above the line, `anchor=north` for below.

**Common pitfalls from experience:**
- Full-width reference lines at similar y-values visually merge and obscure the data line. Use short segments scoped to each category's active period.
- Labels placed with `anchor=west` at the right edge of the chart get clipped. Add padding to `xmax` or position labels inside the chart area.
- Smooth time series need enough coordinate points (every 2-3 years) to avoid angular segments, especially at inflection points.

### Extraction Pipeline

For each figure to extract, work in the build directory.

**1. Create the figures directory**

```bash
mkdir -p figures/originals
```

**2. Render the page and visually verify before cropping**

```bash
pdftoppm -r 300 -png -f <page_num> -l <page_num> <path_to_source_pdf> figures/originals/<figname>
```

**CRITICAL: Read the rendered PNG with the Read tool before cropping.** Do not assume the page number from text annotations is correct; PDF page numbers in text files can be offset from physical pages. Visual verification catches:
- Wrong page (references section instead of figure)
- Multiple figures on one page (requires manual crop coordinates, not whitespace detection)
- Figure title and source notes that should be excluded from the crop

**3. Crop to the chart area only**

The goal is to include the chart axes, data, and legend, but exclude:
- The figure title unless needed for context
- Source notes and methodology text below the chart
- Page numbers and headers

For single-figure pages: whitespace detection may work as a starting point, but always verify the result visually and trim source notes manually if included.

For multi-figure pages: use manual pixel coordinates. After reading the rendered PNG, estimate the vertical position of each figure as a fraction of page height and crop with PIL:

```python
from PIL import Image
img = Image.open('figures/originals/page-35.png')
w, h = img.size
# Figure 3 is the bottom chart on this page, roughly 50-75% of page height
fig3 = img.crop((40, int(h*0.50), w-40, int(h*0.75)))
fig3.save('figures/fig3_income_curves.png')
```

Iterate on the crop bounds until the chart fills the image without source notes or adjacent figures.

**4. Verify aspect ratio for 16:9 slides**

After cropping, check the image dimensions. A crop wider than 3:1 will render as a narrow strip on a 16:9 slide. If the chart is very wide and short (for example, two side-by-side panels), accept the aspect ratio rather than adding whitespace, but use `height=0.68\textheight,keepaspectratio` to prevent overflow:

```latex
\includegraphics[width=0.85\textwidth,height=0.68\textheight,keepaspectratio]{figures/fig3_name}
```

Always include both `width` and `height` with `keepaspectratio` for extracted figures. Without the height constraint, tall images overflow the frame.

**5. Name and reference**

- Cropped figures: `figures/fig<N>_<descriptive_name>.png`
- Original page renders: `figures/originals/` (preserved for re-cropping)
- Reference in `.tex`: `\includegraphics[width=0.85\textwidth,height=0.68\textheight,keepaspectratio]{figures/fig3_mechanism}`

---

## Compilation Cycle

### Step 1: Validate Any Existing Work, Write, and Compile

**If `slides.tex` already exists** in the working directory (that is, this session is continuing prior work), validate its preamble before touching anything:
- Confirm `\usetheme{default}`; if any other theme (Madrid, Warsaw, Berlin, etc.) is present, stop and notify the user before continuing
- Confirm `aspectratio=169` in the document class options
- Confirm no `fontspec`, `\setmainfont`, or `luatexja` (markers of lualatex-specific code incompatible with the style guide)

If any check fails, report the violation to the user and ask how to proceed. Do not silently continue with a broken preamble.

1. Write the complete `.tex` file, copying the preamble verbatim from the Quick Reference section of `../../style-guides/beamer/style-guide.md`.
   - **TikZ overlay box constraint:** When using the empty-box-plus-overlay pattern (or any TikZ node with `minimum height` and separate text overlay), compute content height before writing the overlay content. Calculate `chars_per_line = (text_width - indent) / avg_char_width` (1.7mm for `\footnotesize`, 1.5mm for `\scriptsize`), write each item to fit within that count, then verify total content height < `minimum_height - top_shift`. If content does not fit, shorten text or increase box height; never rely on post-compilation visual inspection to catch overflow.
2. Compile with `pdflatex` at least twice. The `\sourcecite{}` macro uses `remember picture,overlay`, which requires two passes to stabilize absolute page coordinates. A single pass will produce incorrect citation placement on new or restructured slides. Always run: `pdflatex` (first pass, writes coordinates to `.aux`), then `pdflatex` (second pass, reads coordinates and places nodes correctly). Do not use lualatex or xelatex. The style guide's preamble uses pdflatex-compatible packages and is incompatible with lualatex's fontspec-based font loading. If you encounter a font error, fix it within pdflatex constraints rather than switching compilers.
3. Run `bibtex`/`biber` if references are used, then add a third `pdflatex` pass.
4. Recompile further if the log reports "Label(s) may have changed."
5. **Dropbox-synced directories:** If the working directory is inside a Dropbox-synced folder, compile to a temporary filename (`pdflatex -jobname=slides_tmp slides.tex`) to prevent Dropbox from silently overwriting the output during rapid edit-compile cycles. After verifying the output, copy the temporary file to the final `slides.pdf` location.

### Step 2: Fix Compilation Warnings

After initial compilation, review the log file and fix **ALL**:
- Overfull `\hbox` warnings
- Underfull `\hbox` warnings
- Overfull `\vbox` warnings
- Underfull `\vbox` warnings

No matter how small. Every single one.

Common fixes:
- Adjust text width, margins, or column widths
- Reword text to fit line breaks
- Adjust `\parbox` or `minipage` widths
- Fix spacing commands

**Compression limit:** If fixing overfull warnings on a single slide requires more than two compression passes (reducing font size, shrinking spacing, narrowing widths), stop compressing. The slide is overloaded. Restructure instead: split into two slides, simplify the diagram, replace a dense TikZ diagram with a table or two-column layout, or change the visual mechanism. Repeated compression produces illegible slides that pass compilation but fail visual review.

Recompile and verify all warnings are eliminated.

### Step 3: Quality Audit (Merged)

After the deck compiles cleanly, perform a **comprehensive quality audit** of the final PDF and `.tex` source. This audit is not optional; it must happen every time. This single audit replaces the former three-agent pipeline (deck evaluation, graphics verification, quality audit) to avoid loading the full source into context three times.

Launch **one audit agent** (using the Agent tool) that reads these files before examining any slides:
1. The **Beamer Style Guide** at `../../style-guides/beamer/style-guide.md`
2. The **audit checklist** at `audit-checklist.md` (in this skill's directory)
3. The full compiled PDF (all pages)
4. The `.tex` source

The agent checks every slide against every item in the audit checklist, covering all three former audit domains in a single pass:

**Deck evaluation** (narrative and design):
- Narrative flow, logical consistency, and technical rigor
- Cognitive density balance (no slide too dense, no slide too sparse)
- Design originality and professionalism
- `\highlight{}` inside `itemize` or `enumerate` (style violation; replace with `\textbf{\color{DeepTeal}...}`)

**Graphics verification** (charts and diagrams):
- Label positioning errors (overlapping, clipped, outside visible area)
- Coordinate placement errors and bounding box arithmetic for TikZ node overlap
- Numerical accuracy against source material
- Axis containment, scaling, `axis lines=left` with `axis on top`, no `clip=false`, no `symbolic x coords`
- Frame shrink prohibition (no `[shrink=N]`)
- `nodes near coords` formatting (`/pgf/number format/fixed`)
- Brace and annotation collisions (account for amplitude and label height)
- Dual-label collisions (`nodes near coords` combined with manual `\node` annotations)
- Diagram centering (parent elements centered over children)
- Color and readability

**Checklist audit** (all items in `audit-checklist.md`):
- Sourcecite clearance, hyphenation, text overflow, citation strategy, style guide compliance, and all other checklist items

The agent returns a structured report.

#### Report Format

Present the audit results to the user as a slide-by-slide list. Only list slides with issues; skip clean slides:

> **Quality Audit: [N] issues found across [M] slides:**
>
> - **Slide 3** "Title of Slide": bar chart x-axis labels extend beyond right edge of frame; "methodology" hyphenated awkwardly in subtitle
> - **Slide 7** "Title of Slide": TikZ flow diagram arrow from node 3 to node 4 is clipped; left column text overlaps the column divider
> - **Slide 12** "Title of Slide": table values show 2,024 instead of 2024; title is generic ("Data Overview"), should state the finding

If the audit finds **zero issues**, report:

> **Quality Audit: all [N] slides clean. No issues found.**

Then proceed to Output.

Proceed immediately to Step 4 to fix all reported issues. Do not pause for user confirmation. The audit findings are objective defects with one correct fix each; no decision gate adds value here.

### Step 4: Fix and Recompile

Fix all reported issues in the `.tex` source. Then:

1. Recompile.
2. Verify the log is clean (no new hbox/vbox warnings introduced).
3. **Re-read every slide that was fixed** and verify each original issue is resolved (do not assume the fix worked). For each fixed issue, confirm:
   - The specific element that was wrong is now correct
   - The fix did not introduce a new collision, overlap, or layout problem nearby
   - For legend repositioning: verify the legend does not still overlap data at its new position
4. **Cross-category re-verification:** if a fix changed an element's position, re-check that element against all other applicable checklist categories. A fix that resolves one issue but creates another counts as a new finding and must be fixed before finalizing.

If fixes introduced new problems, fix those too before finalizing.

#### Circuit Breaker

After three different fix attempts on the same compile error or audit defect, **stop editing**. Do not attempt a fourth approach. Instead, report to the user:

1. The specific error or defect
2. What three approaches were tried
3. Why each attempt failed or introduced new problems

Ask the user how to proceed. The cost of stopping is two minutes. The cost of spiraling is an hour and a .tex file that is worse than after attempt two, because each fix introduces side effects that obscure the original error.

This limit applies per-error, not per-cycle. If the audit reports five defects and three are fixed cleanly but one resists three attempts, stop on that one and report. Do not abandon the fixes that worked.

After the final clean compile, report what the audit found and what was changed:

> **Audit fixes applied ([N] issues across [M] slides):**
> - Slide 3: [what was fixed]
> - Slide 7: [what was fixed]
> - ...

If the audit found zero issues, no report is needed; proceed silently to Output.

---

## Output

### Build artifacts (stay in `_build/`)

- `slides.tex` (the Beamer source)
- `slides.pdf` (the compiled output)
- `outline.md` (the approved outline from Step 0.7)
- `figures/`: extracted figures from the source (if any were embedded) and matplotlib-generated figures (if any)
- `figures/originals/`: full-page PDF renders at 300 DPI (preserved for re-cropping)
- `scripts/`: standalone Python scripts for matplotlib-generated figures (if any)
- `tables/`: `.tex` table fragments (if any were generated separately)
- `.aux`, `.log`, `.nav`, `.out`, `.snm`, `.toc` (LaTeX intermediates)

### Deliverable PDF (auto-placed in parent folder)

After successful compilation, always copy `slides.pdf` from the build directory to its parent folder with a standardized name:

1. Take the build directory name (for example, `ai-energy-detailed-slides_build`)
2. Strip the `_build` suffix to get the base name (for example, `ai-energy-detailed-slides`)
3. Copy as `<base_name>_slides.pdf` into the parent folder

This applies to all invocations (standalone and called by workflows). When a calling workflow provides an explicit content name that differs from the build directory base name, the calling workflow's name takes precedence.

**Example:**
```
my_project/                              <-- parent folder
  topic_a_slides.pdf                     <-- deliverable (auto-placed by beamer)
  topic_a_build/                         <-- build directory
    slides.tex
    slides.pdf
    outline.md
    figures/
    scripts/
```

**Confirm with the user:** "Beamer slides compiled and verified. Deliverable saved as `<base_name>_slides.pdf`. Ready to convert to PowerPoint?" (if part of a slides workflow) or "Beamer slides complete. Deliverable saved as `<base_name>_slides.pdf`." (if standalone).

**PPTX conversion:** When converting to PowerPoint, follow the Beamer-to-PPTX Conversion Workflow in `../../style-guides/pptx/style-guide.md` exactly. This includes reading the .tex source and PDF, creating a per-slide conversion plan with native/hybrid/image categorization, presenting the plan for approval, using all font size specifications (18pt body floor, 14pt table/chart floor), calling the quality check function before saving, and fixing all reported issues before the file is written. Do not write ad-hoc conversion code that bypasses this workflow.

---

## Session Log

After the deliverable is confirmed (and after optional PPTX conversion), append a session log entry to `CLAUDE.local.md` in the project root (the parent of the build directory). If `CLAUDE.local.md` does not exist, create it with a header first.

**Entry contents:**
```markdown
## [YYYY-MM-DD] - Beamer slides: [topic/description]
- **Skill:** beamer
- **Files created/modified:** [build directory path, slides.pdf deliverable path, PPTX if generated]
- **Key decisions:** [source content used, slide count, audience pattern, any notable design choices]
- **Status:** complete
- **Next steps:** [none, or note if user mentioned future edits]
```

**Handoff trigger:** If this session involved troubleshooting (Step 4 Fix and Recompile was used, or multiple compilation rounds were needed), ask:

> "This session involved troubleshooting. Write a handoff for the next session?"

If the session was a clean single-pass compilation, do not ask. Just log the entry silently.

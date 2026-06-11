# Beamer Style Guide

LaTeX Beamer presentation formatting for 16:9 slide decks with TikZ figures, pgfplots charts, and structured data visualizations.

## Requirements

### LaTeX Distribution

You need a working TeX Live (or MacTeX on macOS, MiKTeX on Windows) installation with `pdflatex` available on your PATH.

**macOS (recommended):**
```bash
brew install --cask mactex
```
After installation, restart your terminal. Verify with:
```bash
pdflatex --version
```

**Linux (Ubuntu/Debian):**
```bash
sudo apt install texlive-full
```

**Windows:**
Download and install [MiKTeX](https://miktex.org/download) or [TeX Live](https://tug.org/texlive/).

### Required LaTeX Packages

These are included in a full TeX Live installation. If you use a minimal install, add them:

| Package | Purpose |
|---------|---------|
| `beamer` | Presentation document class |
| `tikz` | Diagrams, flowcharts, comparison layouts |
| `pgfplots` | Bar charts, line charts, scatter plots |
| `booktabs` | Professional table formatting |
| `listings` | Code block formatting |
| `array`, `colortbl`, `multirow` | Advanced table layouts |
| `ragged2e` | Text alignment in TikZ nodes |
| `graphicx` | Image inclusion |
| `amsmath`, `amssymb` | Mathematical notation |

TikZ libraries used: `arrows.meta`, `positioning`, `calc`, `patterns`, `decorations.pathreplacing`, `shapes.geometric`

### Python (for PDF splitting and PPTX conversion)

Python 3.8+ is required for two optional steps in the slides pipeline:

```bash
pip install PyPDF2 python-pptx
```

| Library | Used By | Purpose |
|---------|---------|---------|
| `PyPDF2` | [split-pdf](../../skills/split-pdf/) skill | Splitting large PDFs into 4-page chunks |
| `python-pptx` | [PPTX style guide](../pptx/) | Converting Beamer output to PowerPoint |

These are optional. If you only want to produce PDF slide decks, you need only the LaTeX distribution.

## Deployment

### First-time setup

1. Install the LaTeX distribution (see above)
2. Install Python packages if you plan to use split-pdf or PPTX conversion
3. Copy [style-guide.md](style-guide.md) to your Claude Code skills reference location (or leave it in the repo and point your beamer skill to it via relative path)
4. Copy the [beamer skill](../../skills/beamer/) to `~/.claude/skills/beamer/`
5. Test with a simple invocation: ask Claude Code to "make a 3-slide deck about [any topic]"

### Verifying the installation

```bash
# Check LaTeX
pdflatex --version

# Check Python packages
python3 -c "import PyPDF2; print('PyPDF2', PyPDF2.__version__)"
python3 -c "import pptx; print('python-pptx', pptx.__version__)"
```

### Compilation workflow

The beamer skill compiles slides using this sequence:

```bash
pdflatex -interaction=nonstopmode -halt-on-error slides.tex
pdflatex -interaction=nonstopmode -halt-on-error slides.tex  # second pass for cross-references
```

Two passes are required because TikZ `[remember picture, overlay]` nodes (used for `\sourcecite{}` positioning) need a second compilation to resolve absolute page coordinates.

## What the Style Guide Contains

The [style-guide.md](style-guide.md) file is a technical reference document with:

- **Color palette:** 13 named colors with hex values and semantic roles
- **Complete preamble:** Ready to copy verbatim into a new `.tex` file
- **Theme configuration:** `\usetheme{default}` with full color overrides
- **Custom macros:** `\highlight{}` for TikZ labels, `\sourcecite{}` for citations, `\callout{}` for reinforcement boxes, `\placement{}` for deletable review notes
- **Callout vocabulary:** Four callout styles with color-by-message-valence and white-text contrast rules
- **pgfplots rules:** Axis configuration, legend placement, bar chart containment, stacked bar ordering, annotation recipes
- **TikZ conventions:** Empty-box-plus-overlay pattern, overflow height computation, sibling-node uniformity, freeform path clearance
- **Slide type patterns:** Dark accent slides, key takeaways, two-column layouts, data tables
- **Cognitive density rules:** Title conventions, fill-first font sizing, frame under-fill management, when to use tables vs. TikZ, what to avoid

## Customization

See the [parent README](../README.md) for how to adapt colors, fonts, and layout constants to your institution.

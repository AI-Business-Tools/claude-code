# Diagram Style Guide

TikZ diagram formatting for standalone PDF diagrams: colors, typography, node styles, arrow styles, layout spacing, and legend conventions. Used by the [diagram-pdf](../../skills/diagram-pdf/) skill.

## Requirements

### LaTeX Distribution

You need a working TeX Live (or MacTeX on macOS, MiKTeX on Windows) installation with `pdflatex` available on your PATH.

**macOS (recommended):**
```bash
brew install --cask mactex-no-gui
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
| `tikz` | Diagrams, arrows, positioning |
| `standalone` | Document class that crops the PDF to diagram content |

TikZ libraries used: `arrows.meta`, `positioning`, `calc`, `decorations.pathreplacing`, `shapes.geometric`, `fit`

## Deployment

### First-time setup

1. Install the LaTeX distribution (see above).
2. Copy [style-guide.md](style-guide.md) to your Claude Code skills reference location, or leave it in the repo and point the `diagram-pdf` skill to it via relative path. The skill's Step 2 reads this file.
3. Copy the [diagram-pdf skill](../../skills/diagram-pdf/) to `~/.claude/skills/diagram-pdf/`.
4. Test with a simple invocation: ask Claude Code to "create a diagram of a three-step pipeline with an input and an output on each step."

### Verifying the installation

```bash
pdflatex --version
```

### Compilation workflow

The diagram-pdf skill compiles diagrams using this sequence:

```bash
pdflatex -interaction=nonstopmode diagram.tex
```

Single pass is sufficient. For diagrams with feedback loops or complex routing, the skill uses a two-phase procedure documented in the skill's Step 3.

If working in a cloud-synced directory (Dropbox, iCloud Drive, OneDrive), compile to a temporary jobname first, then copy the PDF to the final location. This avoids sync-lock collisions that can corrupt the output file.

## What the Style Guide Contains

The [style-guide.md](style-guide.md) file is a technical reference document with:

- **Color palette:** 12 named colors with hex values and semantic role assignments (primary node, secondary node, input, output, context, milestone, and more)
- **Document class and packages:** `standalone` with 16pt border and the required TikZ libraries
- **Typography:** Font specifications for titles, node text, labels, and annotations
- **Node styles:** Complete TikZ style definitions for pipeline nodes, input/output boxes, context boxes, milestones, orchestrator nodes, and thematic cluster nodes
- **Arrow styles:** Main flow, optional path, side entry, feedback loop, and label styles
- **Layout rules:** Spacing constants for all layout types, side-entry positioning, feedback corridor routing
- **Legend and title conventions:** Two-column legend format, title and subtitle positioning

## Customization

See the [parent README](../README.md) for how to adapt colors, fonts, and layout constants to your brand.

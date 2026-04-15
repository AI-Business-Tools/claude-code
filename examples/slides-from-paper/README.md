# Example: Slides from Paper

This example demonstrates the output of the [slides-content](../../skills/slides-content/) pipeline.

## What the Pipeline Produces

When you give `slides-content` a source document (PDF, markdown, or text), it produces:

1. **Structured reading notes** (`_notes.md`): key themes, findings, data points, and quotations extracted from a deep read of the source
2. **Outline** (`outline.md`): proposed slide sequence with one-line descriptions, reviewed before generation
3. **Beamer source** (`slides.tex`): LaTeX file with TikZ figures, comparison diagrams, pipeline visualizations, and data charts
4. **Compiled PDF** (`slides.pdf`): the rendered presentation after the four-step compile-audit-fix cycle
5. **PPTX** (optional): PowerPoint conversion using the PPTX style guide, with native shapes or image embeds

## Typical Slide Types

A deck generated from an academic paper typically includes:

- **Three-card reading summary**: key themes from the source, one card per major section
- **Comparison slides**: two-column layouts for contrasting concepts (e.g., traditional vs. AI-assisted)
- **Pipeline diagrams**: horizontal or vertical node chains showing multi-step processes
- **Data visualizations**: pgfplots charts recreated from tables or figures in the source
- **Key takeaways**: numbered list of 3-4 main conclusions

## Quality Gates Applied

Every deck passes through:

1. **Compile**: `pdflatex` run twice for cross-references
2. **Warning check**: underfull/overfull boxes flagged and fixed
3. **Merged audit**: style compliance, source citations, overlay positioning, font size minimums, content overflow
4. **Fix and recompile**: defects fixed and recompiled until clean

## Note on Source Material

The source paper is not included in this example because academic papers are typically copyrighted. To try the pipeline yourself, point `slides-content` at any PDF, markdown file, or text document in your project folder.

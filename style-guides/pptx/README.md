# PPTX Style Guide

PowerPoint presentation formatting using python-pptx, including a Beamer-to-PPTX conversion workflow.

## Requirements

### Python

Python 3.8+ with the `python-pptx` library:

```bash
pip install python-pptx
```

Verify:
```bash
python3 -c "import pptx; print('python-pptx', pptx.__version__)"
```

### PowerPoint Template

The style guide expects a `.pptx` template file with:
- A "Title Only" slide layout (used as the base for all content slides)
- 16:9 aspect ratio (13.333" x 7.5")
- Your institutional branding (logo, footer, colors) pre-applied to the template

Set the `TEMPLATE_PATH` variable in [style-guide.md](style-guide.md) to point to your template file.

## Setup

1. Install python-pptx (see above)
2. Create or obtain a `.pptx` template with your branding
3. Copy [style-guide.md](style-guide.md) to your Claude Code skills reference location
4. Update `TEMPLATE_PATH` in the style guide to point to your template
5. Update the color palette hex values if your institution's colors differ from the defaults

## What the Style Guide Contains

The [style-guide.md](style-guide.md) file is a technical reference document with:

- **Typography targets:** 36pt titles, 22-24pt body, 18pt hard floor, 14pt chart axes
- **Layout constants:** Content area boundaries, footer zone, margin rules
- **Color palette:** Matching the Beamer guide, with PPTX-specific usage notes
- **Template loading pattern:** How to load the template, remove placeholder slides, and create content slides
- **Beamer-to-PPTX conversion workflow:** Four-step process with decision rules for native shapes vs. image embed
- **Helper functions:** `add_citation()`, `add_image_proportional()`, `fix_chart_fonts()`, `fix_table_fonts()`, `set_bullet()`, `set_hanging_indent()`, `estimate_text_height()`
- **Chart rules:** Legend positioning, negative-value bar handling, number format requirements
- **`run_quality_check(prs)` function:** 14 automated checks (bounds, overlap, chart fonts, legend position, table styles, vertical alignment, text overflow, and more)
- **Implementation checklist:** Final verification before saving

## Customization

See the [parent README](../README.md) for how to adapt colors, fonts, and layout constants to your institution.

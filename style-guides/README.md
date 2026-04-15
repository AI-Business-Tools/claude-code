# Style Guides

Skills in this repository reference style guides to produce consistent formatting across all generated deliverables. Rather than embedding formatting rules inside each skill, the rules live here as shared documents. Update a color, font, or layout constant in one place and all skills pick up the change automatically.

## Available Guides

| Guide | What It Covers | Setup |
|-------|---------------|-------|
| [Beamer](beamer/) | LaTeX Beamer presentations: color palette, typography, TikZ conventions, chart styling | Requires TeX Live and Python |
| [PPTX](pptx/) | PowerPoint formatting: layout constants, conversion workflow from Beamer, quality checks | Requires Python and python-pptx |

## Customizing for Your Institution

Both guides use a named color palette and explicit constants. To adapt them:

- **Colors:** Replace hex values in the palette section. Keep the color names (SlateNavy, DeepTeal, etc.) unchanged so all referencing code continues to work.
- **Fonts:** Beamer uses Computer Modern Sans Serif (default). PPTX uses Calibri. Replace font names in the relevant guide.
- **Template file:** The PPTX guide references a master `.pptx` template. Replace `TEMPLATE_PATH` with the path to yours.
- **Layout constants:** Adjust margins, footer zones, and content area boundaries if your template differs from the defaults.

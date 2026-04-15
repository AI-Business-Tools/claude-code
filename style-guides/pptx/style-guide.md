# PowerPoint Style Guide

Apply this style guide when creating PowerPoint presentations. Follow all specifications exactly.

## Critical Rules (Most-Violated, Read First)

These five rules are violated in nearly every PPTX generation. They override any conflicting code example or default assumption elsewhere in this file.

1. **Body text targets 22-24pt, not 18pt.** Default to `Pt(22)` for all body text, bullets, and labels. Drop to `Pt(20)` only when content density requires it. 18pt is a hard floor for exceptional cases only. If text does not fit at 20pt, reduce content (split slide, remove bullets, condense phrasing) before reducing font size.
2. **All readable text uses Charcoal (#4D4D4D).** Never use #B0AFA8 (MedGray) or #6C7A89 (Medium Gray) on body text, labels, headings, date labels, or any element that must be readable when projected. #B0AFA8 is exclusively for citation text boxes (`add_citation()`). #6C7A89 is for connector lines and neutral shape outlines only.
3. **No inline source references.** Present findings as factual statements. Author attribution goes exclusively in `add_citation()` text boxes at the bottom of the slide. Never write "Smith et al. (2024) found that..." in body text.
4. **The quality check is mandatory and blockers must be fixed.** Run `run_quality_check(prs)` before every `prs.save()`. Fix all errors (not just warnings) before saving. Fonts below 20pt are errors, not warnings.
5. **Native objects, not image embeds.** Colored boxes, flowcharts, box-and-arrow diagrams, tables, and standard charts must be recreated as native PowerPoint objects. Image embed is a last resort for irreducible visual complexity (Bezier curves, mathematical plots). If you are about to embed a full-slide image, stop and reclassify.

---

## Typography

| Element | Specification |
|---------|---------------|
| Slide titles | 36pt Calibri Bold, #4D4D4D, in Title placeholder |
| Section headers within slides | 24-28pt Calibri Bold |
| Body text | **20-24pt** Calibri Regular, #4D4D4D |
| Minimum text size | **18pt** hard floor for body text; 14pt for chart axis labels and table content only |
| Subtitles | NEVER use subtitles; title only, content below |

**Font size principle: use the largest size that fits attractively.** Target 22-24pt for bullet lists and short labels; drop to 20pt when content density requires it. 18pt is a hard floor, used only when 20pt genuinely cannot fit after reducing content. Never use 16pt or smaller for slide body text. If you find yourself setting text to 18pt, first try reducing content: split the slide, remove a bullet, or condense phrasing before dropping below 20pt.

## Layout Principles

- **Aspect ratio:** 16:9
- **Generous margins** and white space between elements
- **One main idea per slide**
- **Footer space:** Always leave the bottom 1.3" blank for template footers; do not place content below `FOOTER_TOP = 7.70"` on a 9" slide
- **No title slide:** The template provides the title slide; never generate one

### Layout Selection

**Use the "Title Only" slide layout for every slide.** Do not use "Blank", "Title and Content", or any other layout. The title of every slide must be placed in the Title placeholder of the "Title Only" layout.

### Template File

Store a master template at a known path in your project (e.g., `your-template.pptx` or `~/.your-skills/pptx-style/template.pptx`). Always load this template when initializing a new presentation. It should carry the correct slide master, theme colors, fonts, footer placeholders, and the "Title Only" layout. Do not use `Presentation()` (blank) when the template is available.

### python-pptx Implementation

```python
import os
from pptx import Presentation
from pptx.util import Pt
from pptx.dml.color import RGBColor

TEMPLATE_PATH = "path/to/your-template.pptx"  # set this for your project

# Load template (fall back to blank only if template is missing)
if os.path.exists(TEMPLATE_PATH):
    prs = Presentation(TEMPLATE_PATH)
    # Remove pre-existing slides — must drop the relationship first to avoid
    # duplicate-name warnings in the saved ZIP
    xml_slides = prs.slides._sldIdLst
    for sldId in list(xml_slides):
        rId = sldId.get('{http://schemas.openxmlformats.org/officeDocument/2006/relationships}id')
        prs.part.drop_rel(rId)
        xml_slides.remove(sldId)
else:
    prs = Presentation()
    prs.slide_width = Inches(16)
    prs.slide_height = Inches(9)

# Find "Title Only" layout by name (do this once)
title_only_layout = None
for layout in prs.slide_layouts:
    if layout.name == "Title Only":
        title_only_layout = layout
        break
if title_only_layout is None:
    raise ValueError("Template is missing 'Title Only' layout")

# For every slide:
slide = prs.slides.add_slide(title_only_layout)
title_ph = slide.placeholders[0]  # Title placeholder is always index 0
title_ph.text = "Slide Title Here"
# Apply title formatting
for paragraph in title_ph.text_frame.paragraphs:
    for run in paragraph.runs:
        run.font.size = Pt(36)
        run.font.bold = True
        run.font.color.rgb = RGBColor(0x4D, 0x4D, 0x4D)
        run.font.name = "Calibri"
```

**Critical rules:**
- Always load the template file (never start from `Presentation()` blank if the template exists)
- Always clear pre-existing slides from the template before adding new ones
- Never use hardcoded layout indices; always find "Title Only" by name
- Never create a text box for the title; always use `slide.placeholders[0]`
- All slide content (shapes, charts, text boxes) goes below the title placeholder

### Hidden Slide Detection

PowerPoint's "Hide Slide" feature sets `show="0"` on the slide XML element. Use this to detect hidden slides when reading existing PPTX files:

```python
def is_hidden(slide):
    """Check if a slide is marked as hidden in PowerPoint."""
    return slide._element.get('show') == '0'

def set_hidden(slide, hidden=True):
    """Mark a slide as hidden (or visible)."""
    slide._element.set('show', '0' if hidden else '1')
```

**Convention:** Hidden slides in a deck are typically presenter notes, not visible to the audience. They may contain background details, reading notes, or preparation context.

**Rules for hidden slides:**
- **When reading/analyzing a PPTX:** Detect hidden slides and label them as `[HIDDEN - presenter notes]`. Do not recommend replacing, redesigning, or removing them. Do not critique their content density, font sizes, or visual design. They are notes, not presentation material.
- **When editing a PPTX:** Hidden slides can be edited or added when requested. Use `set_hidden(slide)` to mark new notes slides. Hidden slides do not need to follow the style guide's visual rules (font targets, color palette, layout constants).
- **When converting or rebuilding:** Preserve hidden slides and their hidden status. Do not convert them to visible slides or merge their content into presented slides.
- **In the quality check:** Skip hidden slides entirely (they are not presented, so style compliance is irrelevant).

### Content Area Layout Constants

The template is **16" x 9"**. Use these exact constants for all content positioning; do not guess or derive from Beamer coordinates:

```python
# Slide dimensions
SLIDE_W = 16.0   # inches
SLIDE_H = 9.0    # inches

# Title placeholder (from template — do not change)
TITLE_LEFT = 1.10   # inches
TITLE_TOP  = 0.33   # inches
TITLE_W    = 13.80  # inches
TITLE_H    = 1.49   # inches  (bottom edge at 1.82")

# Content area — use these for ALL shapes, charts, text boxes
CONTENT_LEFT  = 1.10   # left margin (aligns with title)
CONTENT_TOP   = 1.95   # just below title bottom (1.82" + 0.13" gap)
CONTENT_W     = 13.80  # full content width (aligns with title)
FOOTER_TOP    = 7.70   # do not place content below this line (footer zone)

# Derived: usable content height
CONTENT_H = FOOTER_TOP - CONTENT_TOP  # = 5.75 inches
```

Every shape, chart, and text box must fit within `CONTENT_LEFT` to `CONTENT_LEFT + CONTENT_W` horizontally, and `CONTENT_TOP` to `FOOTER_TOP` vertically. Content positioned outside these bounds will be clipped by the footer or pushed off the edge of the slide.

**Do not use arbitrary offsets.** Shapes must start at `CONTENT_LEFT = 1.10"` (or inset from it), not at `0.5"`, `0.8"`, `2.0"` or other guessed values. Column widths must sum to `CONTENT_W = 13.80"` minus any gap, not to arbitrary narrower widths.

## Complete Color Palette

### Accent Colors (for outlines and emphasis)

| Role | Color | Hex | Usage |
|------|-------|-----|-------|
| Primary accent | DeepTeal | #0D7377 | Primary accent for outlines, headers, emphasis |
| Secondary accent | Cyan Blue | #0077B6 | Theory, models, formulas, technical content |
| Tertiary accent | Dusty Plum | #9B5978 | Third accent for charts, diagrams, general emphasis |

### Fill Colors (use white text on all fills)

| Role | Color | Hex | Usage |
|------|-------|-----|-------|
| **Primary fill** | SlateNavy | #1B2A4A | Block titles, emphasis boxes within diagrams, dark-background slides |
| Alert fill | WarmAmber | #E8913A | Alert blocks, highlighted annotations |
| Positive fill | Green | #27AE60 | Positive outcomes, solutions, "after" states |
| Warning fill | Soft Red | #DC5C5C | Warnings, errors, negative outcomes |
| Problem fill | Burnt Orange | #BF5700 | Problems, trade-offs, "before" states |
| Problem fill (severe) | AccentRed | #C0392B | Challenges, critical issues |

### Structural and Indicator Colors

| Role | Color | Hex | Usage |
|------|-------|-----|-------|
| Primary text | Charcoal | #4D4D4D | All body text, titles |
| Default outline | Slate Blue | #425563 | Thin borders, divider lines, default outlines |
| Subtle backgrounds | PaleBlue | #E8F0F8 | Secondary containers, neutral boxes, alternating table rows |
| Light background | LightGray | #F0EFEC | Spare light fill |
| Neutral connector | Medium Gray | #6C7A89 | Neutral states, connectors, transitions |
| Background | White | #FFFFFF | Main slide background |

## Color Application Rules

### Colors Per Slide
- **Target:** 3 accent colors per slide (beyond black, gray, white)
- **Maximum:** 4 colors when necessary for clarity

### Filled Content Boxes
- **Primary fill:** SlateNavy (#1B2A4A) with white text for block headers and emphasis boxes
- **Alert fill:** WarmAmber (#E8913A) with white text for alert blocks, highlighted annotations
- **Positive fill:** Green (#27AE60) with white text for solutions, "after" states
- **Problem fill:** Burnt Orange (#BF5700) with white text for problems, trade-offs, "before" states
- **Problem fill (severe):** AccentRed (#C0392B) with white text for critical issues
- **Warning fill:** Soft Red (#DC5C5C) with white text for errors, warnings

### Outlined Content Boxes
- **Default outline:** Slate Blue (#425563) for standard content boxes
- **Accent outlines:** DeepTeal (#0D7377), Cyan Blue (#0077B6), or Dusty Plum (#9B5978)

## Visual Elements

### DO
- Use solid color-blocked rectangles with rounded or square corners
- Keep icons and graphics flat, vector, high-contrast
- Use accent bars (thin vertical rectangles) for left-edge emphasis
- Use SlateNavy (#1B2A4A) as primary fill for block titles and emphasis boxes within diagrams
- Stick to 3 colors per slide, expand to 4 only when needed

### DON'T
- Use gradients, glows, drop shadows, or bevels on any element (text, shapes, charts, images)
- Use text shading, text highlighting, text background fills, or text shadows
- Add subtitles under titles
- Clutter slides with too many elements
- Use more than 4 accent colors on a single slide
- Forget to leave footer space at the bottom
- Create title slides (template provides these)
- Embed charts as images when they can be recreated as native PowerPoint charts

## Beamer-to-PPTX Conversion Workflow

**Full-slide image embedding of Beamer pages is NOT conversion.** The purpose of this workflow is to recreate slide content as native, editable PowerPoint objects (charts, shapes, text boxes, tables). Image embed is reserved for irreducible visual complexity (mathematical curves, Bezier paths) and requires written justification per slide. If your implementation renders PDF pages as PNGs and embeds them, you have not followed this workflow.

When converting Beamer output to PPTX, follow this workflow in order. Do not write any python-pptx code until Steps 1-4 are complete.

### Step 1: Read the .tex source and compiled PDF

- Read `slides.tex` from the build directory
- Read the compiled PDF (use split reading with the `pages` parameter if >10 pages)
- Identify the content name from the calling workflow or from the working directory name

### Step 2: Per-slide conversion plan

For each Beamer slide, categorize every visual element into one of four types:

| Type | When to use | PowerPoint implementation |
|------|------------|--------------------------|
| **Native chart** | Standard bar, line, scatter, pie charts where data is extractable from the .tex source | `add_chart()` + `fix_chart_fonts()` + palette colors |
| **Native table** | Data tables | `add_table()` + `fix_table_fonts()` |
| **Native shapes/text** | Bullet points, text boxes, simple box layouts, colored boxes with text labels, box-and-arrow diagrams, flowcharts, stacked/layered layouts | `add_shape()` + `add_textbox()` with Calibri formatting |
| **Hybrid (text + image)** | Two-column Beamer slides where one column is text/bullets and the other is a complex visual | Native text box(es) for the text column + `add_image_proportional()` for the visual column |
| **Image embed** | LAST RESORT. The visual contains mathematical curve plots with axis annotations, or TikZ paths with Bezier curves/decorative elements that have no PowerPoint shape equivalent, AND it cannot be decomposed into rectangles, arrows, and text labels | Render at 300 DPI, crop, `add_image_proportional()` |

**Hybrid default rule:** Hybrid is the default for any two-column Beamer slide. The text column is ALWAYS recreated as native text boxes at 22pt+ font (20pt minimum). Only the visual column is assessed for native vs. image. A full-slide image embed is only permitted when the slide has no separable text content.

**Image embed decision rules:**

- **ALWAYS native shapes** (never image embed): colored rectangles/boxes with text labels, box-and-arrow diagrams, flowcharts, stacked/layered layouts with labeled sections, simple node-and-edge diagrams, comparison layouts, tables, process flows with labeled steps
- **MAY be image embed** (requires written justification): mathematical function plots with axis annotations, complex pgfplots with many overlapping series and fill regions, TikZ diagrams with decorative elements (braces, Bezier curves, custom path decorations), choropleth maps, multi-panel composite figures

**For each slide marked "image embed," write one sentence justifying why it cannot be recreated natively.** If no justification exists, reclassify as native or hybrid.

### Step 3: Specify output filename

The PPTX must be named `<content_name>.pptx` using the content name from the calling workflow. Never use generic names like `slides.pptx`. If no content name was provided by a calling workflow, derive one from the working directory name or ask the user.

### Step 4: Present the plan

Present the conversion plan to the user in table format before writing any code:

```
Slide | Type           | Elements                                      | Notes
1     | image          | Complex multi-layer TikZ flow diagram          | 12 positioned nodes with crossing arrows
2     | native chart   | Clustered bar chart (3 series, 5 categories)   | Data: [values from .tex]
3     | native shapes  | 3-box comparison layout with text              | DeepTeal/CyanBlue/DustyPlum outlines
...
```

Wait for user approval before proceeding to code generation. Then follow the rest of this style guide for implementation.

**Exception:** When a calling workflow specifies "without pause" or "proceed directly," skip the pause and execute the plan immediately. Still produce the plan internally and log it in the output, but do not wait for explicit approval.

### Font Size Rule for Conversion

All native text boxes created during Beamer-to-PPTX conversion must target **22-24pt** body text. Drop to 20pt when content density requires it. 18pt is a hard floor, used only when 20pt genuinely cannot fit after reducing content. Never use 16pt or smaller for slide body text.

If the Beamer source has dense text that would require fonts below 20pt to fit in a PPTX text box, **reduce content, not font size.** Split the text across two slides, remove less critical bullets, or condense phrasing before dropping below 20pt.

This applies to all native text boxes: bullet lists, labels, standalone text, hybrid slide text columns, and annotation text. The only exceptions are chart axis labels (14pt per chart font rules), table content (14pt minimum per table rules), and italic caption text (11pt per the caption pattern).

### Source Citation Handling

Every `\sourcecite{}` in the Beamer source must be carried over to the PPTX as a citation text box. Citations are not optional content; they are part of the slide.

**Placement:** Right-justified, positioned just above `FOOTER_TOP` (at approximately `FOOTER_TOP - 0.30"`). The citation text box spans the full `CONTENT_W` width with right-aligned text.

**Formatting:** 11pt Calibri Italic, color #B0AFA8 (MedGray), right-aligned.

```python
from pptx.enum.text import PP_ALIGN

CITATION_TOP = FOOTER_TOP - 0.30  # just above footer zone
CITATION_H   = 0.25

def add_citation(slide, citation_text):
    """Add a right-justified citation text box just above the footer margin."""
    txbox = slide.shapes.add_textbox(
        Inches(CONTENT_LEFT), Inches(CITATION_TOP),
        Inches(CONTENT_W), Inches(CITATION_H)
    )
    tf = txbox.text_frame
    tf.word_wrap = True
    p = tf.paragraphs[0]
    p.alignment = PP_ALIGN.RIGHT
    run = p.add_run()
    run.text = citation_text
    run.font.size = Pt(11)
    run.font.italic = True
    run.font.color.rgb = RGBColor(0xB0, 0xAF, 0xA8)
    run.font.name = "Calibri"
    return txbox
```

**Extraction:** Parse each slide's `\sourcecite{...}` content from the `.tex` source. Strip LaTeX formatting (`\textit{}` becomes plain text; backslash escapes become their characters). If a slide has `\sourcecite{}`, the PPTX slide must have a citation text box. If a slide has no `\sourcecite{}`, do not add one.

### Vertical Text Alignment

All text frames in content shapes (text boxes, rounded rectangles, auto shapes) must use **top vertical alignment** by default. python-pptx defaults rounded rectangles to middle alignment, which pushes text down from the top edge and creates inconsistent visual spacing. Set `text_frame.vertical_anchor = MSO_ANCHOR.TOP` explicitly on every shape that contains text.

```python
from pptx.enum.text import MSO_ANCHOR

# After creating a shape or text box:
tf = shape.text_frame
tf.vertical_anchor = MSO_ANCHOR.TOP  # always set explicitly
```

Middle alignment (`MSO_ANCHOR.MIDDLE`) is acceptable only for single-line labels inside small boxes (e.g., cycle diagram nodes, connector labels) where the text should be vertically centered. For any box with a title and body text, multi-line content, or bullet lists, use top alignment.

### Text Box Consolidation

Related text content on a slide must go in **one continuous text box** with paragraph-level formatting, not split into multiple separate text boxes.

**Rule:** When a Beamer slide has a text column containing a heading followed by bullet points (or multiple formatted paragraphs), recreate this as a single text box with multiple paragraphs. Use paragraph-level properties for differentiation:

- **Section headers within a text box:** Bold run, 20-24pt
- **Bullet points:** Normal weight, 22pt (drop to 20pt if density requires), with `paragraph.level` set to create indent
- **Sub-bullets:** 20pt, `paragraph.level = 1` for additional indent
- **Spacing between sections:** Use `paragraph.space_before = Pt(12)` to separate logical sections within one text box

**Do not** create separate text boxes for a heading and its bullets, or for each bullet point individually. A single text column should be ONE text box with multiple paragraphs.

```python
from pptx.util import Inches, Pt, Emu
from pptx.enum.text import PP_ALIGN
from pptx.dml.color import RGBColor

# Single text box with header + bullets:
tf = txbox.text_frame
tf.word_wrap = True

# Section header paragraph
p = tf.paragraphs[0]
run = p.add_run()
run.text = "Section Header"
run.font.bold = True
run.font.size = Pt(22)
run.font.color.rgb = RGBColor(0x4D, 0x4D, 0x4D)
run.font.name = "Calibri"

# Bullet point (new paragraph in SAME text box)
p2 = tf.add_paragraph()
p2.level = 0
p2.space_before = Pt(6)
run2 = p2.add_run()
run2.text = "First bullet point with detail"
run2.font.size = Pt(22)
run2.font.color.rgb = RGBColor(0x4D, 0x4D, 0x4D)
run2.font.name = "Calibri"
```

### Bullet Preservation

When the Beamer source uses `\begin{itemize}` or `\begin{enumerate}`, the PPTX must reproduce those as native PowerPoint bullets or numbered lists, not as plain text with dashes or asterisks.

**Implementation:** Set `paragraph.level` to control indent depth. PowerPoint auto-applies bullet characters based on the level. For explicit bullet control:

```python
from pptx.oxml.ns import qn
from lxml import etree

def set_bullet(paragraph, level=0, bullet_char='\u2022'):
    """Set a bullet character on a paragraph."""
    paragraph.level = level
    pPr = paragraph._p.get_or_add_pPr()
    # Add bullet character
    buChar = etree.SubElement(pPr, qn('a:buChar'))
    buChar.set('char', bullet_char)

# Usage:
p = tf.add_paragraph()
set_bullet(p, level=0)  # top-level bullet
run = p.add_run()
run.text = "Bullet point text"
run.font.size = Pt(22)
```

For enumerated lists, use `buAutoNum` instead of `buChar`:
```python
buAutoNum = etree.SubElement(pPr, qn('a:buAutoNum'))
buAutoNum.set('type', 'arabicPeriod')  # "1.", "2.", etc.
```

### Bullet Indentation (Hanging Indents)

All bullet lists must use hanging indents. Continuation lines align under the text start, not under the bullet marker. python-pptx does not create hanging indents automatically; the paragraph properties `marL` (left margin) and `indent` (negative for hanging) must be set explicitly via XML.

```python
from pptx.util import Inches

def set_hanging_indent(paragraph, margin_inches=0.35, indent_inches=-0.25):
    """Set hanging indent so wrapped text aligns under text start, not bullet."""
    pPr = paragraph._p.get_or_add_pPr()
    pPr.set('marL', str(int(Inches(margin_inches))))
    pPr.set('indent', str(int(Inches(indent_inches))))
```

Apply `set_hanging_indent()` to every bullet paragraph. The pre-save quality check should flag bullet paragraphs without an explicit `indent` attribute set.

### Source Attribution

Never reference authors by name in slide body text (e.g., "Brynjolfsson et al. (2023) find that..."). Present findings as factual statements in the body and attribute the source exclusively via `add_citation()` at the bottom of the slide.

### Chart Number Formatting

When converting Beamer charts to native PowerPoint charts, axis labels and data labels must use appropriate number formatting. Do not leave axes with raw unformatted numbers.

**Common format strings for `number_format` on chart axes and data labels:**

| Data type | Format string | Example |
|-----------|--------------|---------|
| Currency (millions) | `'$#,##0"M"'` | $150M |
| Currency (billions) | `'$#,##0.0"B"'` | $2.5B |
| Currency (exact) | `'$#,##0'` | $1,500 |
| Percentage | `'0%'` or `'0.0%'` | 45% or 45.0% |
| Percentage (from decimal) | `'0%'` | 0.45 displays as 45% |
| Comma-separated | `'#,##0'` | 1,500 |
| Year (no commas) | `'0'` | 2026 |
| Decimal | `'0.0'` or `'0.00'` | 3.5 or 3.50 |

**Apply to axes:**
```python
chart.value_axis.tick_labels.number_format = '$#,##0"M"'
chart.value_axis.tick_labels.number_format_is_linked = False
```

**Apply to data labels:**
```python
plot = chart.plots[0]
plot.has_data_labels = True
plot.data_labels.number_format = '0%'
plot.data_labels.number_format_is_linked = False
```

**Rule:** Cross-reference the Beamer `.tex` source for the data units. If the pgfplots axis shows `ylabel={Revenue (\$M)}`, the PPTX value axis must use `'$#,##0"M"'`. If percentages are plotted, use `'0%'`. If years are on the category axis, use `'0'` (no comma separators). Never leave chart axes with the default unformatted number display.

---

## Chart and Diagram Conversion

When converting Beamer/LaTeX charts and diagrams to PowerPoint:

### Match the Beamer source

When converting Beamer charts and diagrams to PowerPoint, the PPTX chart should match the PDF as closely as possible:
- Same axis ranges and tick marks
- Same data label format and placement
- Same legend position (see legend rules below)
- Same series colors (using this guide's palette)
- Same chart type (bar, line, scatter, etc.)

Cross-reference the `.tex` source and the compiled PDF when making layout decisions.

### Use native PowerPoint charts (default)
Recreate charts using python-pptx's chart API (`add_chart()`). This includes bar charts, line charts, pie charts, scatter plots, and other standard chart types. Native charts are editable, scalable, and professional.

**Formatting requirements:**
- Number formatting (decimal places, percentages, currency) must match the Beamer source exactly
- Axis label formatting (font size, orientation, number format) must match the Beamer source
- Data labels must use the same format as the Beamer chart
- Bar/series colors must use the style guide palette
- No shadows, gradients, or 3D effects on any chart element

### Chart font sizes: mandatory XML fix

python-pptx generates charts with hardcoded small font sizes (10-12pt) embedded in `<c:txPr>/<a:defRPr sz="...">` elements. These are never overridden by general style settings. **You must explicitly fix them for every chart** after creating it:

```python
from pptx.oxml.ns import qn
from lxml import etree

def fix_chart_fonts(chart, axis_pt=14, legend_pt=14):
    """Set font size on all chart text elements (axes, legend, data labels)."""
    chart_el = chart._element
    for txpr in chart_el.iter(qn('c:txPr')):
        parent_tag = txpr.getparent().tag.split('}')[1]
        if parent_tag == 'chartSpace':
            continue   # leave the chart-level default alone
        target_sz = str((legend_pt if parent_tag == 'legend' else axis_pt) * 100)
        defrpr = txpr.find('.//' + qn('a:defRPr'))
        if defrpr is not None:
            defrpr.set('sz', target_sz)
        else:
            for p in txpr.findall('.//' + qn('a:p')):
                ppr = p.find(qn('a:pPr'))
                if ppr is None:
                    ppr = etree.SubElement(p, qn('a:pPr'))
                    p.insert(0, ppr)
                dr = etree.SubElement(ppr, qn('a:defRPr'))
                dr.set('sz', target_sz)

# Call immediately after add_chart():
fix_chart_fonts(chart_shape.chart, axis_pt=14, legend_pt=14)
```

Target sizes:
- Axis tick labels: **14pt** (cannot be 18pt, but must be readable, not 10-11pt)
- Legend text: **14pt**
- Data labels: **14pt**
- Do NOT modify `chartSpace` txPr (that controls the chart title default)

### Chart legend rules

**Line charts:** Legend always on the **RIGHT** (`XL_LEGEND_POSITION.RIGHT`), outside the plot area.

**Bar/column charts:** Legend on **TOP** or **RIGHT**; match the Beamer source. If the bar chart has a callout or annotation box below the chart, ensure the legend does not overlap it.

**All charts:** `include_in_layout = False` (legend sits outside plot area, does not shrink it).

```python
from pptx.enum.chart import XL_LEGEND_POSITION

chart.legend.position = XL_LEGEND_POSITION.RIGHT   # line charts always
chart.legend.include_in_layout = False
```

### Bar charts with negative values

When a bar/column chart contains series with negative values, explicitly disable `invertIfNegative` to preserve the fill color for negative bars. If this is not set, PowerPoint defaults to inverting the fill (bars appear white or unfilled):

```python
from lxml import etree
from pptx.oxml.ns import qn

for series in chart.series:
    ser_el = series._element
    # Remove any existing invertIfNeg, then add with val=0
    for old in ser_el.findall(qn('c:invertIfNegative')):
        ser_el.remove(old)
    inv = etree.SubElement(ser_el, qn('c:invertIfNegative'))
    inv.set('val', '0')
    # Position after <c:tx> element
    tx_el = ser_el.find(qn('c:tx'))
    if tx_el is not None:
        tx_el.addnext(inv)
```

### Chart captions
Every chart or diagram that has a caption or figure label in the Beamer source **must** include that caption as a text box directly below the chart in the PowerPoint slide. Do not omit captions.

**Implementation:** After adding the chart shape, add a text box immediately below it spanning the same horizontal width:
```python
from pptx.util import Inches, Pt
from pptx.dml.color import RGBColor
from pptx.enum.text import PP_ALIGN

# Caption text box — same left/width as chart, positioned just below
caption_top = chart_shape.top + chart_shape.height + Inches(0.05)
caption_tf = slide.shapes.add_textbox(
    chart_shape.left, caption_top, chart_shape.width, Inches(0.3)
).text_frame
caption_tf.word_wrap = True
p = caption_tf.paragraphs[0]
p.alignment = PP_ALIGN.CENTER
run = p.add_run()
run.text = "Figure N. Caption text here."
run.font.size = Pt(11)
run.font.italic = True
run.font.color.rgb = RGBColor(0x4D, 0x4D, 0x4D)
```

**Verification step:** After generating the PPTX, scan every slide that contains a chart or figure. Cross-reference against the `.tex` source to confirm every `\caption{}` or figure label present in Beamer is represented as a caption text box in the corresponding PowerPoint slide. Flag any slide where a caption is missing and add it before saving the final file.

### Use images only as a last resort
Only embed a chart or diagram as an image when it is too complex to accurately reproduce in PowerPoint (e.g., multi-layered TikZ diagrams with custom paths, complex mathematical annotations, or highly customized pgfplots with dozens of overlays). When embedding as an image, export at high resolution (300+ DPI).

**Image positioning (mandatory):** All embedded images must fit proportionally within the content area. **"Fill the content area" means fit proportionally within, centered horizontally, top-aligned; never stretch an image to fill the full width and height regardless of its native aspect ratio.** This applies to all embedded image types: paper figures, charts exported as images, photographs, and interface screenshots.

PIL/Pillow is an assumed dependency for all image handling. Install if needed: `pip3 install Pillow`.

Use `add_image_proportional()` for all embedded image placement:

```python
from PIL import Image

def add_image_proportional(slide, img_path, area_left, area_top, area_w, area_h):
    """Fit image proportionally within bounding box: centered horizontally, top-aligned."""
    with Image.open(img_path) as im:
        native_w, native_h = im.size
    aspect = native_w / native_h
    if area_w / area_h > aspect:
        fit_h = area_h
        fit_w = area_h * aspect
    else:
        fit_w = area_w
        fit_h = area_w / aspect
    left = area_left + (area_w - fit_w) / 2.0
    top  = area_top
    return slide.shapes.add_picture(
        img_path, Inches(left), Inches(top), Inches(fit_w), Inches(fit_h)
    )

# Full-width figure slide (no caption):
add_image_proportional(slide, img_path, CONTENT_LEFT, CONTENT_TOP, CONTENT_W, CONTENT_H)

# Figure with caption below (leave room for caption text box):
CAPTION_H = 0.35
add_image_proportional(slide, img_path, CONTENT_LEFT, CONTENT_TOP, CONTENT_W, CONTENT_H - CAPTION_H - 0.08)

# Two images side by side:
col_w = (CONTENT_W - 0.50) / 2   # 0.50" gap between images
add_image_proportional(slide, img1_path, CONTENT_LEFT,                 CONTENT_TOP, col_w, CONTENT_H)
add_image_proportional(slide, img2_path, CONTENT_LEFT + col_w + 0.50, CONTENT_TOP, col_w, CONTENT_H)

# Hybrid slide — text column (left) + image column (right):
COL_GAP   = 0.50                               # gap between text and image columns
TEXT_W    = CONTENT_W * 0.52                     # text takes ~52% of content width
IMG_COL_W = CONTENT_W - TEXT_W - COL_GAP         # image gets the remainder
IMG_COL_LEFT = CONTENT_LEFT + TEXT_W + COL_GAP   # image column left edge
# Text column: add_textbox() at CONTENT_LEFT, width=Inches(TEXT_W), 22pt+ font
# Image column: fit image into the image column only (not the full content area)
add_image_proportional(slide, img_path, IMG_COL_LEFT, CONTENT_TOP, IMG_COL_W, CONTENT_H)
```

**Never** position images at hardcoded offsets like `left=2.0"` or size them with explicit `width` and `height` that ignore the native aspect ratio. Every embedded image (paper figures, photographs, chart screenshots) must go through `add_image_proportional()`.

## Tables

### Cell alignment
- **Header row:** center-align text, bold, set explicit font size (16pt minimum; prefer 16-18pt for table content)
- **Data rows:** center-align numbers; left-align labels/text in the first column if the table has a label column
- **Never rely on default alignment;** always call `para.alignment = PP_ALIGN.CENTER` or `PP_ALIGN.LEFT` explicitly

### Font in table cells: mandatory XML fix

Table cells do NOT inherit slide defaults, and the python-pptx API (`run.font.size`) alone is insufficient. It only sets the run-level `<a:rPr>` but misses empty cells that have no runs, and can be overridden by paragraph defaults. **Always use this XML approach after populating any table:**

```python
from pptx.oxml.ns import qn
from lxml import etree

def fix_table_fonts(table_shape, size_pt=18, align='ctr'):
    """Set font size AND alignment on all table cells via XML."""
    sz_val = str(size_pt * 100)
    tbl_el = None
    for el in table_shape._element.iter():
        if el.tag.split('}')[-1] == 'tbl':
            tbl_el = el; break
    if tbl_el is None: return
    for tc in tbl_el.iter(qn('a:tc')):
        for p in tc.iter(qn('a:p')):
            ppr = p.find(qn('a:pPr'))
            if ppr is None:
                ppr = etree.SubElement(p, qn('a:pPr'))
                p.insert(0, ppr)
            ppr.set('algn', align)                     # center alignment
            dr = ppr.find(qn('a:defRPr'))
            if dr is None:
                dr = etree.SubElement(ppr, qn('a:defRPr'))
            dr.set('sz', sz_val)                       # paragraph default font
            for rpr in p.iter(qn('a:rPr')):
                rpr.set('sz', sz_val)                  # explicit run font

# Call after adding all rows:
fix_table_fonts(table_shape, size_pt=18, align='ctr')
```

Target: **18pt** for all table text. Use 14pt only when a table has dense content that genuinely cannot fit at 18pt.

### Table positioning
Tables must start at `CONTENT_LEFT = 1.10"` and span `CONTENT_W = 13.80"` (full content width) unless there is a side-by-side chart or other content. In that case, scale the table and chart proportionally to together fill the full content width. Never let a table float to the right or center at a narrower width than the surrounding shapes.

## Multi-Box Layouts

When a slide has 2 to 4 equal-sized boxes side by side:
- **All boxes must be equal width**
- **The group must fill the full content width** (`CONTENT_W = 13.80"`)
- **Gap between boxes:** 0.5"
- **Formula:** `box_w = (CONTENT_W - (n - 1) * 0.5) / n` where n = number of boxes

```python
n = 3  # or 2, or 4
GAP = 0.5
box_w = (CONTENT_W - (n - 1) * GAP) / n   # e.g. n=3: 4.267"

for k in range(n):
    left = CONTENT_LEFT + k * (box_w + GAP)
    # add_shape(left=Inches(left), width=Inches(box_w), ...)
```

Never create boxes of unequal widths unless the content explicitly requires different sizes (e.g., a 60/40 comparison layout). Never leave a gap on the right side of the slide (the last box should end at `CONTENT_LEFT + CONTENT_W = 14.90"`).

## Content Fitting

python-pptx provides no API to measure rendered text height. Text that overflows a shape is invisible in code but renders as clipped or overlapping content in PowerPoint. **Always estimate text height before assigning box dimensions.**

### Text-Height Estimation

```python
import math

def estimate_text_height(text, box_width_inches, font_size_pt, line_spacing=1.4):
    """Estimate rendered text height in inches.
    
    Use BEFORE setting shape height to verify content fits.
    Use in run_quality_check() to detect overflow after the fact.
    """
    chars_per_line = max(1, box_width_inches * 72 / (font_size_pt * 0.55))
    lines_needed = math.ceil(len(text) / chars_per_line)
    height_inches = lines_needed * font_size_pt * line_spacing / 72
    return height_inches
```

**Usage during generation:** Before creating a text box or content box, estimate the height needed for its text. If the estimated height exceeds the allocated space, reduce content or change the layout before writing any shapes.

```python
# Example: verify a stat box can hold its description
desc = "Enterprise AI adoption grew 15 percentage points year-over-year..."
box_w = 4.27  # inches (3-column grid box width)
font_pt = 20
needed_h = estimate_text_height(desc, box_w, font_pt)
available_h = 1.75  # planned box height

if needed_h > available_h:
    # Content does not fit — reduce items, shorten text, or change layout
    ...
```

### Grid Layout Limits

Grid layouts (2x2, 2x3, 3x2) with content boxes are constrained by `CONTENT_H = 5.75"`. Apply these rules:

| Grid | Max rows | Row height (approx) | Content per box |
|------|----------|---------------------|-----------------|
| 2 boxes (1 row) | 1 | 5.50" | Full paragraphs OK |
| 3 boxes (1 row) | 1 | 5.50" | Full paragraphs OK |
| 4 boxes (2x2) | 2 | 2.50" | 2-3 short lines at 20pt |
| 6 boxes (2x3 or 3x2) | 2 | 2.50" | 1-2 short lines at 20pt |

**Rules:**
1. **Never use paragraph-length descriptions in 2-row grids.** At 20pt in a 4.27"-wide box, one line holds ~14 characters. A 100-character description needs ~7 lines (~2.7"). A 2.50" box cannot hold it.
2. **If descriptions exceed 2 lines per box, switch layout:** use a bulleted list, a table, or split across slides.
3. **Stat callout boxes** (large number + short label) work in grids. Stat boxes with explanatory paragraphs do not.
4. **Always run `estimate_text_height()` on the longest box's content** before committing to a grid layout. If any box overflows, the layout is wrong.

## Slide Structure Patterns

### Standard Content Slide
1. Title in placeholder (36pt Calibri Bold, #4D4D4D); the title IS the key message
2. Bullet points or content area, starting directly below the title placeholder
3. Optional visualization or supporting graphic
4. Blank space at bottom for footer

### Comparison Slide
- Two or three **equal-width** boxes side by side, filling CONTENT_W
- Use contrasting colors to differentiate options
- Limit to 3 colors total (e.g., outline + two fills)

### Progression Slide
- Three **equal-width** boxes showing stages, filling CONTENT_W
- Color progression: Medium Gray outline to Burnt Orange fill to Green fill
- Shows evolution from neutral to active to positive

### Summary Slide
- May use up to 4 colors for different categories
- Four-box layout for strategic frameworks

## Pre-Save Structural Quality Check

**Run this check on every PPTX before calling `prs.save()`.** It catches the most common generation errors that are invisible to visual inspection of the code: overlapping shapes, out-of-bounds positioning, hardcoded small fonts in chart XML, bad table style GUIDs, and missing legend/color rules.

```python
def run_quality_check(prs):
    """
    Structural quality check. Returns a list of issue strings.
    Empty list = all clear. Run before prs.save().

    Catches:
      1. Shapes outside content area bounds
      2. Overlapping shapes on the same slide
      3. Chart axis/legend font < 14pt (hardcoded in XML by python-pptx)
      4. Line chart legend not positioned RIGHT
      5. Bar chart series missing invertIfNegative=0 (causes unfilled negative bars)
      6. Table using built-in style GUID that overrides cell alignment
      7. Table cell font < 14pt
      8. Conversion coverage — flags when >40% of slides are single-image-only
         (with reclassification guidance: hybrid, native shapes, or native chart)
      9. Vertical alignment is MIDDLE on multi-line content shapes (should be TOP)
     10. Text box body font < 20pt (excludes chart axes, tables, and italic captions)
     11. Chart axis number format left as default (warns to apply explicit number_format)
     12. Bullet paragraphs missing hanging indent (negative indent attribute)
     13. Text box body font below target (20-21pt) — warning, not blocker
     14. Text overflow — estimated text height exceeds shape height by >10%
    """
    from pptx.oxml.ns import qn
    from pptx.enum.chart import XL_LEGEND_POSITION

    IN = 914400
    CONTENT_LEFT = 1.10;  CONTENT_TOP = 1.95
    FOOTER_TOP   = 7.70;  CONTENT_W   = 13.80
    MAX_RIGHT = CONTENT_LEFT + CONTENT_W   # 14.90

    # Built-in table style that silently overrides cell-level paragraph alignment
    BAD_STYLE = '{5C22544A-7EE6-4342-B048-85BDC9FD1C3A}'

    LINE_TYPES = {
        'LINE', 'LINE_MARKERS', 'LINE_STACKED', 'LINE_MARKERS_STACKED',
        'LINE_100_PERCENT', 'LINE_MARKERS_100_PERCENT',
    }
    BAR_TYPES = {
        'BAR_CLUSTERED', 'BAR_STACKED', 'BAR_STACKED_100',
        'COLUMN_CLUSTERED', 'COLUMN_STACKED', 'COLUMN_STACKED_100',
    }

    issues = []

    for si, slide in enumerate(prs.slides, start=1):
        # Skip hidden slides (presenter notes, not presented)
        if slide._element.get('show') == '0':
            continue
        lbl = f"Slide {si}"

        # Collect non-placeholder, non-background content shapes
        content = []
        for s in slide.shapes:
            if s.is_placeholder or s.left is None:
                continue
            l, t = s.left/IN, s.top/IN
            w, h = s.width/IN, s.height/IN
            if l <= 0.1 and t <= 0.1 and w >= 14 and h >= 8:
                continue  # intentional full-slide background — skip
            content.append((s, l, t, w, h))

        # 1. Position bounds
        for s, l, t, w, h in content:
            n = s.name
            if l < CONTENT_LEFT - 0.05:
                issues.append(f"{lbl} '{n}': left={l:.2f}\" (need >=|{CONTENT_LEFT}\")")
            if t < CONTENT_TOP - 0.05:
                issues.append(f"{lbl} '{n}': top={t:.2f}\" (need >={CONTENT_TOP}\")")
            if t + h > FOOTER_TOP + 0.05:
                issues.append(f"{lbl} '{n}': bottom={t+h:.2f}\" (need <={FOOTER_TOP}\" — footer zone)")
            if l + w > MAX_RIGHT + 0.10:
                issues.append(f"{lbl} '{n}': right={l+w:.2f}\" (need <={MAX_RIGHT}\")")

        # 2. Bounding-box overlap between shapes on the same slide
        for i, (s1, l1, t1, w1, h1) in enumerate(content):
            for s2, l2, t2, w2, h2 in content[i+1:]:
                h_overlap = l1 < l2 + w2 - 0.02 and l2 < l1 + w1 - 0.02
                v_overlap = t1 < t2 + h2 - 0.02 and t2 < t1 + h1 - 0.02
                if h_overlap and v_overlap:
                    issues.append(f"{lbl}: shapes overlap — '{s1.name}' and '{s2.name}'")

        # 3-5. Chart checks
        for s in slide.shapes:
            if not s.has_chart:
                continue
            chart  = s.chart
            ct     = chart.chart_type.name if chart.chart_type else ''
            sn     = s.name

            # 3. Axis / legend font size must be >= 14pt
            for txpr in chart._element.iter(qn('c:txPr')):
                parent = txpr.getparent().tag.split('}')[1]
                if parent == 'chartSpace':
                    continue
                dr = txpr.find('.//' + qn('a:defRPr'))
                if dr is not None:
                    sz = dr.get('sz', '')
                    if sz and int(sz) < 1400:
                        issues.append(
                            f"{lbl} '{sn}': chart {parent} font {int(sz)//100}pt "
                            f"(need >=14pt) — run fix_chart_fonts()"
                        )

            # 4. Line chart legend must be RIGHT
            if ct in LINE_TYPES:
                if chart.legend is None:
                    issues.append(f"{lbl} '{sn}': line chart has no legend")
                elif chart.legend.position != XL_LEGEND_POSITION.RIGHT:
                    issues.append(
                        f"{lbl} '{sn}': line chart legend is not RIGHT "
                        f"(currently {chart.legend.position}) — set to XL_LEGEND_POSITION.RIGHT"
                    )

            # 5. Bar chart series must have invertIfNegative=0
            if ct in BAR_TYPES:
                for ser in chart.series:
                    inv = ser._element.find(qn('c:invertIfNegative'))
                    if inv is None or inv.get('val', '1') != '0':
                        issues.append(
                            f"{lbl} '{sn}': bar series '{ser.name}' missing "
                            f"invertIfNegative=0 — negative bars will appear white/unfilled"
                        )

        # 6-7. Table checks
        for s in slide.shapes:
            if not s.has_table:
                continue
            sn = s.name
            tbl_el = next(
                (el for el in s._element.iter() if el.tag.split('}')[-1] == 'tbl'), None
            )
            if tbl_el is None:
                continue

            # 6. Bad table style GUID overrides cell-level paragraph alignment
            tbl_pr = tbl_el.find(qn('a:tblPr'))
            if tbl_pr is not None:
                sid = tbl_pr.find(qn('a:tableStyleId'))
                if sid is not None and sid.text and sid.text.strip().upper() == BAD_STYLE.upper():
                    issues.append(
                        f"{lbl} '{sn}': table uses built-in style {BAD_STYLE} "
                        f"which overrides cell alignment — replace with None style GUID "
                        f"{{00000000-0000-0000-0000-000000000000}}"
                    )

            # 7. Table cell font size must be >= 14pt
            reported = False
            for tc in tbl_el.iter(qn('a:tc')):
                if reported: break
                for p in tc.iter(qn('a:p')):
                    ppr = p.find(qn('a:pPr'))
                    if ppr is not None:
                        dr = ppr.find(qn('a:defRPr'))
                        if dr is not None:
                            sz = dr.get('sz', '')
                            if sz and int(sz) < 1400:
                                issues.append(
                                    f"{lbl} '{sn}': table cell defRPr {int(sz)//100}pt "
                                    f"(need >=18pt) — run fix_table_fonts()"
                                )
                                reported = True; break
                    if reported: break
                    for rpr in p.iter(qn('a:rPr')):
                        sz = rpr.get('sz', '')
                        if sz and int(sz) < 1400:
                            issues.append(
                                f"{lbl} '{sn}': table cell rPr {int(sz)//100}pt "
                                f"(need >=18pt) — run fix_table_fonts()"
                            )
                            reported = True; break
                    if reported: break

    # 8. Conversion coverage — flag blanket image embedding
    image_only_slides = 0
    for si2, slide2 in enumerate(prs.slides, start=1):
        shapes = [s for s in slide2.shapes if not s.is_placeholder]
        if len(shapes) == 1 and shapes[0].shape_type == 13:  # MSO_SHAPE_TYPE.PICTURE
            image_only_slides += 1
    total = len(prs.slides)
    if total > 0 and image_only_slides / total > 0.4:
        issues.append(
            f"CONVERSION COVERAGE: {image_only_slides} of {total} slides "
            f"({image_only_slides*100//total}%) contain only a single embedded image "
            f"with no native charts, tables, or text boxes. Reclassify each image-only "
            f"slide as: (a) Hybrid — if the Beamer slide has a text column and a visual "
            f"column, recreate text natively at 22pt+ and image-embed only the visual; "
            f"(b) Native shapes — if the visual is colored boxes, flowcharts, or "
            f"box-and-arrow diagrams, recreate entirely with add_shape(); "
            f"(c) Native chart — if the visual is a standard bar/line/scatter chart, "
            f"recreate with add_chart(). A full-slide image embed is only permitted "
            f"when the slide has no separable text content AND the visual cannot be "
            f"decomposed into rectangles, arrows, and text labels."
        )

    # 9. Vertical alignment must be TOP on multi-line content shapes
    for si_va, slide_va in enumerate(prs.slides, start=1):
        if slide_va._element.get('show') == '0':
            continue
        lbl_va = f"Slide {si_va}"
        for s in slide_va.shapes:
            if s.is_placeholder or not s.has_text_frame:
                continue
            if s.shape_type == 13:  # picture
                continue
            sn = s.name
            bodyPr = s.text_frame._txBody.find(qn('a:bodyPr'))
            if bodyPr is not None:
                anc = bodyPr.get('anchor', 't')  # default is top
                # Count text paragraphs with content
                para_count = sum(1 for p in s.text_frame.paragraphs if p.text.strip())
                if anc == 'ctr' and para_count > 1:
                    issues.append(
                        f"{lbl_va} '{sn}': vertical alignment is MIDDLE on multi-line "
                        f"content shape — set text_frame.vertical_anchor = MSO_ANCHOR.TOP"
                    )

    # 10. Text box body font size must be >= 20pt
    for si3, slide3 in enumerate(prs.slides, start=1):
        lbl3 = f"Slide {si3}"
        for s in slide3.shapes:
            # Skip placeholders, charts, tables, and images
            if s.is_placeholder or s.has_chart or s.has_table:
                continue
            if s.shape_type == 13:  # MSO_SHAPE_TYPE.PICTURE
                continue
            if not s.has_text_frame:
                continue
            sn = s.name
            for p in s.text_frame.paragraphs:
                for run in p.runs:
                    if run.font.size is not None and run.font.size < Pt(20):
                        # Exception: italic text at 12pt or less (caption text)
                        if run.font.italic and run.font.size <= Pt(12):
                            continue
                        issues.append(
                            f"{lbl3} '{sn}': text box font {run.font.size.pt:.0f}pt "
                            f"(need >=20pt; target 22-24pt) — increase font size or reduce content"
                        )
                        break  # one issue per shape is enough
                else:
                    continue
                break  # break out of paragraph loop too

    # 11. Chart axis number format — warn if left as default "General"
    for si4, slide4 in enumerate(prs.slides, start=1):
        lbl4 = f"Slide {si4}"
        for s in slide4.shapes:
            if not s.has_chart:
                continue
            chart = s.chart
            sn = s.name
            # Check value axis number format
            try:
                va = chart.value_axis
                if va and va.tick_labels:
                    nf = va.tick_labels.number_format
                    if nf in (None, '', 'General', '0.##############'):
                        issues.append(
                            f"{lbl4} '{sn}': chart value axis uses default number format "
                            f"'{nf}' — set explicit number_format ($, %, #,##0, etc.) "
                            f"matching the source data units"
                        )
            except Exception:
                pass  # some chart types lack a value axis

    # 12. Bullet paragraphs missing hanging indent
    for si5, slide5 in enumerate(prs.slides, start=1):
        lbl5 = f"Slide {si5}"
        for s in slide5.shapes:
            if s.is_placeholder or not s.has_text_frame:
                continue
            sn = s.name
            for p in s.text_frame.paragraphs:
                pPr = p._p.find(qn('a:pPr'))
                if pPr is None:
                    continue
                # Check if paragraph has a bullet (buChar or buAutoNum)
                has_bullet = (pPr.find(qn('a:buChar')) is not None or
                              pPr.find(qn('a:buAutoNum')) is not None)
                if has_bullet:
                    indent = pPr.get('indent')
                    if indent is None or int(indent) >= 0:
                        issues.append(
                            f"{lbl5} '{sn}': bullet paragraph missing hanging indent "
                            f"— call set_hanging_indent(paragraph)"
                        )
                        break  # one issue per shape

    # 13. Text box body font below target (22-24pt) but above minimum (20pt) — WARNING only
    warnings = []
    for si6, slide6 in enumerate(prs.slides, start=1):
        lbl6 = f"Slide {si6}"
        for s in slide6.shapes:
            if s.is_placeholder or s.has_chart or s.has_table:
                continue
            if s.shape_type == 13:
                continue
            if not s.has_text_frame:
                continue
            sn = s.name
            for p in s.text_frame.paragraphs:
                for run in p.runs:
                    if run.font.size is not None and Pt(20) <= run.font.size < Pt(22):
                        if run.font.italic and run.font.size <= Pt(12):
                            continue
                        warnings.append(
                            f"{lbl6} '{sn}': text box font {run.font.size.pt:.0f}pt "
                            f"(target is 22-24pt) — can content be reduced to allow "
                            f"a larger font?"
                        )
                        break
                else:
                    continue
                break
    if warnings:
        for w in warnings:
            issues.append(f"WARNING: {w}")

    # 14. Text overflow — estimated text height exceeds shape height
    import math
    for si7, slide7 in enumerate(prs.slides, start=1):
        lbl7 = f"Slide {si7}"
        for s in slide7.shapes:
            if s.is_placeholder or not s.has_text_frame:
                continue
            if s.has_chart or s.has_table:
                continue
            if s.shape_type == 13:  # MSO_SHAPE_TYPE.PICTURE
                continue
            sn = s.name
            shape_w = s.width / IN
            shape_h = s.height / IN
            if shape_h < 0.1:
                continue  # skip decorative/spacer shapes
            total_text_h = 0
            for p in s.text_frame.paragraphs:
                p_text = p.text
                if not p_text.strip():
                    total_text_h += 0.15  # blank paragraph spacing
                    continue
                font_pt = 20  # default assumption
                if p.runs and p.runs[0].font.size is not None:
                    font_pt = p.runs[0].font.size.pt
                chars_per_line = max(1, shape_w * 72 / (font_pt * 0.55))
                lines = math.ceil(len(p_text) / chars_per_line)
                total_text_h += lines * font_pt * 1.4 / 72
            if total_text_h > shape_h * 1.1:  # 10% tolerance
                overflow_pct = int((total_text_h / shape_h - 1) * 100)
                issues.append(
                    f"{lbl7} '{sn}': TEXT OVERFLOW — estimated {total_text_h:.2f}\" "
                    f"of text in {shape_h:.2f}\" box ({overflow_pct}% over) — "
                    f"reduce content, increase box height, or split across slides"
                )

    return issues


# --- Run before prs.save() ---
issues = run_quality_check(prs)
errors = [i for i in issues if not i.startswith("WARNING:")]
warnings = [i for i in issues if i.startswith("WARNING:")]
if errors:
    print(f"\nQUALITY CHECK FAILED — {len(errors)} error(s) found:")
    for e in errors:
        print(f"  - {e}")
    if warnings:
        print(f"\n  Plus {len(warnings)} warning(s):")
        for w in warnings:
            print(f"  - {w}")
    raise SystemExit("Fix the errors above before saving.")
elif warnings:
    print(f"\nQuality check passed with {len(warnings)} warning(s) ({len(prs.slides)} slides):")
    for w in warnings:
        print(f"  - {w}")
    print("Warnings do not block save. Review and address if content can be reduced.")
else:
    print(f"Quality check passed ({len(prs.slides)} slides).")

prs.save(output_path)
```

Fix every reported issue before saving. Do not skip or suppress the check. Common fixes:
- **Overlap**: adjust `top` or `height` of one of the overlapping shapes so bounding boxes no longer intersect
- **Out of bounds**: correct `left`, `top`, `width`, or `height` to fit within the content area constants
- **Chart fonts**: call `fix_chart_fonts(chart)` immediately after `add_chart()`
- **Line legend**: set `chart.legend.position = XL_LEGEND_POSITION.RIGHT` and `include_in_layout = False`
- **invertIfNegative**: add `<c:invertIfNegative val="0">` to each bar series element (see Bar Charts section above)
- **Table style**: set `tableStyleId` element text to `{00000000-0000-0000-0000-000000000000}`
- **Table fonts**: call `fix_table_fonts(table_shape)` after populating the table
- **Text box fonts**: increase to `Pt(22)` (target) or at minimum `Pt(20)`; if text does not fit, reduce content or split the slide rather than reducing font size
- **Conversion coverage**: reclassify image-only slides as hybrid (text column native + image column embedded), native shapes (colored boxes, flowcharts, box-and-arrow diagrams), or native charts (bar/line/scatter) per Step 2 decision rules
- **Chart number format**: set `chart.value_axis.tick_labels.number_format` to the appropriate format string and set `number_format_is_linked = False`; cross-reference the source for data units
- **Hanging indent**: call `set_hanging_indent(paragraph)` on every bullet paragraph to set proper `marL` and negative `indent`
- **Below-target font (WARNING)**: try setting to `Pt(24)` first; if content overflows, reduce content (fewer bullets, shorter text, split slide); only drop to `Pt(22)` or `Pt(20)` after content is already minimal
- **Text overflow**: reduce text content (shorten descriptions, remove items), increase box height (fewer items per slide = taller boxes), or change layout (switch from grid to bulleted list or table). Never ignore overflow; the rendered PPTX will clip or overlap

## Implementation Checklist

When generating slides, verify:

**Layout:**
- [ ] Title in placeholder, 36pt Calibri Bold, #4D4D4D (Charcoal); title is the key message
- [ ] No subtitle added; no title slide generated
- [ ] No key message boxes (no SlateNavy callout bar below the title)
- [ ] Content starts at `CONTENT_TOP = 1.95"`, never above the title bottom (1.826")
- [ ] All shapes start at `CONTENT_LEFT = 1.10"` or further right
- [ ] All shapes fill `CONTENT_W = 13.80"`; no narrower layouts that leave gaps on the right
- [ ] Blank space at bottom for footer (nothing below `FOOTER_TOP = 7.70"`)

**Typography:**
- [ ] Body text >= 20pt; no 18pt or smaller for slide content (18pt is hard floor for exceptional cases only)
- [ ] Use largest font that fits attractively (default 22-24pt; 20pt when density requires; 18pt absolute last resort)
- [ ] Table cells: explicit font size set (never rely on inherited defaults)
- [ ] Table cells: alignment explicitly set (never rely on inherited defaults)

**Multi-box layouts:**
- [ ] Equal-width boxes when layout is symmetric
- [ ] Box group fills full `CONTENT_W = 13.80"` with 0.5" gaps; no gap on right side

**Charts:**
- [ ] Line charts: legend = RIGHT
- [ ] Bar charts with negative values: `invertIfNegative` = 0 on all series
- [ ] Chart layout matches source (axis ranges, legend position, data labels)
- [ ] Chart axis number formats set explicitly ($, %, #,##0, etc.) matching source data units

**Citations:**
- [ ] Every `\sourcecite{}` in the Beamer source is reproduced as a citation text box in the PPTX
- [ ] Citation text boxes are right-justified, positioned just above `FOOTER_TOP`
- [ ] Citation formatting: 11pt Calibri Italic, MedGray (#B0AFA8)

**Text structure:**
- [ ] Related text (heading + bullets) is in ONE continuous text box, not split into separate boxes
- [ ] Beamer `\begin{itemize}` and `\begin{enumerate}` are reproduced as native PPTX bullets/numbered lists
- [ ] Bullet indentation uses `paragraph.level`, not manual spaces or dashes

**Visual:**
- [ ] Maximum 3-4 colors per slide
- [ ] No gradients, shadows, text shading, or effects
- [ ] White text on all filled boxes
- [ ] Pre-save structural quality check passes with no errors (run `run_quality_check(prs)` before `prs.save()`)
- [ ] No text overflow errors (estimated text height fits within shape height for every text box)
- [ ] Below-target font warnings reviewed and addressed where possible
- [ ] Grid layouts verified with `estimate_text_height()` on longest content before committing to layout

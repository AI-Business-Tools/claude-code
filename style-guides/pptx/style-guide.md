# PowerPoint Style Guide

Apply this style guide when creating PowerPoint presentations. Follow all specifications exactly.

## Note on Body-Text Color Across Media

The accent palette in this style guide matches the Beamer style guide exactly. **Body text differs intentionally:** PPTX uses Charcoal `#4D4D4D`, while Beamer uses CharText `#3A3A3A` (slightly darker). The rationale: PowerPoint output is typically projected via screen-mirror or shared in PDF viewers where `#3A3A3A` reads as visually heavy on backlit displays; LaTeX-rendered PDFs are typically printed or viewed at higher contrast where `#3A3A3A` reads correctly. If you generate a deck via Beamer and later convert to PPTX (or vice versa), expect body text to shift slightly between the two outputs. This is by design.

## Critical Rules (Most-Violated, Read First)

These rules are violated in nearly every PPTX generation. They override any conflicting code example or default assumption elsewhere in this file.

1. **Font size is role-based and computed, never a floor written as a literal.** Text must match the role-to-size hierarchy below. A single flat floor is wrong; citations legitimately use 11pt and diagram micro-labels use 14-16pt, while body text must stay at 22pt+. For every text element, compute the largest size in the role's range that fits the box (`fit_font_size()` in the canonical scaffold), then clamp at the role floor; a floor is what the computed size may not go below, never the size you assign. A generator that writes `size=22` as the default for every body run is the uniform-at-floor defect the quality check blocks. See "Role-Based Font Hierarchy" below.
2. **All readable text uses Charcoal (#4D4D4D).** Never use #B0AFA8 (MedGray) or #6C7A89 (Medium Gray) on body text, labels, headings, date labels, or any element that must be readable when projected. #B0AFA8 is exclusively for citation text boxes (`add_citation()`). #6C7A89 is for connector lines and neutral shape outlines only.
3. **No inline source references.** Present findings as factual statements. Author attribution goes exclusively in `add_citation()` text boxes at the canonical citation band at the bottom of the slide. Never write "Smith et al. (2024) found that..." in body text.
4. **The quality check is mandatory and blockers must be fixed.** Run `run_quality_check(prs)` before every `prs.save()`. Fix all errors (not just warnings) before saving.
5. **Native objects, not image embeds.** Colored boxes, flowcharts, box-and-arrow diagrams, tables, and standard charts must be recreated as native PowerPoint objects. Image embed is a last resort for irreducible visual complexity (Bezier curves, mathematical plots). If you are about to embed a full-slide image, stop and reclassify.
6. **Lock shape dimensions with `auto_size = MSO_AUTO_SIZE.NONE` on every text-containing text frame.** Every shape or text box that holds text (rounded rectangles with labels, cards, citations, text boxes, callouts) must explicitly set `text_frame.auto_size = MSO_AUTO_SIZE.NONE` immediately after the shape is created. python-pptx defaults vary by shape type, and Keynote's PDF export silently resizes auto-sized shapes (cards misalign, text frames grow beyond their coded height). Coded dimensions are only honored when `auto_size` is locked. Bake this into every wrapper helper (`add_rounded_card()`, `add_citation()`, direct `add_textbox()` calls). **Exempt:** purely decorative shapes that contain no text (e.g., a thin accent sliver or a background rectangle) do not need `auto_size` locked; there is nothing to resize. Also exempt: chart title/axis frames managed by python-pptx's chart API, and the Title placeholder provided by the template.
7. **Prevent PowerPoint "repaired and removed content" warnings.** python-pptx generates two structures that PowerPoint's strict validator flags as malformed; both must be neutralized in every PPTX:
   - **Auto-added `<p:style>` block on autoshapes.** When `add_shape()` creates a rounded rectangle (or any preset autoshape), python-pptx attaches a `<p:style>` element that references theme scheme colors (accent1, lt1, etc.). When the generator also sets explicit RGB fill and line via `spPr` (which `add_rounded_card()` does), PowerPoint sees the conflict and silently strips shapes during repair. **Fix:** remove the `<p:style>` element from the shape after `add_shape()` returns. `add_rounded_card()` does this automatically; if you create a custom autoshape helper with explicit fills, do the same.
   - **`<a:buChar>` without a paired `<a:buFont>`.** PowerPoint requires a typeface to render the bullet character. `set_bullet()` adds `<a:buFont typeface="Arial"/>` immediately before `<a:buChar>` to satisfy the schema. Do not write a custom bullet helper that emits only `<a:buChar>`.
   These regressions surface as "PowerPoint couldn't read some content - Repaired and removed it" on file open, which silently drops shapes the user expects to see. Both checks are enforced by `run_quality_check()` (see "Pre-Save Structural Quality Check"). Do not bypass either guard.

### Role-Based Font Hierarchy

Every text element on a slide has a role. Match the role to its target font size. Floors are blocking; above-target is acceptable if the content warrants emphasis.

| Role | Target | Floor (blocking) | Typical position/shape |
|---|---|---|---|
| Title | 36pt | 32pt | Title placeholder, T≈0.33", H≈1.49" |
| Category header (section label in a box) | 32pt | 28pt | Top of a rounded rectangle or column |
| Body primary (main text audience reads) | 24-28pt | 22pt | Bullet lists, paragraph body |
| Body secondary (supporting text, sub-bullets) | 22pt | 20pt | Continuation text, inset bullets |
| In-shape label (word inside a diagram node, row/column label) | 18-22pt | 16pt | Rounded rectangles or label boxes <3.5"W and <1.2"H, connector nodes |
| Diagram micro-label (connector annotation) | 14-16pt | 12pt | Small text boxes <2.5"W and <0.6"H |
| Chart axis, legend, data labels | 14pt | 14pt | Inside charts (handled by `fix_chart_fonts()`) |
| Chart caption or annotation text | 12pt | 11pt | Short explanatory text below/beside a chart |
| Citation | 11pt (fixed) | 11pt | Canonical citation band, T=8.00" |
| Footer, slide number | Template default | Template default | Footer placeholder |

Shape-size signals the role. A text box narrower than 2.5" and shorter than 0.6" is an annotation, not body text: allow down to 14pt. A text box occupying most of the slide width (>10") with standing multi-line content is body: floor at 22pt. Citations are identified by position (T between 7.5 and 8.25, H ≤ 0.80).

**Compute the size, then clamp (mandatory).** For each text element: start at the role's target ceiling (28pt for body primary), use `estimate_text_height()` to step down until the content fits the box, and apply `max(computed, floor)`. The canonical scaffold's `fit_font_size()` implements this; compute the size at the call site and pass the result as `size=`. Two guards so the computation cannot be gamed: the box itself must respect the content-area and grid-layout limits (a size only "fits" in a legitimately sized box, not an inflated one), and the overflow check still runs after sizing. The floor is reached only when content is already minimal; it is never the starting value.

When body content does not fit at its role's target, **reduce content**: split the slide, remove a bullet, condense phrasing. Never drop body text below 22pt. Symmetrically, when content sits far below its box capacity at the floor, the size was never computed: recompute upward toward the role ceiling rather than shipping small text in an under-filled box.

### Accent Colors on Card Category Headers

Card category headers (the label at the top of a rounded-rectangle card or column) default to **Charcoal** (`#4D4D4D`), matching body text. A palette accent color is appropriate when the card is **statistic-led**: its purpose is to surface a single headline number or short emphatic phrase, not to deliver prose.

| Card type | Header color | Example |
|---|---|---|
| Statistic-led (card leads with a large number or short emphasis) | Palette accent (DeepTeal, BurntOrange, SlateNavy, WarmAmber) | A three-card row showing "82%", "4.3x", "$1.2B" with short captions beneath |
| Content-led (card contains a paragraph, bullet list, or descriptive text) | Charcoal | A three-card row showing "Context", "Finding", "Implication" with explanatory text beneath |

This is positive guidance, not a blocking rule. Rule #2 (no grays on body text) remains the enforced floor; accent colors on statistic-led card headers are permitted above that floor.

---

## Typography

| Element | Specification |
|---------|---------------|
| Slide titles | 36pt Calibri Bold, #4D4D4D, in Title placeholder |
| Section headers within slides | 24-28pt Calibri Bold |
| Body text | **24-28pt target, 22pt floor** Calibri Regular, #4D4D4D (per the Role-Based Font Hierarchy, the canonical spec) |
| Minimum text size | Role floors per the Role-Based Font Hierarchy (body 22pt, body secondary 20pt, in-shape label 16pt; 14pt for chart axis labels and table content only) |
| Subtitles | NEVER use subtitles; title only, content below |

**Font size principle: compute the largest size that fits attractively, then clamp at the role floor.** The Role-Based Font Hierarchy in Critical Rules is the single canonical size spec; this table summarizes it and defers to it wherever they could be read to differ. Body text starts at its 24-28pt target and steps down via `fit_font_size()` only as the box requires; it reaches the 22pt floor only when content is already minimal (split the slide, remove a bullet, condense phrasing first). Never use 16pt or smaller for slide body text, and never write a floor value as a default.

## Layout Principles

- **Aspect ratio:** 16:9
- **Generous margins** and white space between elements
- **One main idea per slide**
- **Footer and citation zones:** Body content must stay above `CONTENT_BOTTOM = 8.00"`. The citation band occupies T=8.00 to T=8.25. The footer placeholder (slide number, copyright) occupies T=8.38 to T=8.86. On a 16x9 slide this gives 8.00 - 1.95 = 6.05" of content height below the title.
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
- Use SlateNavy (#1B2A4A) as primary fill for block titles, in-diagram emphasis boxes, and standalone reinforcement callouts (the Beamer `\callout`); recreate callouts as editable filled text boxes, used selectively as in the source, not on every slide
- Stick to 3 colors per slide, expand to 4 only when needed

### DON'T
- Use gradients, glows, drop shadows, or bevels on any element (text, shapes, charts, images)
- Use text shading, text highlighting, text background fills behind running text, or text shadows (a deliberate `\callout` reinforcement box, a filled shape with its own text, is not a text background fill and is permitted)
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
| **Native chart** | Standard bar, line, scatter, pie charts. Read the data points from the `.tex` source programmatically (see "Chart data fidelity" below); never re-key them by eye | `add_chart()` + `fix_chart_fonts()` + palette colors |
| **Native table** | Data tables | `add_table()` + `fix_table_fonts()` + `fix_table_style()` |
| **Native shapes/text** | Bullet points, text boxes, simple box layouts, colored boxes with text labels, box-and-arrow diagrams, flowcharts, stacked/layered layouts | `add_shape()` + `add_textbox()` with Calibri formatting |
| **Hybrid (text + image)** | Two-column Beamer slides where one column is text/bullets and the other is a complex visual | Native text box(es) for the text column + `add_image_proportional()` for the visual column |
| **Image embed** | LAST RESORT. The visual contains mathematical curve plots with axis annotations, or TikZ paths with Bezier curves/decorative elements that have no PowerPoint shape equivalent, AND it cannot be decomposed into rectangles, arrows, and text labels | Render at 300 DPI, crop, `add_image_proportional()` |

**Two-column Beamer slides:** Always recreate the text column as native text boxes at the computed fill size (body target 24-28pt via `fit_font_size()`, clamped at the 22pt floor; see "Font Size Rule for Conversion"). Then classify the slide by its visual column: standard bar/line/scatter/column chart → `native chart`; colored boxes, flowcharts, box-and-arrow diagrams, cards, comparison layouts → `native shapes`; data table → `native table`; complex visual that cannot be recreated (Bezier paths, choropleth maps, multi-panel composites) → `hybrid (text + image)`. The `hybrid` classification is reserved for when the visual column genuinely requires an image embed. A two-column slide with bullets + a native pgfplots bar chart is `native chart`, not hybrid. A full-slide image embed is only permitted when the slide has no separable text content.

**Image embed decision rules:**

- **ALWAYS native shapes** (never image embed): colored rectangles/boxes with text labels, box-and-arrow diagrams, flowcharts, stacked/layered layouts with labeled sections, simple node-and-edge diagrams, comparison layouts, tables, process flows with labeled steps
- **MAY be image embed** (requires written justification): mathematical function plots with axis annotations, complex pgfplots with many overlapping series and fill regions, TikZ diagrams with decorative elements (braces, Bezier curves, custom path decorations), choropleth maps, multi-panel composite figures

**For each slide marked "image embed," write one sentence justifying why it cannot be recreated natively.** If no justification exists, reclassify as native or hybrid.

**Callout boxes (`\callout` in the source).** A `\callout` is a standalone reinforcement box (dark fill, white bold text). Recreate it as a native editable filled text box: `add_rounded_card(slide, ..., border_rgb, fill_rgb)` plus a white text run, never a rasterized image, matching the source fill color. Reproduce only the callouts the Beamer source contains; never add new ones. Contrast: white text is recreated only on the dark source fills (SlateNavy, DeepTeal, AccentRed, DustyPlum, CyanBlue, BurntOrange). The source never fills a callout with green, amber, or soft red: those valences arrive as bold colored text on white (an ordinary editable text run, no fill). If you ever see white text on a light fill, that is a defect to correct, not reproduce.

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

Conversion sizes are **computed from the source's hierarchy, then clamped at the role floors**, never flattened to one value. Two steps per text element:

1. **Carry the Beamer hierarchy proportionally.** Map the source's relative sizes so the deck's visual hierarchy survives: `\normalsize` body anchors at ~24pt; `\large` above it (~28pt); `\Large`/`\LARGE` map to section-header/title sizes; `\small` body lands ~22-24pt; `\footnotesize` secondary text lands at the body-secondary tier; `\scriptsize` maps to its role (citation band, caption, micro-label). A `\large` heading must come out larger than a `\normalsize` body line; flattening every run to one size erases the hierarchy the Beamer deck had.
2. **Clamp at the role floors** (body 22pt, body secondary 20pt, per the Role-Based Font Hierarchy) and verify fit with `fit_font_size()`/`estimate_text_height()`.

**The PPTX layer cannot manufacture hierarchy the source lacks.** If the Beamer source is uniformly `\footnotesize`/`\small`, proportional mapping clamps most runs to the floor and the quality check's uniform-at-floor signature fires; the defect is upstream in `slides.tex`, and the right response is to report that, not to silently inflate PPTX fonts into a hierarchy the source never had. Apply sizing before any text-fidelity verification pass, and re-run the quality check after any post-verification correction (corrected text can change wrapping).

If the Beamer source has dense text that would require fonts below the role floor to fit in a PPTX text box, **reduce content, not font size.** Split the text across two slides, remove less critical bullets, or condense phrasing.

This applies to all native text boxes: bullet lists, labels, standalone text, hybrid slide text columns, and annotation text. The only exceptions are chart axis labels (14pt per chart font rules), table content (14pt minimum per table rules), and italic caption text (11pt per the caption pattern).

### Source Citation Handling

Every `\sourcecite{}` in the Beamer source must be carried over to the PPTX as a citation text box. Citations are not optional content; they are part of the slide.

**Canonical placement:** Fixed position at `L=1.10", T=8.00", W=13.80", H=0.25"` on a 16x9 slide. The citation band sits above the footer strip (footer placeholder occupies `T=8.38"` to `T=8.86"`). Right-aligned text within the full-width box.

**Canonical formatting:** 11pt Calibri non-italic, color #B0AFA8, right-aligned.

**Multi-source citations:** Separate sources with `; ` (semicolon space). Target a single line. If text would wrap, grow the box **upward** (reduce `T` while keeping the bottom edge fixed at `T + H = 8.25"`) so the citation never enters the footer strip.

| Lines | T | H |
|---|---|---|
| 1 | 8.00 | 0.25 |
| 2 | 7.75 | 0.50 |
| 3 | 7.50 | 0.75 |

```python
from pptx.enum.text import PP_ALIGN, MSO_AUTO_SIZE

CITATION_LEFT = 1.10
CITATION_W    = 13.80
CITATION_BOTTOM = 8.25   # fixed — citation never extends below this
CITATION_LINE_H = 0.25   # height per line

def add_citation(slide, citation_text, lines=1):
    """Add a right-aligned citation text box at the canonical location.

    Default: single-line, T=8.00, H=0.25. For multi-source or long citations
    that must wrap to 2 or 3 lines, pass lines=2 or lines=3; the box grows
    upward while the bottom edge stays fixed at 8.25.
    """
    h = CITATION_LINE_H * lines
    t = CITATION_BOTTOM - h
    txbox = slide.shapes.add_textbox(
        Inches(CITATION_LEFT), Inches(t),
        Inches(CITATION_W), Inches(h)
    )
    tf = txbox.text_frame
    tf.auto_size = MSO_AUTO_SIZE.NONE   # lock canonical height (Critical Rule 6)
    tf.word_wrap = True
    p = tf.paragraphs[0]
    p.alignment = PP_ALIGN.RIGHT
    run = p.add_run()
    run.text = citation_text
    run.font.size = Pt(11)
    run.font.italic = False
    run.font.color.rgb = RGBColor(0xB0, 0xAF, 0xA8)
    run.font.name = "Calibri"
    return txbox
```

**Extraction:** Parse each slide's `\sourcecite{...}` content from the `.tex` source. Strip LaTeX formatting (drop `\textit{}` wrappers to produce plain text; backslash escapes become their characters). If a slide has `\sourcecite{}`, the PPTX slide must have a citation text box. If a slide has no `\sourcecite{}`, do not add one.

**Line count estimation:** With Calibri 11pt at a 13.80" width, a single line fits approximately 160-180 characters. Pass `lines=2` when the citation text exceeds ~160 characters or when it contains two or more sources joined by `; `. Pass `lines=3` only for genuinely long multi-source citations (>320 characters).

### Vertical Text Alignment

All text frames in content shapes (text boxes, rounded rectangles, auto shapes) must use **top vertical alignment** by default. python-pptx defaults rounded rectangles to middle alignment, which pushes text down from the top edge and creates inconsistent visual spacing. Set `text_frame.vertical_anchor = MSO_ANCHOR.TOP` explicitly on every shape that contains text.

```python
from pptx.enum.text import MSO_ANCHOR, MSO_AUTO_SIZE

# After creating a shape or text box:
tf = shape.text_frame
tf.auto_size = MSO_AUTO_SIZE.NONE    # lock dimensions (Critical Rule 6)
tf.vertical_anchor = MSO_ANCHOR.TOP  # always set explicitly
```

Middle alignment (`MSO_ANCHOR.MIDDLE`) is acceptable only for single-line labels inside small boxes (e.g., cycle diagram nodes, connector labels) where the text should be vertically centered. For any box with a title and body text, multi-line content, or bullet lists, use top alignment.

### Text Box Consolidation

Related text content on a slide must go in **one continuous text box** with paragraph-level formatting, not split into multiple separate text boxes.

**Rule:** When a Beamer slide has a text column containing a heading followed by bullet points (or multiple formatted paragraphs), recreate this as a single text box with multiple paragraphs. Use paragraph-level properties for differentiation:

- **Section headers within a text box:** Bold run, sized 2-4pt above the body size (see the canonical scaffold's `body_pt + 4` pattern)
- **Bullet points:** Normal weight, at the computed body size (22pt floor), with `paragraph.level` set to create indent
- **Sub-bullets:** 20pt, `paragraph.level = 1` for additional indent
- **Spacing between sections:** Use `paragraph.space_before = Pt(12)` to separate logical sections within one text box

**Do not** create separate text boxes for a heading and its bullets, or for each bullet point individually. A single text column should be ONE text box with multiple paragraphs.

```python
from pptx.util import Inches, Pt, Emu
from pptx.enum.text import PP_ALIGN, MSO_AUTO_SIZE
from pptx.dml.color import RGBColor

# Single text box with header + bullets:
tf = txbox.text_frame
tf.auto_size = MSO_AUTO_SIZE.NONE   # lock dimensions (Critical Rule 6)
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

def set_bullet(paragraph, level=0, bullet_char='\u2022', typeface='Arial'):
    """Set a bullet character on a paragraph.

    Always pairs <a:buFont typeface="..."/> with <a:buChar/>; PowerPoint
    flags <a:buChar> alone as malformed and strips the bullet during repair.
    """
    paragraph.level = level
    pPr = paragraph._p.get_or_add_pPr()
    # Bullet font (typeface) must precede bullet char per OOXML schema order
    for existing in pPr.findall(qn('a:buFont')):
        pPr.remove(existing)
    buFont = etree.SubElement(pPr, qn('a:buFont'))
    buFont.set('typeface', typeface)
    # Bullet character
    for existing in pPr.findall(qn('a:buChar')):
        pPr.remove(existing)
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

### Chart data fidelity: read the points, do not re-key them

**The data for a native chart must be READ from `slides.tex`, never transcribed by eye.** Re-keying chart numbers from a glance at the source is how a 17-point monthly curve once became a 4-point yearly one with nobody noticing: the result looked plausible and no check compared the data (only text and composition were checked). Remove the eyeball step with a parser, and add a verification pass that compares the built chart back against the source.

**The pattern.** Write (or reuse) a small parser that reads the pgfplots coordinate values out of `slides.tex`: one chart record per `\begin{axis}` in document order, each carrying the frame title, the chart kind (bar vs. line), whether x is numeric or categorical, every series' `(x, y)` points and legend label, any reference lines drawn as `\draw (axis cs:..) -- (axis cs:..)`, and any raw spans it could not parse. Exclude forget-plot and fill-region series from the data series. Coalesce the one-`\addplot`-per-bar idiom into a single series, so a bar chart reads as one series of N points, matching its single PPTX category series.

**Prevention: feed the parsed points into the chart.** When building a native chart, take its categories and values from the parsed record for that slide (keyed on the frame title), not from a mental summary of the source.

**Axis-type rule.** When the source x-coordinates are continuous or unevenly spaced (true time, decimals, gaps), build an **XY chart** (`XL_CHART_TYPE.XY_SCATTER_LINES*` with `XyChartData`), not a category chart. Collapsing a numeric time axis onto evenly spaced text categories silently distorts the chart. Use a category chart (`CategoryChartData`) only when x is sequential integer positions or symbolic categories.

**Markers.** If the source draws reference lines (e.g., a dashed vertical event marker), reproduce each as a thin two-point series (or a line shape) at its exact x, so the source reference line survives into the PPTX.

**Charts the parser cannot read.** If a chart contains spans the parser refused (a function/expression plot, error bars) or the figure is a rendered image embed, the parser cannot supply points; hand-build the chart AND flag it as unverified for manual review. Never hand-key a chart silently.

**Verification (mandatory, pre-save).** After the deck is built and `run_quality_check()` passes, verify every native chart's series against the source coordinates (matching by slide title, then series name) and report three classes of finding:

- **Divergence**: a value differs; the source is truth, correct the PPTX series and re-run.
- **Unverified**: a structural mismatch (point or series count), or a source the parser could not read (so the chart was hand-built); review it, do not ship it silently.
- **Marker**: a source reference line with no matching PPTX series; confirm it was preserved.

An empty report means every native chart matched the source within tolerance. A non-empty report is never a silent pass; surface it. This is the chart analog of the text-fidelity verification pass, and it inherits the same fail-loud contract: a chart the verification cannot confirm is reported, never assumed correct.

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

### Table style: mandatory XML fix

python-pptx's `add_table()` produces a table whose `<a:tableStyleId>` is the **null GUID** `{00000000-0000-0000-0000-000000000000}`. This GUID **crashes LibreOffice 26 on PPTX import**. Setting a real built-in style GUID avoids the crash. The canonical safe choice is `{2D5ABB26-0587-4C30-8999-92F81FD0307C}` ("No Style, No Grid"), which provides no visual styling and does not override cell-level paragraph alignment.

Two GUIDs are forbidden:
- `{00000000-0000-0000-0000-000000000000}` (null): crashes LibreOffice 26.
- `{5C22544A-7EE6-4342-B048-85BDC9FD1C3A}` ("Medium Style 2 - Accent 1"): silently overrides `para.alignment = PP_ALIGN.CENTER` and similar cell-level specs.

```python
def fix_table_style(table_shape):
    """Set table style to the canonical safe built-in GUID.

    {2D5ABB26-0587-4C30-8999-92F81FD0307C} = "No Style, No Grid":
    minimal styling, no alignment override, LibreOffice 26 compatible.
    """
    SAFE_STYLE = '{2D5ABB26-0587-4C30-8999-92F81FD0307C}'
    tbl_el = None
    for el in table_shape._element.iter():
        if el.tag.split('}')[-1] == 'tbl':
            tbl_el = el; break
    if tbl_el is None: return
    tbl_pr = tbl_el.find(qn('a:tblPr'))
    if tbl_pr is None:
        tbl_pr = etree.SubElement(tbl_el, qn('a:tblPr'))
        tbl_el.insert(0, tbl_pr)
    sid = tbl_pr.find(qn('a:tableStyleId'))
    if sid is None:
        sid = etree.SubElement(tbl_pr, qn('a:tableStyleId'))
    sid.text = SAFE_STYLE

# Call after add_table() and fix_table_fonts():
fix_table_style(table_shape)
```

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

## Canonical Generator Template

This is the known-good starter scaffold for a new PPTX generator. Every helper below bakes in the rules defined earlier (auto_size locked, Charcoal body text, canonical citation, hanging indents), so copy-paste extension produces compliant output without re-deriving each rule.

**Use this as the starting point for every PPTX script.** Adapt the slide loop to the deck's content, but do not edit the helper bodies without a clear reason; they encode the rules.

```python
"""Canonical PPTX generator scaffold.

Starting point for any new deck. Every helper enforces the style guide's
rules (auto_size=NONE, Charcoal default, canonical citation, hanging
indents on bullets). Extend the slide section; leave helpers alone.
"""
import math, os, sys
from pptx import Presentation
from pptx.util import Inches, Pt
from pptx.dml.color import RGBColor
from pptx.enum.text import PP_ALIGN, MSO_ANCHOR, MSO_AUTO_SIZE
from pptx.enum.shapes import MSO_SHAPE
from pptx.oxml.ns import qn
from lxml import etree

TEMPLATE_PATH = "path/to/your-template.pptx"  # set this for your project
OUTPUT_PATH = '/absolute/path/to/deck.pptx'   # edit me

IN = 914400   # EMU per inch

# --- Layout constants -------------------------------------------------------
CONTENT_LEFT   = 1.10
CONTENT_TOP    = 1.95
CONTENT_W      = 13.80
CONTENT_BOTTOM = 8.00
CITATION_LEFT   = 1.10
CITATION_W      = 13.80
CITATION_BOTTOM = 8.25
CITATION_LINE_H = 0.25

# --- Palette ---------------------------------------------------------------
CHARCOAL   = RGBColor(0x4D, 0x4D, 0x4D)   # body text default
SLATE_NAVY = RGBColor(0x1B, 0x2A, 0x4A)
DEEP_TEAL  = RGBColor(0x0D, 0x73, 0x77)
CYAN_BLUE  = RGBColor(0x00, 0x77, 0xB6)
DUSTY_PLUM = RGBColor(0x9B, 0x59, 0x78)
WARM_AMBER = RGBColor(0xE8, 0x91, 0x3A)
ACCENT_RED = RGBColor(0xC0, 0x39, 0x2B)
MED_GRAY   = RGBColor(0xB0, 0xAF, 0xA8)   # citations ONLY
PALE_BLUE  = RGBColor(0xE8, 0xF0, 0xF8)
WHITE      = RGBColor(0xFF, 0xFF, 0xFF)

def tint(rgb, pct):
    """Mix rgb with white. pct=12 → 12% of color, 88% white."""
    r = int(rgb[0] + (255 - rgb[0]) * (1 - pct / 100))
    g = int(rgb[1] + (255 - rgb[1]) * (1 - pct / 100))
    b = int(rgb[2] + (255 - rgb[2]) * (1 - pct / 100))
    return RGBColor(r, g, b)

# --- Helpers (rules baked in) ----------------------------------------------
def set_bullet(paragraph, level=0, bullet_char='•', typeface='Arial'):
    """Always pairs <a:buFont/> with <a:buChar/>; PowerPoint flags
    <a:buChar> alone as malformed and strips the bullet during repair."""
    paragraph.level = level
    pPr = paragraph._p.get_or_add_pPr()
    for existing in pPr.findall(qn('a:buFont')):
        pPr.remove(existing)
    buFont = etree.SubElement(pPr, qn('a:buFont'))
    buFont.set('typeface', typeface)
    for existing in pPr.findall(qn('a:buChar')):
        pPr.remove(existing)
    buChar = etree.SubElement(pPr, qn('a:buChar'))
    buChar.set('char', bullet_char)

def set_hanging_indent(paragraph, margin_inches=0.30, indent_inches=-0.25):
    pPr = paragraph._p.get_or_add_pPr()
    pPr.set('marL', str(int(Inches(margin_inches))))
    pPr.set('indent', str(int(Inches(indent_inches))))

def add_citation(slide, text, lines=1):
    """Canonical citation band. Grows upward for multi-line; bottom fixed at 8.25."""
    h = CITATION_LINE_H * lines
    t = CITATION_BOTTOM - h
    tb = slide.shapes.add_textbox(
        Inches(CITATION_LEFT), Inches(t), Inches(CITATION_W), Inches(h))
    tf = tb.text_frame
    tf.auto_size = MSO_AUTO_SIZE.NONE
    tf.word_wrap = True
    tf.margin_left = tf.margin_right = Inches(0.05)
    tf.margin_top = tf.margin_bottom = Inches(0.02)
    p = tf.paragraphs[0]
    p.alignment = PP_ALIGN.RIGHT
    r = p.add_run()
    r.text = text
    r.font.size = Pt(11)
    r.font.italic = False
    r.font.name = "Calibri"
    r.font.color.rgb = MED_GRAY
    return tb

def add_rounded_card(slide, left, top, w, h, border_rgb, fill_rgb):
    """Rounded rectangle with canonical text-frame setup."""
    shape = slide.shapes.add_shape(
        MSO_SHAPE.ROUNDED_RECTANGLE,
        Inches(left), Inches(top), Inches(w), Inches(h))
    shape.line.color.rgb = border_rgb
    shape.line.width = Pt(1)
    shape.fill.solid()
    shape.fill.fore_color.rgb = fill_rgb
    shape.adjustments[0] = 0.08
    # Strip the auto-added <p:style> theme-color block. python-pptx attaches
    # it on every preset autoshape, but it conflicts with the explicit srgb
    # fill/line set above and causes PowerPoint to "repair and remove" the
    # shape on file open. (Critical Rule 7.)
    sp_el = shape._element
    style_el = sp_el.find(qn('p:style'))
    if style_el is not None:
        sp_el.remove(style_el)
    tf = shape.text_frame
    tf.auto_size = MSO_AUTO_SIZE.NONE
    tf.word_wrap = True
    tf.margin_left = tf.margin_right = Inches(0.20)
    tf.margin_top = tf.margin_bottom = Inches(0.15)
    tf.vertical_anchor = MSO_ANCHOR.TOP
    return shape

def add_body_textbox(slide, left, top, w, h):
    """Plain text box with canonical defaults."""
    tb = slide.shapes.add_textbox(Inches(left), Inches(top), Inches(w), Inches(h))
    tf = tb.text_frame
    tf.auto_size = MSO_AUTO_SIZE.NONE
    tf.word_wrap = True
    tf.vertical_anchor = MSO_ANCHOR.TOP
    return tb

def add_paragraph(tf, text, size=24, bold=False, color=CHARCOAL,
                  bullet=False, space_before=None, alignment=PP_ALIGN.LEFT,
                  first=False):
    """Add a paragraph; `first=True` reuses tf.paragraphs[0] (empty default)."""
    p = tf.paragraphs[0] if first else tf.add_paragraph()
    p.alignment = alignment
    if space_before is not None:
        p.space_before = Pt(space_before)
    if bullet:
        set_bullet(p)
        set_hanging_indent(p)
    r = p.add_run()
    r.text = text
    r.font.size = Pt(size)
    r.font.bold = bold
    r.font.name = "Calibri"
    r.font.color.rgb = color
    return p

def estimate_text_height(text, box_width_inches, font_size_pt, line_spacing=1.4):
    """Estimated rendered height in inches (same function as Content Fitting)."""
    chars_per_line = max(1, box_width_inches * 72 / (font_size_pt * 0.55))
    lines_needed = math.ceil(len(text) / chars_per_line)
    return lines_needed * font_size_pt * line_spacing / 72

ROLE_RANGES = {              # (ceiling, floor) pt, per Role-Based Font Hierarchy
    'body':           (28, 22),
    'body_secondary': (22, 20),
    'label':          (22, 16),
    'micro':          (16, 12),
}

def fit_font_size(paragraph_texts, box_w, box_h, role='body'):
    """Largest size in the role's range whose stacked estimated height fits the box.

    Compute-then-clamp (Critical Rule 1): start at the role ceiling, step down
    1pt while the estimated total height exceeds the box height, stop at the
    role floor. The floor is a clamp on the computed value, never the starting
    size — do not write a floor literal as a default. The box itself must
    respect the content-area and grid limits (an oversized box does not make a
    size "fit"), and the overflow check in run_quality_check() still applies.
    """
    ceiling, floor = ROLE_RANGES[role]
    size = ceiling
    while size > floor:
        total = sum(estimate_text_height(t, box_w, size) for t in paragraph_texts)
        if total <= box_h * 0.92:    # margin for paragraph spacing
            return size
        size -= 1
    return floor

def add_title(slide, text):
    ph = slide.placeholders[0]
    ph.text = ""
    p = ph.text_frame.paragraphs[0]
    p.alignment = PP_ALIGN.LEFT
    r = p.add_run()
    r.text = text
    r.font.size = Pt(36)
    r.font.bold = True
    r.font.name = "Calibri"
    r.font.color.rgb = CHARCOAL
    return ph

def remove_existing_slides(prs):
    xml_slides = prs.slides._sldIdLst
    for sldId in list(xml_slides):
        prs.part.drop_rel(sldId.get(qn('r:id')))
        xml_slides.remove(sldId)

# --- Build deck ------------------------------------------------------------
prs = Presentation(TEMPLATE_PATH)
remove_existing_slides(prs)

title_only = next(
    (l for l in prs.slide_layouts if l.name == "Title Only"),
    prs.slide_layouts[5])

# ------ Slide 1 (replace with real content) ------
slide = prs.slides.add_slide(title_only)
add_title(slide, "Your Title Here (the key message)")

card = add_rounded_card(slide,
    left=CONTENT_LEFT, top=CONTENT_TOP + 0.10,
    w=CONTENT_W, h=5.00,
    border_rgb=DEEP_TEAL, fill_rgb=tint(DEEP_TEAL, 8))
tf = card.text_frame
# Compute the body size for this box, then pass it — never hardcode a floor.
bullets = ["First supporting bullet.", "Second supporting bullet."]
body_pt = fit_font_size(["Section header"] + bullets, box_w=CONTENT_W - 0.4, box_h=4.6, role='body')
add_paragraph(tf, "Section header", size=body_pt + 4, bold=True, first=True)
add_paragraph(tf, bullets[0], size=body_pt, bullet=True, space_before=10)
add_paragraph(tf, bullets[1], size=body_pt, bullet=True, space_before=10)

add_citation(slide, "Author, First. YYYY. Title. Publication.")

# ------ Add more slides the same way ------

# --- Quality check + save --------------------------------------------------
# run_quality_check() is defined in the Pre-Save Structural Quality Check
# section below; copy that function into this file (or import it).
issues = run_quality_check(prs)
errors = [i for i in issues if not i.startswith("WARNING:")]
warnings = [i for i in issues if i.startswith("WARNING:")]

if errors:
    print(f"QUALITY CHECK FAILED — {len(errors)} error(s):")
    for e in errors:
        print(f"  • {e}")
    sys.exit("Fix errors before saving.")
if warnings:
    print(f"Quality check passed with {len(warnings)} warning(s):")
    for w in warnings:
        print(f"  • {w}")
else:
    print(f"Quality check passed ({len(prs.slides)} slides).")

prs.save(OUTPUT_PATH)
print(f"Saved: {OUTPUT_PATH}")
```

**Extension guidance:**

- For charts, call `fix_chart_fonts(chart)` immediately after `add_chart()`; see "Chart and Diagram Conversion" above for the full function body and axis/legend rules.
- For tables, use `add_table()` then call `fix_table_fonts()` and `fix_table_style()`; see "Tables" above.
- For multi-column layouts, compute column widths from `CONTENT_W` using the formula `(CONTENT_W - (n-1)*GAP) / n` (see "Multi-Box Layouts").
- For multi-line citations, pass `lines=2` or `lines=3` to `add_citation()`.
- If a body shape needs `MSO_ANCHOR.MIDDLE` (single-line label), set `tf.vertical_anchor = MSO_ANCHOR.MIDDLE` after `add_rounded_card()`; do not remove the `auto_size = NONE` assignment.

## Pre-Save Structural Quality Check

**Run this check on every PPTX before calling `prs.save()`.** It catches the most common generation errors that are invisible to visual inspection of the code: overlapping shapes, out-of-bounds positioning, hardcoded small fonts in chart XML, bad table style GUIDs, and missing legend/color rules.

```python
def run_quality_check(prs, conversion_source=None):
    """
    Structural quality check. Returns a list of issue strings.
    Empty list = all clear. Run before prs.save().

    conversion_source: path to the Beamer slides.tex when this PPTX is a
    conversion; None for direct generation. Controls the severity of the
    uniform-at-floor check (#18): blocking error at generation (the generator
    controls sizes and must compute them), surfaced warning at conversion
    (the PPTX inherits the source; the fix is upstream in slides.tex).

    Catches:
      1. Shapes outside content area bounds (role-aware: citations may sit in
         the citation band)
      2. Overlapping shapes on the same slide
      3. Chart axis/legend font < 14pt (hardcoded in XML by python-pptx)
      4. Line chart legend not positioned RIGHT
      5. Bar chart series missing invertIfNegative=0 (causes unfilled negative bars)
      6. Table using built-in style GUID that overrides cell alignment
      7. Table cell font < 14pt
      8. Conversion coverage — flags when >40% of slides are single-image-only
         (with reclassification guidance: hybrid, native shapes, or native chart)
      9. Vertical alignment is MIDDLE on multi-line content shapes (should be TOP)
     10. Role-based font floor — citation 11pt, micro-label 12pt, in-shape label
         16pt, body 22pt; role inferred from shape position and size
     11. Chart axis number format left as default (warns to apply explicit number_format)
     12. Bullet paragraphs missing hanging indent (negative indent attribute)
     13. Text box body font below target (20-21pt) — warning, not blocker
     14. Text overflow — estimated text height exceeds shape height by >10%
     15. Off-spec gray color on body text — gray-toned run color not in the approved
         gray whitelist (catches regressions like #3A3A3A in place of Charcoal)
     16. <p:style> theme block conflicting with explicit srgb fill/line on a shape
         (PowerPoint repair-and-remove)
     17. <a:buChar> without paired <a:buFont> (PowerPoint strips the bullet)
     18. Uniform-at-floor signature — >50% of body-role runs within 1pt of the 22pt
         floor (min 8 body runs). ERROR at generation; WARNING with an upstream
         pointer when conversion_source is set.
     19. Box under-fill — estimated text height under 60% of the box height while a
         larger in-role size would fit (WARNING; compute the size, then clamp)
    """
    from pptx.oxml.ns import qn
    from pptx.enum.chart import XL_LEGEND_POSITION

    IN = 914400
    CONTENT_LEFT = 1.10;  CONTENT_TOP = 1.95
    CONTENT_W   = 13.80
    # Body content must end above CONTENT_BOTTOM (leaves room for citation band).
    # Citations live in the citation band at T=8.00 to T=8.25.
    # Actual footer placeholder begins at 8.38.
    CONTENT_BOTTOM  = 8.00   # body content max bottom edge
    CITATION_BOTTOM = 8.25   # citation max bottom edge
    FOOTER_TOP      = CONTENT_BOTTOM  # legacy alias
    MAX_RIGHT = CONTENT_LEFT + CONTENT_W   # 14.90

    # Null GUID — python-pptx's add_table() default. Crashes LibreOffice 26
    # on PPTX import. Treat as a save blocker.
    NULL_STYLE = '{00000000-0000-0000-0000-000000000000}'
    # "Medium Style 2 - Accent 1" — silently overrides cell-level paragraph alignment.
    OVERRIDE_STYLE = '{5C22544A-7EE6-4342-B048-85BDC9FD1C3A}'
    # Canonical safe built-in: "No Style, No Grid" — minimal styling, no alignment override.
    SAFE_STYLE = '{2D5ABB26-0587-4C30-8999-92F81FD0307C}'

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

        # 1. Position bounds (role-aware)
        for s, l, t, w, h in content:
            n = s.name
            # Detect citation role by position — allowed in citation band
            is_citation = (7.4 <= t <= 8.3 and h <= 0.85)
            if l < CONTENT_LEFT - 0.05:
                issues.append(f"{lbl} '{n}': left={l:.2f}\" (need >={CONTENT_LEFT}\")")
            if t < CONTENT_TOP - 0.05 and not is_citation:
                issues.append(f"{lbl} '{n}': top={t:.2f}\" (need >={CONTENT_TOP}\")")
            # Body content stays above CONTENT_BOTTOM; citations stay above CITATION_BOTTOM
            if is_citation:
                if t + h > CITATION_BOTTOM + 0.05:
                    issues.append(f"{lbl} '{n}': citation bottom={t+h:.2f}\" (need <={CITATION_BOTTOM}\" — would enter footer strip)")
            else:
                if t + h > CONTENT_BOTTOM + 0.05:
                    issues.append(f"{lbl} '{n}': bottom={t+h:.2f}\" (need <={CONTENT_BOTTOM}\" — citation band)")
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

            # 6. Table style GUID checks.
            #    a) Null GUID crashes LibreOffice 26 on PPTX import (BLOCKER).
            #    b) OVERRIDE_STYLE silently overrides cell-level paragraph alignment.
            tbl_pr = tbl_el.find(qn('a:tblPr'))
            if tbl_pr is not None:
                sid = tbl_pr.find(qn('a:tableStyleId'))
                if sid is not None and sid.text:
                    sid_norm = sid.text.strip().upper()
                    if sid_norm == NULL_STYLE.upper():
                        issues.append(
                            f"{lbl} '{sn}': table uses null GUID {NULL_STYLE} "
                            f"— crashes LibreOffice 26 on PPTX import. Run "
                            f"fix_table_style(table_shape) to set {SAFE_STYLE} "
                            f"(\"No Style, No Grid\")."
                        )
                    elif sid_norm == OVERRIDE_STYLE.upper():
                        issues.append(
                            f"{lbl} '{sn}': table uses built-in style {OVERRIDE_STYLE} "
                            f"which overrides cell alignment — run "
                            f"fix_table_style(table_shape) to set {SAFE_STYLE}."
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

    # 10. Role-based font floor check.
    #     Role is inferred from shape position and size:
    #       - Citation band (T in 7.4-8.3, H <= 0.85): floor = 11pt
    #       - Small annotation (W < 2.5" AND H < 0.6"): floor = 12pt (micro-label role)
    #       - In-shape label (W < 3.5" AND H < 1.2"): floor = 16pt (label role)
    #       - Everything else: floor = 22pt (body role)
    #     Violations below the role floor are errors.
    def _role_floor(left_in, top_in, width_in, height_in):
        if 7.4 <= top_in <= 8.3 and height_in <= 0.85:
            return ("citation", 11)
        if width_in < 2.5 and height_in < 0.6:
            return ("micro-label", 12)
        if width_in < 3.5 and height_in < 1.2:
            return ("in-shape label", 16)
        return ("body", 22)

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
            if s.left is None:
                continue
            sn = s.name
            l_in, t_in = s.left/IN, s.top/IN
            w_in, h_in = s.width/IN, s.height/IN
            role, floor_pt = _role_floor(l_in, t_in, w_in, h_in)
            for p in s.text_frame.paragraphs:
                for run in p.runs:
                    if run.font.size is not None and run.font.size < Pt(floor_pt):
                        issues.append(
                            f"{lbl3} '{sn}': {role} font {run.font.size.pt:.0f}pt "
                            f"(need >={floor_pt}pt for this role) — "
                            f"{'reduce content' if role == 'body' else 'adjust role or size'}"
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

    # 15. Off-spec gray color on body text.
    #     A run's color is "gray-toned" when max(R,G,B) - min(R,G,B) <= 15.
    #     Gray-toned runs must match one of the approved palette grays below.
    #     This catches near-Charcoal regressions like #3A3A3A, #555555, #333333
    #     without flagging colored accent runs (SlateNavy emphasis, DeepTeal
    #     highlight text, etc.), which are NOT gray-toned and so are skipped.
    #
    #     Carve-outs (already implied by the gray-tone filter; stated for clarity):
    #       - Citation text boxes are skipped by position (citation band).
    #       - Charts are skipped (has_chart).
    #       - Tables are skipped (has_table).
    #       - Images are skipped (shape_type == 13).
    #       - Accent-colored runs are skipped because their colors are not gray-toned.
    APPROVED_GRAYS = {
        (0x4D, 0x4D, 0x4D),  # Charcoal — primary body text
        (0xB0, 0xAF, 0xA8),  # MedGray — citation only
        (0x6C, 0x7A, 0x89),  # Medium Gray — connectors/neutral states
        (0x42, 0x55, 0x63),  # Slate Blue — default outlines
        (0xF0, 0xEF, 0xEC),  # LightGray — spare fill
        (0xFF, 0xFF, 0xFF),  # White — text on dark fills
        (0x00, 0x00, 0x00),  # Black — occasional emphasis
    }
    for si8, slide8 in enumerate(prs.slides, start=1):
        if slide8._element.get('show') == '0':
            continue
        lbl8 = f"Slide {si8}"
        for s in slide8.shapes:
            if s.is_placeholder or s.has_chart or s.has_table:
                continue
            if s.shape_type == 13:
                continue
            if not s.has_text_frame:
                continue
            # Skip citation shapes (authorized MedGray by role)
            if s.left is not None:
                t_in = s.top / IN
                h_in = s.height / IN
                if 7.4 <= t_in <= 8.3 and h_in <= 0.85:
                    continue
            sn = s.name
            reported_this_shape = False
            for p in s.text_frame.paragraphs:
                if reported_this_shape:
                    break
                for run in p.runs:
                    try:
                        rgb = run.font.color.rgb
                    except AttributeError:
                        continue
                    if rgb is None:
                        continue
                    hex_str = str(rgb)
                    if len(hex_str) != 6:
                        continue
                    try:
                        r = int(hex_str[0:2], 16)
                        g = int(hex_str[2:4], 16)
                        b = int(hex_str[4:6], 16)
                    except ValueError:
                        continue
                    spread = max(r, g, b) - min(r, g, b)
                    if spread > 15:
                        continue   # colored accent, not gray-toned — skip
                    if (r, g, b) in APPROVED_GRAYS:
                        continue
                    issues.append(
                        f"{lbl8} '{sn}': off-spec gray #{hex_str.upper()} on body text "
                        f"— use #4D4D4D (Charcoal); MedGray #B0AFA8 is reserved for citations"
                    )
                    reported_this_shape = True
                    break

    # 16. PowerPoint repair-warning prevention: <p:style> conflicting with explicit srgb fill.
    #     python-pptx auto-attaches a <p:style> theme-color block to every preset autoshape.
    #     When the generator also sets explicit srgb fill or line via spPr (as add_rounded_card
    #     does), PowerPoint detects the conflict and silently strips the shape during repair
    #     ("PowerPoint couldn't read some content - Repaired and removed it"). Critical Rule 7.
    #
    #     Detection: shape has both <p:style> AND explicit <a:solidFill> in spPr. Either:
    #       - drop <p:style> after add_shape() (preferred; bake into helpers), or
    #       - rely on <p:style> theme colors and remove the explicit srgb fill.
    p_ns = 'http://schemas.openxmlformats.org/presentationml/2006/main'
    a_ns = 'http://schemas.openxmlformats.org/drawingml/2006/main'
    for si9, slide9 in enumerate(prs.slides, start=1):
        if slide9._element.get('show') == '0':
            continue
        lbl9 = f"Slide {si9}"
        for s in slide9.shapes:
            if s.is_placeholder or s.has_chart or s.has_table:
                continue
            if s.shape_type == 13:  # picture
                continue
            sp_el = s._element
            style_el = sp_el.find(f'{{{p_ns}}}style')
            sp_pr = sp_el.find(f'{{{p_ns}}}spPr')
            if style_el is not None and sp_pr is not None:
                has_explicit_fill = sp_pr.find(f'{{{a_ns}}}solidFill') is not None
                has_explicit_line = sp_pr.find(f'{{{a_ns}}}ln') is not None
                if has_explicit_fill or has_explicit_line:
                    issues.append(
                        f"{lbl9} '{s.name}': <p:style> theme-color block conflicts with "
                        f"explicit srgb fill/line in spPr — PowerPoint will repair-and-remove "
                        f"on file open. Drop the <p:style> element after add_shape(); see "
                        f"add_rounded_card() for the canonical fix."
                    )

    # 17. PowerPoint repair-warning prevention: <a:buChar> without paired <a:buFont>.
    #     PowerPoint requires a typeface to render the bullet character. A bare <a:buChar>
    #     element is flagged as malformed and the bullet is stripped during repair, so the
    #     paragraph renders without its leading bullet. Critical Rule 7.
    for si10, slide10 in enumerate(prs.slides, start=1):
        if slide10._element.get('show') == '0':
            continue
        lbl10 = f"Slide {si10}"
        for s in slide10.shapes:
            if not s.has_text_frame:
                continue
            sn = s.name
            for p in s.text_frame.paragraphs:
                pPr = p._p.find(qn('a:pPr'))
                if pPr is None:
                    continue
                buChar = pPr.find(qn('a:buChar'))
                if buChar is None:
                    continue
                buFont = pPr.find(qn('a:buFont'))
                if buFont is None or not buFont.get('typeface'):
                    issues.append(
                        f"{lbl10} '{sn}': <a:buChar> without paired <a:buFont typeface=...> "
                        f"— PowerPoint will repair-and-remove the bullet. Use set_bullet() "
                        f"which always pairs the two."
                    )
                    break  # one issue per shape

    # 18. Uniform-at-floor signature — the floor was written as a default.
    #     Collect every body-role run (same _role_floor classification as #10);
    #     if >50% sit within 1pt of the 22pt floor (i.e. 22.0–22.9pt) the sizes
    #     were never computed. Guards: needs >=8 body runs deck-wide (no
    #     statistical basis on tiny decks), and "within 1pt" so nudging a few
    #     runs to 23pt cannot game the test. Severity is context-split:
    #       - Generation (conversion_source=None): ERROR. The generator owns the
    #         sizes; compute-then-clamp via fit_font_size() before saving. The
    #         failure message says compute or reduce content — never inflate
    #         fonts just to clear the check.
    #       - Conversion (conversion_source set): WARNING. The PPTX inherits a
    #         uniformly small Beamer source; the fix is upstream in slides.tex,
    #         so surface it and point there.
    body_run_sizes = []
    for si11, slide11 in enumerate(prs.slides, start=1):
        if slide11._element.get('show') == '0':
            continue
        for s in slide11.shapes:
            if s.is_placeholder or s.has_chart or s.has_table:
                continue
            if s.shape_type == 13 or not s.has_text_frame or s.left is None:
                continue
            role, _fl = _role_floor(s.left/IN, s.top/IN, s.width/IN, s.height/IN)
            if role != 'body':
                continue
            for p in s.text_frame.paragraphs:
                for run in p.runs:
                    if run.font.size is not None and run.text.strip():
                        body_run_sizes.append(run.font.size.pt)
    if len(body_run_sizes) >= 8:
        at_floor = sum(1 for sz in body_run_sizes if 22.0 <= sz < 23.0)
        if at_floor / len(body_run_sizes) > 0.5:
            msg = (
                f"UNIFORM-AT-FLOOR: {at_floor} of {len(body_run_sizes)} body runs sit at "
                f"the 22pt floor — the floor was written as a default, not a clamp on a "
                f"computed size. "
            )
            if conversion_source:
                issues.append(
                    f"WARNING: {msg}This deck is a conversion; the source "
                    f"({conversion_source}) is uniformly small and the PPTX cannot "
                    f"manufacture hierarchy the source lacks. Fix upstream in the "
                    f"Beamer source (slides.tex), and report this to the user — "
                    f"do not silently inflate fonts."
                )
            else:
                issues.append(
                    f"{msg}Compute each box's size with fit_font_size() (start at the "
                    f"role ceiling, step down to fit, clamp at floor) or reduce content "
                    f"so a larger size fits. Do not inflate fonts without checking fit."
                )

    # 19. Box under-fill — the inverse of overflow check #14: text rattling
    #     around a much larger box at a size below the role ceiling means the
    #     size was never computed upward. WARNING (a deliberately airy stat
    #     callout can legitimately sit under 60%), surfaced for a decision.
    for si12, slide12 in enumerate(prs.slides, start=1):
        if slide12._element.get('show') == '0':
            continue
        lbl12 = f"Slide {si12}"
        for s in slide12.shapes:
            if s.is_placeholder or s.has_chart or s.has_table:
                continue
            if s.shape_type == 13 or not s.has_text_frame or s.left is None:
                continue
            shape_w, shape_h = s.width/IN, s.height/IN
            if shape_h < 0.6:
                continue   # labels/citations/slivers — not under-fill candidates
            role, _fl = _role_floor(s.left/IN, s.top/IN, shape_w, shape_h)
            if role != 'body':
                continue
            sizes = [r.font.size.pt for p in s.text_frame.paragraphs
                     for r in p.runs if r.font.size is not None and r.text.strip()]
            texts = [p.text for p in s.text_frame.paragraphs if p.text.strip()]
            if not sizes or not texts:
                continue
            cur = max(sizes)
            if cur >= 28:
                continue   # already at the body ceiling
            def _est_h(t, w_in, pt):   # self-contained, mirrors estimate_text_height
                cpl = max(1, w_in * 72 / (pt * 0.55))
                return math.ceil(len(t) / cpl) * pt * 1.4 / 72
            est = sum(_est_h(t, shape_w, cur) for t in texts)
            if est < shape_h * 0.6:
                bigger = sum(_est_h(t, shape_w, cur + 2) for t in texts)
                if bigger <= shape_h * 0.92:
                    issues.append(
                        f"WARNING: {lbl12} '{s.name}': box under-fill — ~{est:.1f}\" of text "
                        f"in a {shape_h:.1f}\" box at {cur:.0f}pt, and {cur+2:.0f}pt would "
                        f"still fit. Compute the size with fit_font_size() (largest in-role "
                        f"size that fits), or shrink the box to its content."
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
- **Table style**: call `fix_table_style(table_shape)` to set the canonical safe GUID `{2D5ABB26-0587-4C30-8999-92F81FD0307C}` ("No Style, No Grid"). Never use the null GUID `{00000000-...}`; it crashes LibreOffice 26 on PPTX import.
- **Table fonts**: call `fix_table_fonts(table_shape)` after populating the table
- **Text box fonts**: recompute the run's size with `fit_font_size()` toward the role's target (24-28pt for body) and clamp at the role floor (body 22pt); if text does not fit, reduce content or split the slide rather than reducing font size
- **Conversion coverage**: reclassify image-only slides as hybrid (text column native + image column embedded), native shapes (colored boxes, flowcharts, box-and-arrow diagrams), or native charts (bar/line/scatter) per Step 2 decision rules
- **Chart number format**: set `chart.value_axis.tick_labels.number_format` to the appropriate format string and set `number_format_is_linked = False`; cross-reference the source for data units
- **Hanging indent**: call `set_hanging_indent(paragraph)` on every bullet paragraph to set proper `marL` and negative `indent`
- **Below-target font (WARNING)**: try setting to `Pt(24)` first; if content overflows, reduce content (fewer bullets, shorter text, split slide); only drop to `Pt(22)` or `Pt(20)` after content is already minimal
- **Text overflow**: reduce text content (shorten descriptions, remove items), increase box height (fewer items per slide = taller boxes), or change layout (switch from grid to bulleted list or table). Never ignore overflow; the rendered PPTX will clip or overlap
- **Off-spec gray**: change the run's color to `RGBColor(0x4D, 0x4D, 0x4D)` (Charcoal). The check only fires on gray-toned colors (R≈G≈B) that are not in the approved palette grays, so near-Charcoal values like `#3A3A3A`, `#555555`, or `#333333` will be flagged. Colored accent runs (SlateNavy, DeepTeal, DustyPlum, etc.) are not affected
- **UNIFORM-AT-FLOOR (generation)**: the floor was written as a default. Recompute every body box's size with `fit_font_size()` (start at the role ceiling, step down to fit, clamp at floor); where content is genuinely too dense for anything above the floor, reduce content. Never bump sizes without re-checking fit
- **UNIFORM-AT-FLOOR (conversion warning)**: the Beamer source is uniformly small; report it to the user with the pointer to `slides.tex`. Do not silently inflate PPTX fonts to clear the warning
- **Box under-fill (WARNING)**: compute the size with `fit_font_size()` and re-set the runs, or shrink the box to its content; a deliberately airy layout (hero stat, spacious card) can be accepted explicitly
- **`<p:style>` conflict (PowerPoint repair warning)**: after `add_shape()`, find and remove the auto-added `<p:style>` element when you also set explicit `srgb` fill or line on the shape's `spPr`. `add_rounded_card()` does this automatically; if you wrote a custom autoshape helper, copy the `sp_el.find(qn('p:style'))` cleanup pattern from there
- **`<a:buChar>` missing typeface (PowerPoint repair warning)**: use `set_bullet()`, which always emits a paired `<a:buFont typeface="Arial"/>` immediately before `<a:buChar/>`. Never write a custom bullet helper that only sets `<a:buChar>`

## Implementation Checklist

When generating slides, verify:

**Layout:**
- [ ] Title in placeholder, 36pt Calibri Bold, #4D4D4D (Charcoal); title is the key message
- [ ] No subtitle added; no title slide generated
- [ ] Callout boxes present in the Beamer source (`\callout`) are recreated as editable filled text boxes (`add_rounded_card()` + a white text run), matching the source fill and white text, never rasterized; do not add callouts the source does not have
- [ ] Content starts at `CONTENT_TOP = 1.95"`, never above the title bottom (1.826")
- [ ] All shapes start at `CONTENT_LEFT = 1.10"` or further right
- [ ] All shapes fill `CONTENT_W = 13.80"`; no narrower layouts that leave gaps on the right
- [ ] Body content stays above `CONTENT_BOTTOM = 8.00"`. Citation band is T=8.00 to 8.25. Footer placeholder begins at T=8.38.

**Typography:**
- [ ] Every text element sized per the Role-Based Font Hierarchy: compute with `fit_font_size()`, then clamp at the role floor; never write a floor value as a default
- [ ] Body text at the 24-28pt target, 22pt floor (body secondary floor 20pt); reduce content rather than dropping below a floor
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
- [ ] Citation text boxes are at canonical position: `L=1.10", T=8.00", W=13.80", H=0.25"` (single-line)
- [ ] Multi-line citations grow upward only: `T=7.75, H=0.50` for 2 lines; `T=7.50, H=0.75` for 3 lines. Bottom edge always at `T+H=8.25`, never inside the footer strip (which begins at `T=8.38`).
- [ ] Citation formatting: 11pt Calibri **non-italic**, #B0AFA8, right-aligned
- [ ] Multi-source citations use `; ` (semicolon space) between sources

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

## Rendering for Review

When producing a review PDF of a saved PPTX (to inspect rendered slides, audit visually, or share for feedback), use **LibreOffice headless** as the export engine. PowerPoint is the documented fallback when LibreOffice misrenders. Never use Keynote.

**Why LibreOffice over PowerPoint:** PowerPoint on macOS is sandboxed and cannot read files in `/private/tmp/...` or other restricted paths without a per-file "Grant File Access" prompt that the user must dismiss every time. LibreOffice runs headless with no GUI and no permission prompts. LibreOffice respects coded dimensions when Critical Rule 6 (`auto_size = MSO_AUTO_SIZE.NONE`) is applied, the same condition under which PowerPoint respects them.

**Why not Keynote:** Keynote's PDF export applies its own auto-size to text frames on open, which silently resizes shapes that were coded with explicit dimensions. This produces cards with misaligned bottoms, overgrown callouts, and label positions that do not match the coded coordinates, even when the PPTX itself is correct.

**Canonical render path:**

```bash
soffice --headless --convert-to pdf "/absolute/path/to/deck.pptx" --outdir "/absolute/path/to/outdir/"
```

The output PDF lands at `/absolute/path/to/outdir/deck.pdf`. The command exits cleanly when the conversion completes; no application window opens.

Then render PNGs from the PDF with `pdftoppm -png -r 120 deck.pdf deck-slide`. The `-png` flag is required; without it, `pdftoppm` defaults to uncompressed PPM (about 6 MB per slide vs about 200 KB for PNG, and Claude's Read tool does not support PPM). At `-r 150` a standard 16:9 slide renders at 2000x1125, right at the 2000px per-image cap; slightly larger page sizes push PNGs to ~2080x1170 and trigger "image exceeds dimension limit" errors when read into context. `-r 120` yields 1600x900 (or ~1664x936 for wider pages), safely under the cap while remaining sharp enough for visual layout audits.

**PowerPoint fallback.** If a LibreOffice export shows visual defects that the code says should not be there (rare; usually involves obscure chart features or font-substitution surprises), re-export via PowerPoint:

```bash
osascript -e 'tell application "Microsoft PowerPoint"
    open POSIX file "/absolute/path/to/deck.pptx"
    set theDoc to active presentation
    save theDoc in POSIX file "/absolute/path/to/deck.pdf" as save as PDF
    close theDoc saving no
end tell'
```

PowerPoint cannot read `/private/tmp/...` without a permission prompt; copy the deck into the project folder (or `~/Library/Caches/`) before running the AppleScript fallback.

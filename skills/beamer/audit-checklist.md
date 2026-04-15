# Beamer Quality Audit Checklist

Read this file before performing the Step 3 quality audit in `SKILL.md`. Check every slide against every applicable item. The `.tex` source is required alongside the compiled PDF because visual inspection alone at PDF resolution is insufficient to catch tight spacing between positioned elements.

---

## Methodology Rules

These govern how findings are classified and reported:

1. **No soft language for defects.** "Tight against," "slightly beyond," "close to," or "nearly overlapping" means **fix required**, not minor or acceptable. These are overlaps, not near-misses.
2. **Every slide, individually.** Do not group similar slides and spot-check one representative. Each slide has different content, different density, and different TikZ coordinates.
3. **Coordinate arithmetic is mandatory for TikZ.** Compute bounding box positions from `.tex` source coordinates. PDF rendering resolution is insufficient to distinguish a 2mm overlap from a 2mm gap.
4. **Verify semantic accuracy of annotations.** For every annotation referencing chart/diagram elements, verify the coordinate span matches the positions of the referenced elements.

---

## Graphics: Off-Page and Incomplete

1. TikZ nodes, labels, arrows, or chart elements extending beyond the visible slide area or clipped by the frame boundary.
2. Charts missing axes, labels, legends, or data points; TikZ diagrams with unconnected nodes or missing arrows.

## Graphics: Bar Charts

1. Bars not centered over x-axis labels (shifted left or right), missing bar labels, overlapping bars, inconsistently sized bars, bars extending beyond the plot area, missing or misaligned value annotations.
2. **Per-bar coloring:** if multiple `\addplot` commands give each bar a different color (one visible bar per category), verify every `\addplot` includes `bar shift=0pt`. Do NOT use `ybar=0pt` on the axis (it sets gap to zero but does not disable per-series positional offset).
3. **Narrow grouped bars:** for grouped bar charts (2+ series) at narrow widths (under 8cm), verify `bar width` is small enough that adjacent bar groups do not overlap. Reduce to 8-10pt for 2-series charts at 5.5cm width.
4. **X-tick label containment:** estimate the rendered width of each `xticklabel` at the specified font size. If any label's estimated width exceeds 90% of the available inter-tick space, flag for rotation (`rotate=25, anchor=north east`) or abbreviation. Three or more multi-character labels on a chart under 6cm wide almost always require rotation.
5. **Narrow stacked bar segments:** for stacked bar charts, check each segment's rendered width. If any segment is less than 1.5cm wide, labels must be placed outside the segment (above, below, or beside with a leader line), not inside it. Text inside narrow segments will overflow or hyphenate.

## Graphics: Bar Chart Axis Containment

1. Verify `axis lines=left` with `axis on top` (clean L-shaped axes, no box border). Never use default box axes.
2. Verify the chart does NOT use `clip=false`.
3. Verify the chart does NOT use `symbolic x coords` (must use numerical coordinates with `xticklabels`).
4. Verify explicit `xmin`/`xmax` are set with at least 0.7 padding beyond outermost bar positions (do not rely on `enlarge x limits`).
5. For grouped bar charts, verify `bar width` is proportional to the number of series.
6. If `nodes near coords` is used, verify `ymax`/`ymin` provide at least 15-20% headroom beyond the tallest/deepest bar so labels are not clipped.
7. Verify `nodes near coords style` includes `/pgf/number format/fixed` to prevent scientific notation.
8. For all-positive data, verify `ymin=0`.
9. For mixed positive/negative data, verify a zero baseline line exists (`extra y ticks={0}`).
10. Verify no `grid=major` on bar charts (only the zero baseline `extra y tick` grid is permitted).
11. **Visual verification:** all bars contained within plot area, only left and bottom axis lines visible, all bars uniform thickness, x-axis lines extend beyond outermost bars on both sides, `nodes near coords` labels on short bars do not collide with y-axis tick labels.

## Graphics: TikZ Element Clearance

Perform coordinate arithmetic on the `.tex` source. For each pair of adjacent elements, compute the bounding box from `(x +/- minimum width/2, y +/- minimum height/2 +/- inner sep)` and verify no intersection.

1. No text node overlaps another text node.
2. No arrow path crosses through a text node.
3. Every label has at least 3pt visible whitespace from adjacent elements.
4. Every container node is large enough for its text.
5. **Consistent sizing:** boxes in a uniform diagram must have equal `minimum width` and `minimum height` unless intentionally varied.
6. **Vertical and horizontal alignment:** stacked nodes share the same x-coordinate; side-by-side nodes share the same y-coordinate.
7. **Even spacing:** gaps between adjacent nodes in a sequence must be consistent.
8. **Arrow endpoint accuracy:** for every arrow connecting to a node, verify endpoint coordinates match the target node's position. Any gap > 2mm is a defect.
9. **Annotation labels:** side annotations must be at least `\scriptsize`, not `\tiny`.
10. **No masking overlaps with fill:** a text node with `fill=white` placed over arrows or lines is not a valid fix. It hides the conflict. Place the label outside the diagram instead. Flag any node whose `fill` covers non-text elements.
11. **Connector-node conflict resolution:** when an arrow path crosses through an unrelated filled node, this is a layout conflict. Do NOT fix by placing the arrow on a background layer. Reposition the source or destination so the path passes through clear space.

## Graphics: Dual-Label Collision

1. If `nodes near coords` is used, verify no manual annotation nodes (`\node`) are placed at the same position above bars. Having both `nodes near coords` (value labels) AND separate `\node` annotations (for example, percentage labels) above the same bars creates collisions. Choose one labeling system per bar.
2. If both value and percentage labels are needed, use `nodes near coords` for the primary value and place secondary labels (percentages) as a parenthetical suffix in the `nodes near coords` format string, or place them below/inside the bars instead of above.

## Graphics: Chart Legends

1. Verify the legend does not overlap any data series, data labels, bars, or annotation text.
2. **Fallback hierarchy by chart width:** (a) Full-width (> 8cm): `at={(1.03,0.5)},anchor=west` (right of chart, style guide default). (b) Narrow column (4-8cm): `at={(0.5,-0.22)},anchor=north` (below chart, enough offset to clear x-axis labels). (c) Very narrow (< 4cm): place in the opposite column or as separate text outside the axis environment. The style guide default causes overfull hbox in narrow columns; do not force it.
3. A legend inside the plot area is a violation even if it does not currently overlap data (it will if bar heights change).
4. **Stacked chart legend order:** for `ybar stacked` charts, verify `reverse legend` is present so the legend reads top-to-bottom matching the visual stack. Do not use `reverse legend` for non-stacked charts.
5. **After repositioning any legend, visually verify that specific slide before proceeding to the next fix.** Legend repositioning is the most common fix-creates-new-problem pattern. Do not batch-verify.

## Graphics: Axis Baseline Validation

1. For charts showing proportions, fractions, percentages, or cumulative values: verify `ymin=0`. A non-zero baseline exaggerates differences.
2. For charts showing growth rates, changes, or residuals: verify the baseline is appropriate for the data range.

## Graphics: Annotation-Data Alignment

1. For every annotation (brace, arrow, bracket, label) referencing a subset of chart/diagram elements, verify the coordinate span matches exactly the referenced elements.
2. Use `axis cs:` coordinates inside pgfplots axis environments, not hardcoded canvas coordinates.
3. For reference lines with labels (for example, "1x breakeven"), verify the label does not collide with `nodes near coords` at nearby positions.

## TikZ: Diagram Sizing

1. Text labels below approximately 7pt after scaling: too small.
2. Nodes too narrow for their text: too cramped.
3. Diagram with 5+ labeled elements in a column at `0.45\textwidth` or less: flag as cramped.
4. **No `scale=` on complex tikzpictures:** verify the `tikzpicture` environment does not use a `scale` option. `scale` shrinks coordinates but not text, producing text overflow and misaligned arrow endpoints. If the diagram is too large, reduce internal dimensions instead.
5. **No parameterized styles inside frames:** verify all `\tikzset` definitions containing `#` are in the preamble, not inside `\begin{frame}...\end{frame}`. Beamer consumes `#` as a frame argument delimiter before TikZ processes it, producing "Illegal parameter number" errors.

## TikZ: Sibling Node Uniformity

1. All nodes in a visual group must specify explicit `minimum width` and `minimum height`.
2. If any sibling uses `minimum width` instead of `text width`, flag it: `text width` is required for uniform rendered width.
3. If siblings have different line counts, verify `minimum height` accommodates the tallest content.
4. Tables with `\arraystretch` are preferred over TikZ boxes when uniform row heights are needed.

## TikZ: Box Text Anchoring

1. All multi-line TikZ content boxes must use `anchor=north` with `align=left` and `inner sep` of at least 6pt.
2. The only exception is single-line label nodes where centering is appropriate.
3. **`minimum height` trap:** when `minimum height` exceeds natural text height, TikZ vertically centers the text regardless of `anchor=north`. Fix: draw the box as an empty node, then place text with a separate `\node[anchor=north west]` shifted inside.

## TikZ: Font Consistency

1. All sibling nodes in the same visual group must use the same font size and weight.
2. Exception: intentional hierarchy (header node above body node, connected by an arrow).

## Sourcecite and Footer Zone

1. **Citation zone intrusion:** on every slide with `\sourcecite`, verify NO body content extends into the bottom 12mm. Two-column slides with charts are highest risk. If content intrudes, shorten the text, not move the citation. This is a content density problem.
2. **Sourcecite position:** verify the citation appears at the bottom-right, approximately 10mm from page bottom. If displaced upward, the deck needs a second `pdflatex` pass. The fix is always to recompile, not adjust the macro.
3. **Footer zone encroachment:** check every slide individually (no spot-checking). Content must not extend below the bottom 8mm.
4. **Sourcecite clearance:** verify no TikZ content or frame text extends into the sourcecite overlay zone. In a center-anchored tikzpicture, content below approximately `y = -2.0` will collide. For text-heavy slides (multi-column layouts with 4+ bullets), preemptively estimate content height. Overlay nodes do not participate in frame layout.

## Callout/Citation Confusion

1. Search `.tex` for all instances of `\scriptsize\color{MedGray}` outside `\sourcecite{}`. Any match is a defect.
2. Fix: facilitator notes and content framing use `\footnotesize\color{CharText}`; table footnotes use `\scriptsize\color{CharText}`.

## Hyphenation

1. **Frametitles:** verify no word in any `\frametitle{}` is hyphenated across lines. If the title wraps, reword it to break at a natural point. LaTeX's auto-hyphenation produces ugly breaks in headings.
2. **Table columns:** in narrow `p{...}` columns (under 3cm), verify no words are inappropriately hyphenated. Fix by using `\raggedright` in the column specifier (`>{\raggedright\arraybackslash}p{2.2cm}`) or by rewording cell content.
3. **TikZ text nodes:** verify text inside narrow TikZ nodes (`text width` under 3cm) does not hyphenate. Fix by abbreviating text or widening the node.

## TikZ: Diagram Centering and Spacing

1. **Parent-child alignment:** when a single element (box, brace, label) spans two or more child elements below it, verify the parent is horizontally centered over the children. Compute: parent x should equal `(leftmost child x + rightmost child x) / 2`.
2. **Brace placement:** decorative braces (`decorate,decoration={brace,...}`) must span below or above the elements they annotate, not overlap them. Verify the brace endpoints are offset by at least 3pt from the element edges.
3. **Spacing between sibling nodes:** adjacent boxes at the same hierarchical level should have at least 8pt gap between them. Compute gap from node edges, not centers.

## Content Quality

1. **Slide density:** flag any slide where content occupies less than approximately 60% of the available area between title and footer zones.
2. **Content-mechanism match:** verify every TikZ diagram contains at least one element that cannot be a list item or table cell (arrow, spatial position, data axis, geometric relationship). Flag labeled boxes without spatial relationships.
3. **Overlapping content:** text overlapping text, figures, or tables; chart labels colliding; captions too close to axis labels or diagram elements; reference line labels colliding with `nodes near coords`.
4. **Bad hyphenation / line breaks:** ugly word breaks in titles or bullets, orphaned words, awkward paragraph breaks. See also the Hyphenation section above for specific checks.
5. **Numerical accuracy:** values must match source material; years must not have comma separators (2024 not 2,024).
6. **Text readability:** text too small, poor contrast, text running into margins.
7. **Layout problems:** unbalanced columns, excessive whitespace in one area with crowding in another, misaligned elements.
8. **Title quality:** titles that are generic ("Results") instead of conveying the key point; titles longer than two lines.
9. **Vertical spacing between sections:** at least 6pt (`\vskip6pt`) between a `columns` environment and text below it, between a chart and text below, or between last bullet and a facilitator note.
10. **Text overflow from TikZ boxes (source-level computation, not visual inspection):** For every slide using the empty-box-plus-overlay pattern or any TikZ node with `minimum height`:
    - **Horizontal:** verify `text width` = `minimum width - 2*(inner sep)`. If `text width` is close to or exceeds `minimum width`, text will overflow horizontally.
    - **Vertical (mandatory computation):** extract the box `minimum height` and the overlay content from the `.tex` source. Compute content height: count header lines, bullet items, and lines per item (check each item's character count against `chars_per_line = (text_width - indent) / avg_char_width`; items exceeding chars_per_line wrap to 2+ lines). Multiply total lines by line height (approximately 3.5mm for `\footnotesize`, approximately 3.0mm for `\scriptsize`), add spacing (header approximately 3.5mm, gap approximately 1.4mm, itemsep approximately 0.7mm between items, minipage overhead approximately 2mm). Verify `total_content_height < minimum_height - top_shift`. Flag any case where it does not fit, with the specific measurements.
    - **Do not rely on PDF visual inspection.** At page-level rendering resolution, 2-3mm of vertical overflow is invisible. The computation must be done from the `.tex` source.

## Deck-Level Checks

1. **Citation strategy:** if >80% of content slides cite the same source, replace per-slide `\sourcecite{}` with a single "Based on [Author. Year. Title.]" line on the title slide. Do not retain per-slide citations with rationale about "academic deck" or "classroom use"; repeated identical citations add visual noise without informational value. Slides citing a different source retain their own `\sourcecite{}`.
2. **Cross-deck terminology:** if multiple related decks are built from the same source, verify shared labels and terminology match across decks.

## Narrative Arc

1. **Section-level arc check:** within each thematic section of the deck, verify the slide sequence moves from narrative/application toward technical/framework. The expected progression is: Narrative (story, concrete scene), then Application (specific example), then Visual (chart, diagram), then Technical (equation, formal framework). If a technical slide appears before its motivating example or application, flag for reordering.
2. **Opening check:** the first content slide after the title must be a hook (surprising finding, paradox, concrete problem), not a definition, agenda, or literature review.
3. **Closing check:** the final slide must be a memorable takeaway or actionable statement, not "Questions?" or "Thank you."
4. **Devil's Advocate placement:** if a limitations/critique slide exists, verify it appears in Act III (near the end), after the main findings but before the closing.

## Bezier Curve Clearance

1. For every arrow with `bend left=N` or `bend right=N`, compute the curve's maximum depth:
   ```
   max_depth = (chord_length / 2) * tan(N_degrees / 2)
   safe_zone = max_depth + 0.5cm
   ```
2. Quick reference for common bend angles:

   | Bend angle | tan(angle/2) | Multiplier for half-chord |
   |---|---|---|
   | 20 | 0.176 | 0.18 |
   | 25 | 0.222 | 0.22 |
   | 30 | 0.268 | 0.27 |
   | 35 | 0.315 | 0.32 |
   | 40 | 0.364 | 0.36 |
   | 45 | 0.414 | 0.41 |

3. Verify every label within the safe_zone of the curve baseline (in the direction the curve bends) is moved outside the zone.
4. Verify the curve does not cross any other arrow in the same figure. Curves bending downward cross vertical arrows; fix by reversing the bend direction.

## Code Block Audit

1. Every `lstlisting` environment must use a language specifier (`language=Python`, `language=bash`, `language=R`).
2. Code blocks must be under 12 lines. If longer, flag for splitting or skeleton extraction.
3. Font size must be at least `\footnotesize` (the default). `\scriptsize` is permitted only for dense reference code, never for instructional code.
4. Verify `listings` colors match the palette: keywords in DeepTeal, comments in MedGray, strings in CyanBlue, background in LightGray.
5. If a code block appears on a slide, verify a corresponding runnable script exists in `scripts/` (or note that one should be created).

## Style Guide Compliance

Cross-reference against `../../style-guides/beamer/style-guide.md`:

1. Every color must be from the defined palette (check hex values).
2. Slide background must be white except title/closing slides (SlateNavy).
3. No footer content (slide numbers, author, date, navigation symbols).
4. Frametitle must be CharText (#3A3A3A) and bold (not SlateNavy, not black).
5. pgfplots axes must include `1000 sep={}` on any axis displaying years.
6. `[shrink=N]` must not be used on any frame (displaces TikZ overlay nodes including `\sourcecite`).
7. No `\emphbox` or callout boxes; no `\highlight{}` inside `itemize`, `enumerate`, or running text (reserved for standalone TikZ diagram labels; use `\textbf{\color{DeepTeal}...}` for inline emphasis).
8. Source citations must use `\sourcecite{}` with Chicago Author-Date (Author, Year, Title in `\textit{}`, Publication). No ad-hoc "Source: X" text, no custom footer macros, no manual `\vfill` constructions.
9. `\sourcecite{}` must use `[remember picture,overlay]` with `yshift=10mm`, `anchor=south east`, `align=right`, `text width=\dimexpr\paperwidth-36pt\relax`. Do NOT use `\RaggedLeft` or `\raggedleft` inside TikZ nodes.
10. No visible insertion notes or `\insertnote` on slides; notes use `\note{}` only.
11. The preamble must match `../../style-guides/beamer/style-guide.md` Quick Reference exactly (colors, theme, fonts, templates, macros, `\setbeamersize`, footer `\vskip8mm`).

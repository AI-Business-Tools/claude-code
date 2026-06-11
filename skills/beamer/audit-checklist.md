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
3. **In-axis annotation trimmed by the pgfplots clip path.** Distinct from #1 (frame-boundary clipping): pgfplots clips everything drawn inside an `axis` environment to the axis rectangle (`clip=true` is the default and is required by the bar-chart containment rules), so a `\node` or label placed at an `(axis cs:...)` coordinate near a limit, with its text growing toward that limit, is silently trimmed at the data edge. There is no overfull/underfull box, no compile warning, and no error: the failure is silent, which is why a compile-log scan and a thumbnail glance both miss it. Highest-risk pattern: an annotation anchored `south` / `south east` / `south west` at a `y` within roughly one node-height of `ymax` (text grows up into the ceiling); the symmetric cases are `north*` near `ymin` and `*east` / `*west` near `xmax` / `xmin`. Magnitude check: a `\scriptsize` node is about 9-10pt tall, which on a 4.8cm axis spanning about 270 data units is about 18-20 units, so a `south`-anchored label at `y >= ymax - 20` (at that scale) has its top cut. Source-level test: for every `\node ... at (axis cs:X,Y)` inside an `axis`, read the anchor direction and compare `Y` (or `X`) against the axis `ymax`/`ymin` (`xmax`/`xmin`); flag any node whose text grows toward a limit it sits within about one node-dimension of. Fix order: (a) flip the anchor so the text grows away from the limit into open plot space (for example, `south east` to `north east`, hanging the label down from its own point); (b) move the anchor coordinate inward; (c) last resort, raise `ymax` or widen the limit for headroom (it rescales the plot, so prefer (a)). Never use `clip=false` to escape the trim: it lets the label spill outside the axis frame, trading an in-axis trim for an off-axis overlap, and it is prohibited by the bar-chart containment rules. **Audit-time confirmation is mandatory and visual:** render the slide to PNG at 150 DPI or higher (`pdftoppm -r 150 -png -f <N> -l <N> slides.pdf out`) and inspect the top or edge of the annotation; because the defect emits no warning and is invisible in the source, the render is the only reliable check.

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

## Graphics: `\addlegendentry` Math Tokens

Pre-compile source check, cheap and catches a fatal pgfplots/beamer corruption that is mis-attributed to the wrong frame.

1. **No raw math delimiters inside `\addlegendentry`:** grep the `.tex` source for `\addlegendentry{[^}]*\$`. Flag every match. Inside `\addlegendentry{...}`, math symbols must be wrapped with `\ensuremath{token}`, never with `$token$`. Math-mode dollars inside legend labels corrupt pgfplots state when the legend has 2+ entries and another frame follows, producing a fatal `Missing control sequence inserted / \inaccessible` error attributed to the wrong frame's `\end{frame}` (off-by-one). Fix by replacing every `$math$` inside `\addlegendentry` with `\ensuremath{math}`.

## Graphics: Horizontal Bar Chart Axis Containment

For every `xbar` (horizontal bar) chart, apply these checks in addition to the vertical-bar containment rules above where they apply (axis lines=left, no `clip=false`, no `symbolic x coords`).

1. **Explicit `ymin`/`ymax` with padding (required):** verify the chart sets explicit `ymin` and `ymax` with at least 0.5 padding beyond the outermost bar y-positions. For N categories at y={0,…,N-1}, the minimum is `ymin=-0.5, ymax=N-0.5`. Or `enlarge y limits=0.18` or larger. Without padding, the top and bottom bars are clipped at the plot-area edges. This is the y-axis analog of the `xmin`/`xmax` padding rule for vertical bars.
2. **Headroom for value labels via `nodes near coords`:** verify `xmax` provides at least 15-20% horizontal headroom beyond the longest bar so labels do not clip at the right edge.
3. **Visual verification:** every bar's full thickness is visible with at least 3pt of clearance from the top and bottom plot-area boundaries; y-axis tick labels align vertically with their corresponding bars.

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
12. **Arrow endpoint face vs vertex.** Grep `slides.tex` for arrow-drawing commands whose endpoint anchors at a node corner: pattern `\\draw\[[^\]]*Stealth[^\]]*\][^;]*--\s*\([^)]*\.(north|south)\s*(west|east)\)` (also catch the abbreviated forms `.nw`, `.ne`, `.sw`, `.se`). Every match is a candidate defect: an arrow terminating at a node's corner reads as "stuck on the edge" rather than entering the box through a face, because the Stealth arrowhead lands on a vertex. Fix by anchoring the endpoint on the appropriate face: use `(target.north)`, `(target.south)`, `(target.east)`, or `(target.west)`; or, when the source is offset horizontally and you want the arrow to land on the face directly below or above it, use TikZ's perpendicular coordinate combiner: `(target.north -| source.south)` takes y from `target.north` and x from `source.south`, placing the endpoint on `target`'s top edge directly below the source. Corner anchors remain legitimate for annotation labels (`\node at (target.north east)`) and for braces; the rule is scoped to arrow termination only, which is why the grep matches the `\draw[...Stealth...]` form. Two-or-fewer matches per deck is typical; if a corner anchor on an arrow endpoint is intentional, leave a one-line `% intentional corner anchor:` comment explaining why.
13. **Freeform path vs node clearance.** The bounding-box arithmetic above covers node-to-node overlap only; a hand-drawn curve or line has no `minimum width` or `minimum height` for those rules to test, so curve-into-box collisions fall through. For every tikzpicture that contains BOTH a freeform path (`\draw ... .. controls ... ..` Bezier, or `\draw ... -- ...` polyline, including pgfplots-free schematic diagrams) AND one or more `\node` boxes, identify the path's extreme coordinate in the direction of the nearest node (max y when boxes sit above the path, min y when below, and so on) and verify at least 0.3 cm clearance between that extreme and the nearest node edge. Compute the path extreme from the control points: a cubic Bezier stays within the bounding box of its four control points, so the largest control-point y is a safe upper bound for "how high the curve reaches." A curve whose peak control point is within 0.3 cm of a box edge is a defect even if the rendered curve appears to stop short, because PDF-resolution inspection cannot distinguish a 2 mm gap from a touch. Fix by lowering the path, raising the boxes, or both, so the gap holds for the worst-case point. This is the rule that a "curve touches the box" defect (a hand-drawn schematic curve running into a labeled phase box) would trigger.

## Graphics: Dual-Label Collision

1. If `nodes near coords` is used, verify no manual annotation nodes (`\node`) are placed at the same position above bars. Having both `nodes near coords` (value labels) AND separate `\node` annotations (for example, percentage labels) above the same bars creates collisions. Choose one labeling system per bar.
2. If both value and percentage labels are needed, use `nodes near coords` for the primary value and place secondary labels (percentages) as a parenthetical suffix in the `nodes near coords` format string, or place them below/inside the bars instead of above.

## Graphics: Chart Legends

1. Verify the legend does not overlap any data series, data labels, bars, or annotation text.
2. **Fallback hierarchy by chart width:** (a) Full-width (> 8cm): `at={(1.03,0.5)},anchor=west` (right of chart, style guide default). (b) Narrow column (4-8cm): `at={(0.5,-0.22)},anchor=north` (below chart, enough offset to clear x-axis labels). (c) Very narrow (< 4cm): place in the opposite column or as separate text outside the axis environment. The style guide default causes overfull hbox in narrow columns; do not force it.
3. A legend inside the plot area is a violation even if it does not currently overlap data (it will if bar heights change).
4. **Stacked chart legend order:** for `ybar stacked` charts, verify `reverse legend` is present so the legend reads top-to-bottom matching the visual stack. Do not use `reverse legend` for non-stacked charts.
5. **After repositioning any legend, visually verify that specific slide before proceeding to the next fix.** Legend repositioning is the most common fix-creates-new-problem pattern. Do not batch-verify.
6. **Legend-xlabel clearance.** For every pgfplots chart that has both an `xlabel` defined and a legend placed below the axis (`legend style={at={(*,-y)},anchor=north,...}` form with negative y), verify y is at least `0.32` when the chart `height` is in the 4-5 cm range, and at least `0.28` when the chart `height` is in the 5-6 cm range. Smaller y values place the legend in the same vertical band as the rendered xlabel (axis line, then tick labels, then xlabel, then legend), producing visible overlap. Grep `slides.tex` for `legend style={at={(0\.5,-0\.[0-2]` (matches y values between 0.00 and 0.29). For every match, locate the enclosing `\begin{axis}[...]` and check whether `xlabel=` is set; if it is, the legend must move down. Apply the fix in one pass across the deck: legend repositions are independent and can be batched, but per rule #5 above, visually verify each affected slide after recompile.

## Graphics: Axis Baseline Validation

1. **Zero-baseline default (all-positive y-axis data, all chart types):** verify `ymin=0` on every chart with all-positive y-axis values, regardless of chart type (bar, line, scatter, area). A non-zero baseline makes trends look larger than they are and is a recurring defect. Non-zero baseline is permitted only when (a) the data genuinely fills a tight band such that zero-basing produces 80%+ whitespace, AND (b) the slide carries a visible "scale starts at N" note near the axis or in a caption. Verify the note is rendered at `\scriptsize` in `CharText`, placed in the caption or near the axis origin, not inside the plot area. Flag any non-zero baseline that lacks the scale note or renders it at a smaller size or inside the plot area.
2. **No exception for proportions, fractions, or percentages:** these axes use `ymin=0` (and typically `ymax=100` or `ymax=1`) with no exceptions, no non-zero baseline even with a scale note.
3. For charts showing growth rates, changes, or residuals: verify the baseline is appropriate for the data range.
4. The zero-baseline rule applies to y-axes only (this is a vertical-scale convention). X-axis baselines on horizontal bar charts are not bound by this rule.

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
5. **Sub-header y-alignment across sibling cards.** For empty-box-plus-overlay sibling card groups whose overlay contains a title plus a subhead (date, subtitle, category tag), verify each labeled region is its own overlay node anchored at a fixed y-offset from the card's north anchor. Grep the `.tex` source for sibling card families and inspect their overlay structure: if title and subhead share one overlay node (packed via `\\[Npt]` or `\\` separators inside a single `\node{...}` body), the subhead in a sibling whose title wraps to a different line count will sit at a different y-position than its peers, producing a visibly misaligned subhead row across the card family. Defect class: visible at PDF resolution; appears even when no content overflows the card. Fix: split title and subhead (and bullets) into separate overlay nodes, each anchored at a fixed y-offset from the card anchor, with the title's y-range sized to the worst-case sibling. See the Sibling-Node Uniformity section of `../../style-guides/beamer/style-guide.md`, "Sub-header alignment in card siblings."

## TikZ: Box Text Anchoring

1. All multi-line TikZ content boxes must use `anchor=north` with `align=left` and `inner sep` of at least 6pt.
2. The only exception is single-line label nodes where centering is appropriate.
3. **`minimum height` trap:** when `minimum height` exceeds natural text height, TikZ vertically centers the text regardless of `anchor=north`. Fix: draw the box as an empty node, then place text with a separate `\node[anchor=north west]` shifted inside.
4. **No manual list typography inside TikZ nodes.** Any list of three or more parallel items inside a TikZ node must use a real `itemize` or `enumerate` environment wrapped in a `minipage` matching the node's text width. This rule applies regardless of how the items are separated in the source:
   - Manual bullet glyphs: `$\bullet$~Item one\\$\bullet$~Item two\\$\bullet$~Item three`
   - Manual line breaks alone: `Item one\\Item two\\Item three`
   - Comma-separated grouped lines: `Vendor A, Vendor B, Vendor C\\Vendor D, Vendor E, Vendor F`

   All three patterns produce no hanging indent on wrapped lines, no consistent inter-item spacing, and no visual list affordance. Fix: replace the manual layout with `\node{\begin{minipage}{Wcm}\setlength{\leftmargini}{1em}\begin{itemize}\setlength{\itemsep}{2pt}\item Item one \item Item two \item Item three\end{itemize}\end{minipage}};`. The minipage gives `itemize` a real list context. Use `\setlength{\leftmargini}{1em}` (native LaTeX) for tighter indent inside narrow cards. **Do not** use `\begin{itemize}[leftmargin=*]` syntax: it requires `\usepackage{enumitem}` in the preamble, and loading `enumitem` silently overrides Beamer's `\setbeamertemplate{itemize items}[circle]` template and strips visible bullet glyphs from every itemize environment in the deck. Two-or-fewer items in a TikZ node may remain as inline prose without `itemize`.
5. **Vertical symmetry of card content.** For every TikZ card built from the empty-box-plus-overlay pattern (a filled box with a header node and a bullet block placed via `[shift={(...,-Npt)}]` from the card's north west), compute the top margin (card top edge to first content baseline) and the bottom margin (last content baseline to card bottom edge) for the **most content-heavy sibling** in the card family. The two margins must differ by no more than 3 mm. Computation: top margin ≈ header-shift + header-text-height + header-to-bullets gap; bottom margin = `minimum height` − top margin − content height (content height = lines × line-height for the active font size, plus `itemsep` × (lines − 1), plus minipage overhead ~2 mm). If the two differ by more than 3 mm, apply one of: (a) reduce the header-to-bullets gap by tightening the bullet block's vertical shift (for example, `-26pt` → `-20pt`), (b) increase the card `minimum_height` to absorb the worst-case content while leaving the lightest sibling enough bottom margin, or (c) anchor the content block to the card center rather than the north edge. Sibling cards inherit the same anchors, so the rule is checked once per card family. Worst-case sibling, not average: if any one card overflows or has a collapsed bottom margin, the rule is violated even if the other cards in the family are balanced.

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

1. **Frametitles:** verify no word in any `\frametitle{}` is hyphenated across lines. If the title wraps, reword it to break at a natural point. LaTeX's auto-hyphenation produces ugly breaks in headings (for example, "Writ-ten", "Assess-ments").
2. **Table columns:** in narrow `p{...}` columns (under 3cm), verify no words are inappropriately hyphenated. Fix by using `\raggedright` in the column specifier (`>{\raggedright\arraybackslash}p{2.2cm}`) or by rewording cell content.
3. **TikZ text nodes:** verify no word in any TikZ node containing body content is hyphenated across lines, regardless of node width. Fix by rephrasing, abbreviating, widening the node, or adding `\hyphenpenalty=10000\exhyphenpenalty=10000` inside the node. Mid-word hyphenation in a 12cm centered box is just as ugly as in a 2cm box; the visual defect does not depend on width.
4. **TikZ hyphenpenalty does not always take effect, so apply fixes in order.** Adding `\hyphenpenalty=10000\exhyphenpenalty=10000` (or `\sloppy`) inside a TikZ `\node{...}` body is NOT a reliable fix in all contexts. When the node's `text width` is too short for the content to flow without breaks, TikZ's line-breaking pass can still split words at hyphenation points despite the penalty assignment. This is observed most often in `\sourcecite{}` overlay nodes (text width near `\paperwidth-36pt`, right-aligned `\scriptsize`), where long multi-source citations joined by `;` still split month names ("Oc-tober", "Decem-ber") or common words ("re-lease") across lines even with the penalty set inside the node body.

   **Fix order (try in this sequence; do not skip ahead):**
   1. **Shorten the text** so it fits on one line, or fits with a clean wrap at a space boundary. This is the most reliable fix and the default. For sourcecites, drop the longest non-essential phrase (interviewer attribution, secondary subtitle, an appositive descriptor).
   2. **Force a clean break at a known-good point** with `\\` (or `\linebreak`). For a multi-source `\sourcecite{}` joined by `;`, insert `\\` after the semicolon so each citation gets its own line: `\sourcecite{... 2025;\\ ... 2026.}`. This is the canonical fix when the text cannot be further shortened.
   3. **Then, and only then, add `\hyphenpenalty=10000\exhyphenpenalty=10000` inside the node** as a belt-and-suspenders measure. Do not rely on it as the sole fix; verify in the rendered PDF that the hyphenation actually disappeared. If it did not, fall back to step 1 or 2.
   4. `\sloppy` inside a TikZ node body does not suppress hyphenation in observed cases. Do not substitute `\sloppy` for the steps above.

   **Audit-time test:** run `pdftotext -layout slides.pdf -` and scan for lines ending in `-` followed by a continuation fragment of the same word on the next line. Every match is a defect. Cross-reference against `slides.tex` to confirm the source did not contain an explicit hyphen at that position. This is the same hyphenation grep specified in this skill's SKILL.md (Compilation Cycle Step 3); this entry documents the fix order to apply when the grep flags a match inside a TikZ node.

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

11. **Prose-vs-bullet match for parallel claims.** In any non-TikZ column or block where the planned content consists of three or more parallel claims, facts, or steps, the rendered form must be `itemize` or `enumerate`, not running prose paragraphs. Source-level test: scan each `\begin{column}` (or each top-level content block outside `tikzpicture`) for sequences of 3+ paragraphs separated by `\vskip6pt` (or any consistent `\vskip` pattern) where each paragraph asserts one claim parallel to the others. Each such block is a defect. Fix: convert to `itemize` with `\textbf{\color{DeepTeal}...}` or `\textbf{\color{SlateNavy}...}` lead-ins on the key facts. Acceptable patterns:
    - A short prose lead-in (1 sentence or less) followed by an `itemize` block.
    - Genuinely narrative content with no parallel structure (story, scenario walkthrough, single sustained argument). Signal: removing any one paragraph breaks the argument's flow. If the paragraphs are independent claims that could be reordered without loss, they should be bullets.

    This rule is the audit-side backstop to the Step 1 Column Content Invariant in `SKILL.md` and the planning-time text-column mechanism inventory in Step 0.7. Primary defense is write-time, this is the safety net.

12. **Bullet rendering visibility (verify in the rendered PDF).** For every slide containing `\begin{itemize}` or `\begin{enumerate}`, verify visible bullet glyphs appear before each `\item` in the rendered PDF. The Beamer style guide preamble specifies `\setbeamertemplate{itemize items}[circle]` with `\setbeamercolor{itemize item}{fg=DeepTeal}`, so itemize bullets should render as DeepTeal-colored circles; enumerate bullets should render as bold Arabic numerals. If bullets are absent in the rendered PDF despite `\item` being present in the source, flag as a defect: bullet markers are a load-bearing visual element of the deck. The most common cause is `\usepackage{enumitem}` in the preamble, which silently overrides Beamer's bullet template and strips visible glyphs from every itemize in the deck. Fix: remove `\usepackage{enumitem}` and rewrite any `\begin{itemize}[leftmargin=*]` to use native LaTeX (`\setlength{\leftmargini}{1em}\begin{itemize}`).
13. **Acronym discipline.** Per the Acronyms and Abbreviations section in `SKILL.md`: every acronym not on the exemption list must be defined on its first deck-wide appearance using the form `Term (ACRONYM)`. Audit procedure: grep `slides.tex` for tokens matching `[A-Z][A-Z0-9&]{2,}` (three or more consecutive uppercase letters, digits, or ampersands; catches RCT, RLHF, R&D, P&L, and similar). For each unique token, locate its first occurrence in slide order. Verify either (a) the token is on the exemption list (Geographic/political, Business roles and education, Tech generic, Business and finance, US agencies and regulation — canonical list in `SKILL.md`), or (b) the first occurrence is the acronym in parentheses immediately after its full term (`Term (ACRONYM)`), or the acronym immediately followed by the full term in parentheses (`ACRONYM (Full Term)` — also accept this form even though `SKILL.md` prescribes the first; rewrite to `Term (ACRONYM)` if found). Acronyms inside `\includegraphics{...}` extracts from the source paper are exempt (the figure carries the paper's own conventions). Flag every unexpanded non-exempt acronym with its first-occurrence slide number. The fix is to expand on first use; do not delete the acronym to bypass the rule.
14. **Register and domain translation (judgment scan, not a grep).** This item applies only when `register=business` (the default); skip it entirely when `register=technical`, where the source vocabulary is kept for a specialist reader. With a business register the reader is a business or executive audience, not a specialist in the source's field, so the source's terms of art must be translated. Flag three patterns: (a) a domain term from the source's field or its subject matter used on a slide without being translated or glossed on its first deck-wide appearance; (b) a chart, axis label, metric name, or legend entry that states a quantity only a specialist can decode, without naming what it measures and against what baseline in the audience's words; (c) a term translated one way on one slide and left in the source vocabulary (or paraphrased differently) on another. This is the audit-time backstop to the Step 0.5 register resolution in `SKILL.md`. Fix by translating or glossing on first use, relabeling or captioning the chart, and making the chosen rendering consistent across the deck. Read each slide as the target reader would; this is a judgment scan, not a mechanical pattern match.

## Deck-Level Checks

1. **Citation strategy:** if >80% of content slides cite the same source, replace per-slide `\sourcecite{}` with a single "Based on [Author. Year. Title.]" line on the title slide. Do not retain per-slide citations with rationale about "academic deck" or "classroom use"; repeated identical citations add visual noise without informational value. Slides citing a different source retain their own `\sourcecite{}`.
2. **Cross-deck terminology:** if multiple related decks are built from the same source, verify shared labels and terminology match across decks.
3. **Limitations slide format:** if a Limitations slide exists, verify each card or item follows the three-part structure specified in `SKILL.md` Content Requirements: **what a skeptic would say / why the concern is reasonable / how it is addressed or acknowledged.** Short prose paragraphs without that structure are a defect. The three-part format reads as a Devil's Advocate exchange, which is the pedagogical pattern this slide is designed for; loose prose loses that affordance. Fix by rewriting each card with three labeled lines (for example, bolded "Concern:" / "Why reasonable:" / "Response:" or equivalent).

4. **No facilitator prompts outside teaching/lecture structures:** when the active structure is mba, faculty, professional, consulting, or working, grep the `.tex` source for `\textit{Discuss:`, `\textit{Activity:`, `\textit{Reflect:`, `\textit{Think about:`, `\textit{Ask the room:`, and similar facilitator-prompt patterns. Flag every match. These belong only in teaching or lecture decks. Fix by deleting the entire facilitator-prompt block (and adjusting any surrounding `\vskip` spacing). Correct styling (`\footnotesize\color{CharText}`) does not exempt the prompt; the defect is its presence on a non-teaching deck, not its appearance.

5. **Compress decision audit (each Compress is content-tested, not count-tested).** For every Compress decision recorded in Step 0.7 of `SKILL.md`, verify the two or more folded findings share the same magnitude, the same country, the same mechanism, and the same time period. If any of those differ, the Compress is a defect: the folded findings must be restored as separate slides. Specifically flag:
    - Findings about different countries folded into one slide when their magnitudes differ (for example, sector-staying contribution in three countries with three different magnitudes folded into one card-set slide).
    - Findings about different mechanisms folded into one slide (for example, sector / location / occupation / FLFP findings folded into one "no single pathway" slide when each has a distinct mechanism with its own magnitude).
    - Findings about different time periods folded into one slide.
    - A country exception folded into a parent slide as a footer or aside when the exception itself has a distinct magnitude or distinct mechanism.

    **Diagnostic signal (not a numerical floor):** if the final deck has fewer than 8 slides for an academic paper, working paper, long-form report, or whitepaper, suspect over-compression. Inspect every Compress decision. Restore any whose folded items have different magnitudes, countries, mechanisms, or time periods. The signal is "too few for the source," not "below a numerical floor"; if the source has only three distinct findings, the deck legitimately stays small. This rule is the audit-time backstop to the Step 0.7 Compress discipline.

## Narrative Arc

1. **Section-level arc check:** within each thematic section of the deck, verify the slide sequence moves from narrative/application toward technical/framework. The expected progression is: Narrative (story, concrete scene), then Application (specific example), then Visual (chart, diagram), then Technical (equation, formal framework). If a technical slide appears before its motivating example or application, flag for reordering.
2. **Opening check:** the first content slide after the title must be a hook (surprising finding, paradox, concrete problem), not a definition, agenda, or literature review.
3. **Closing check:** the final slide must be a memorable takeaway or actionable statement, not "Questions?" or "Thank you."
4. **Devil's Advocate placement:** if a limitations/critique slide exists, verify it appears in Act III (near the end), after the main findings but before the closing.

## Methodology Slide Structure

If the deck has a methodology slide (per the Methodology Slide Template in `SKILL.md`), verify these structural rules:

1. **Element vocabulary:** every element label on the slide is drawn from the canonical seven — Question, Method, Data, Population, Outcomes, Comparison, Analysis. Flag any label outside this set (for example, "Approach," "Sample," "Setup," "Hypotheses," "Variables"). The template's value is cross-deck consistency; substitute labels break the pattern.
2. **Column placement:** elements present from {Question, Method, Data, Population} appear in the left column; elements present from {Outcomes, Comparison, Analysis} appear in the right column. Cross-column placement is a defect.
3. **Order within column:** within each column, elements appear in canonical order top-to-bottom. Left column order: Question → Method → Data → Population (omitting drops). Right column order: Outcomes → Comparison → Analysis (omitting drops). Reordered elements are a defect.
4. **Label color uniformity:** every element label uses DeepTeal via `\textbf{\color{DeepTeal}<Label>:}` or equivalent. Mixed colors across labels are a defect. Verify all element labels share the same DeepTeal color macro.
5. **Phrase length:** each element's content is a short phrase, not a paragraph or bullet list. Flag any element whose content wraps to a third line at the slide's column text width; two-line phrases are acceptable, three-line or longer are over-budget. The fix is to tighten the phrase, not shrink the font.
6. **Column balance:** neither column has fewer than 2 elements after drops, OR the slide uses an explicit single-column layout. If both columns are present with one column at 1 element and the other at 3+, flag for rebalance: move Outcomes to the left column, or collapse to single-column. Do not ship asymmetric two-column methodology slides.
7. **Sanity check signal:** does the rendered slide let a reader predict the shape of the findings slides? This is a judgment call, not a mechanical grep — the audit agent makes this assessment after reading the slide and the deck's findings slides. If the answer is no, recommend restoring a dropped element or strengthening an existing phrase.

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
8. Source citations must use `\sourcecite{}` with Chicago Author-Date (Author, Year, Title, Publication; all set upright, no `\textit{}` on titles). No ad-hoc "Source: X" text, no custom footer macros, no manual `\vfill` constructions.
9. `\sourcecite{}` must use `[remember picture,overlay]` with `yshift=10mm`, `anchor=south east`, `align=right`, `text width=\dimexpr\paperwidth-36pt\relax`. Do NOT use `\RaggedLeft` or `\raggedleft` inside TikZ nodes.
10. No visible insertion notes or `\insertnote` on slides; notes use `\note{}` only.
11. The preamble must match `../../style-guides/beamer/style-guide.md` Quick Reference exactly (colors, theme, fonts, templates, macros, `\setbeamersize`, footer `\vskip8mm`).

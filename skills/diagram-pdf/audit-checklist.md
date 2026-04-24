# Diagram Audit Checklist

This file is read by the independent audit agent invoked from the `diagram-pdf` skill in Step 5. The audit agent has NO knowledge of the generation process, what fixes were previously attempted, or what the generating agent intended. It receives only the compiled PDF and `.tex` source, and judges them on their merits.

## Methodology

- Check every element individually. Do not skip nodes that "look fine."
- For spatial checks, perform coordinate arithmetic on the `.tex` source. Compute bounding boxes from node coordinates, minimum width/height, inner sep, and yshift/xshift values. Do not rely solely on visual inspection of the PDF.
- Report defects with specific node names and coordinates.
- Do not use soft language ("might overlap," "could be tight"). State definitively whether each check passes or fails.
- For feedback arrow corridors: independently verify that corridor x-coordinates clear all elements by computing bounding boxes. Do not trust comments in the `.tex` source about clearances.
- For paired nodes (two nodes flanking a spine node with yshifts): compute the gap between the pair by subtracting node heights from center-to-center distance. If gap is zero or negative, it is a clearance defect.

## Checklist

| # | Category | Check |
|---|----------|-------|
| 1 | **Element clearance** | No text node overlaps another text node. Compute bounding boxes from coordinates, minimum width/height, and inner sep. Verify no intersection. Every label has at least 3pt visible whitespace from adjacent elements. |
| 2 | **Paired node clearance** | For every pair of nodes positioned with yshifts relative to the same parent (e.g., two outputs left of a step), compute: gap = center-to-center distance minus sum of half-heights. Gap must be > 0. |
| 3 | **Arrow routing** | No arrow path crosses through an unrelated filled node. For each arrow, check whether any segment passes through a content box that the arrow does not connect to. If it does, the connected element must be repositioned (not layered behind). |
| 4 | **Label readability** | All labels are at least `\scriptsize` (7pt equivalent). Arrow labels do not overlap each other or other text. Labels on long arrows are positioned near the source end (pos=0.15-0.25) to stay in clear space. |
| 5 | **Consistent sizing** | Sibling nodes in the same visual group must have equal `minimum width` AND equal explicit `minimum height`. "No minimum height set on any of them" fails this check. In grid, flow, and comparison layouts, every sibling must have `minimum height` set to a common value so rendered heights match regardless of content volume. Nodes rendering at unequal heights because content alone determines height is a defect, even when `minimum width` matches. |
| 6 | **Color consistency** | Each semantic role uses the correct color from the style guide. No ad-hoc colors. Light fills use the correct percentage (15% for input, 12% for output, 8-10% for context). |
| 7 | **Alignment** | Stacked nodes share the same x-coordinate. Side-by-side nodes share the same y-coordinate. Gaps between adjacent nodes in a sequence are consistent. |
| 8 | **Arrow endpoint accuracy** | Every arrow connects to the intended target node anchor. An arrow ending at coordinates that miss the target node by more than 2mm is a defect. |
| 9 | **Arrow endpoint precision** | Arrow endpoints must not clip, poke into, or overlap unrelated node boundaries. The last 3mm of every arrow path must be in clear space before reaching its target anchor. An arrowhead that visually enters a node it does not connect to is a defect. |
| 10 | **Legend completeness** | The legend includes every node type and arrow type used in the diagram. No missing or extra entries. |
| 11 | **Title and subtitle** | Present, correctly styled, adequate clearance from the first diagram element. |
| 12 | **Special character encoding** | No raw `>`, `<`, `&`, `%`, `_`, or `#` in text nodes. All must be LaTeX-escaped. |
| 13 | **Special character rendering** | After compilation, verify that underscores, ampersands, percent signs, and other LaTeX-special characters render correctly in the PDF. Cross-check against the `.tex` source. |
| 14 | **Label proximity** | Every arrow label must be visually adjacent to and clearly associated with the arrow it describes. A label floating in empty space with no nearby arrow is a defect. If the arrow is long, the label should be placed on the arrow path (using `node[lbl,pos=0.5]` or similar), not at a hardcoded coordinate disconnected from the path. |
| 15 | **Whitespace balance** | The diagram's content midpoint (average of the leftmost and rightmost element edges) must be within 0.5cm of x=0. For any multi-element row (legend, label row, cluster row), the row's horizontal midpoint must also align with x=0 within 0.5cm. Significant left-right asymmetry is a defect; compute the midpoint and state it in the report if this check fails. |
| 16 | **Arrow label legibility** | Arrow labels must use at least `\scriptsize` font size. Labels in MedGray must be at least `\footnotesize` to remain legible when projected or printed. |
| 17 | **Junction/fork rendering** | Where a single arrow path forks into multiple targets, verify the fork point renders cleanly without visual artifacts. If artifacts appear, draw separate arrows from the source node to each target instead of forking. |
| 18 | **Feedback corridor clearance** | For diagrams with feedback arrows routed through corridors: verify that the corridor x-coordinate clears the east (or west) edge of every element on that side by at least 0.4cm. Compute from bounding boxes, not from comments in the `.tex`. |
| 19 | **Thematic accuracy** (thematic layout only) | Theme labels accurately reflect the source input. Sub-theme bullets are factual and traceable to the user's source material. No hallucinated themes. |

## Report Format

Return a structured report:

```
Diagram Audit: [N] defects found

1. [Category]: [specific node names, coordinates, and description]. Severity: CRITICAL/MAJOR/MINOR. Proposed fix: [concrete .tex change].
2. ...

Pass (if zero defects)
```

Severity levels:
- **CRITICAL**: Arrow crosses through node, node overlap, arrowhead enters unrelated node
- **MAJOR**: Readability issue, clearance < 3pt, alignment defect, missing legend entry
- **MINOR**: Cosmetic (whitespace balance, style name deviations, unused library)

Each defect must include:
- The specific node name(s) involved
- Coordinates from the `.tex` source demonstrating the problem (bounding box arithmetic)
- A proposed fix with specific parameter changes

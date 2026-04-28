# External Figure Generation with Matplotlib

Rules for generating figures outside of pgfplots using Python and matplotlib. These figures are saved as PDF, included in the deck via `\includegraphics`, and accompanied by standalone scripts students or collaborators can run.

---

## When to Use Matplotlib vs. pgfplots

| Figure type | Use | Reason |
|---|---|---|
| Simple bar chart (single or grouped, under 8 categories) | pgfplots | Well-supported by the style guide; audit checklist covers all edge cases |
| Simple line chart (1-3 series, single panel) | pgfplots | Native axis control, palette integration, tick formatting |
| Scatter plot (single panel) | pgfplots | Clean with `only marks` |
| Stacked bar chart | pgfplots | `ybar stacked` plus `reverse legend` is reliable |
| Horizontal bar chart | pgfplots | `xbar` with `bar shift=0pt` |
| **Multi-panel / faceted plot** | **matplotlib** | pgfplots has no native facet support; manual subfigures are fragile |
| **Statistical overlays** (confidence bands, KDE, regression with CI) | **matplotlib** | `fill_between`, `kdeplot` (seaborn), statsmodels integration |
| **Complex annotations** (many labeled regions, callout arrows, shaded periods) | **matplotlib** | `ax.annotate` plus `FancyArrowPatch` is more flexible than pgfplots annotations |
| **Geographic / map visualization** | **matplotlib** | geopandas plus matplotlib; pgfplots cannot do maps |
| **Structural equation model / path diagram** | TikZ (in .tex) | TikZ is better for node-and-arrow diagrams with precise positioning |
| **Simple flow / hierarchy diagram** | TikZ (in .tex) | Use the `diagram-pdf` skill's patterns |

**Default to pgfplots.** Only use matplotlib when the figure exceeds pgfplots' comfortable range per the table above. pgfplots figures are editable in the .tex source; matplotlib figures are static images.

---

## Palette Export

Every matplotlib script must import the deck's color palette. Use this dict at the top of every script:

```python
# Beamer deck palette (matches style-guides/beamer/style-guide.md)
PALETTE = {
    'SlateNavy':   '#1B2A4A',
    'DeepTeal':    '#0D7377',
    'CyanBlue':    '#0077B6',
    'DustyPlum':   '#9B5978',
    'BurntOrange': '#BF5700',
    'WarmAmber':   '#E8913A',
    'SoftRed':     '#DC5C5C',
    'AccentRed':   '#C0392B',
    'AccentGreen': '#27AE60',
    'MedGray':     '#B0AFA8',
    'CharText':    '#3A3A3A',
    'PaleBlue':    '#E8F0F8',
    'LightGray':   '#F0EFEC',
}
```

### Color assignments for chart series (matches the Beamer style guide)

| Series | Color key | Use |
|---|---|---|
| Primary / baseline | `DeepTeal` | First series, main data line |
| Secondary / alternative | `CyanBlue` | Second series |
| Tertiary / positive | `AccentGreen` | Third series, growth |
| Reference / trend line | `MedGray` | Dashed reference lines |
| Fifth | `DustyPlum` | Additional series |
| Alert | `AccentRed` | Warnings, negative outcomes |
| Dark / aggregate | `SlateNavy` | Totals, emphasis |

---

## Figure Background and Styling

Every figure must match the slide background (white) and use consistent typography:

```python
import matplotlib.pyplot as plt
import matplotlib as mpl

# Match slide background
fig, ax = plt.subplots(figsize=(6, 3.5))
fig.set_facecolor('#FFFFFF')
ax.set_facecolor('#FFFFFF')

# Typography: sans-serif, matching Beamer defaults
mpl.rcParams['font.family'] = 'sans-serif'
mpl.rcParams['font.sans-serif'] = ['Helvetica', 'Arial', 'DejaVu Sans']
mpl.rcParams['font.size'] = 10
mpl.rcParams['axes.labelsize'] = 11
mpl.rcParams['axes.titlesize'] = 12
mpl.rcParams['xtick.labelsize'] = 9
mpl.rcParams['ytick.labelsize'] = 9

# Clean axes (match pgfplots axis lines=left)
ax.spines['top'].set_visible(False)
ax.spines['right'].set_visible(False)
ax.spines['left'].set_color(PALETTE['CharText'])
ax.spines['bottom'].set_color(PALETTE['CharText'])
ax.tick_params(colors=PALETTE['CharText'])
```

---

## Output Conventions

### File locations

```
<parent>_build/
├── scripts/
│   ├── fig1_descriptive_name.py    # standalone script
│   └── fig2_descriptive_name.py
├── figures/
│   ├── fig1_descriptive_name.pdf   # vector output
│   └── fig2_descriptive_name.pdf
```

### Script requirements

Each script must be **standalone**: a reader can open it, run it with `python3 scripts/fig1_name.py`, and reproduce the figure.

1. All imports at the top
2. Palette dict at the top (copy from above)
3. Data defined or loaded at the top (use relative paths to a `data/` directory if external data is needed; for approximated data from papers, define coordinates inline with comments noting the source)
4. Figure construction in the middle
5. `plt.savefig()` at the bottom, saving to `../figures/fig1_name.pdf`
6. No shared state between scripts
7. No dependencies on other scripts in the same directory

### Output format

- **Vector PDF** for line charts, bar charts, scatter plots, and schematics: `plt.savefig('path.pdf', bbox_inches='tight', dpi=300)`
- **PNG at 300 DPI** only for dense rasters (heatmaps, images) where PDF would be too large: `plt.savefig('path.png', dpi=300, bbox_inches='tight')`

---

## Figure Design Rules

### One message per figure

If you can't state the takeaway in one sentence, the figure is too complex. Split it.

### Title states the finding, not the chart type

```python
# GOOD
ax.set_title('Peer Influence Drives Adoption More Than Training',
             fontsize=12, fontweight='bold', color=PALETTE['CharText'])

# BAD
ax.set_title('Bar Chart of Adoption Factors',
             fontsize=12, fontweight='bold', color=PALETTE['CharText'])
```

### Direct labels, no legends (when possible)

Label data directly at endpoints, inside bars, or adjacent to data points. Reserve legends only when density makes direct labels unreadable.

```python
# Direct label at line endpoint
ax.annotate('Peer influence', xy=(x[-1], y[-1]),
            xytext=(10, 0), textcoords='offset points',
            fontsize=9, color=PALETTE['DeepTeal'], fontweight='bold')
```

### No chartjunk

Remove gridlines, borders, unnecessary axis marks. Use `ax.spines['top'].set_visible(False)` and `ax.spines['right'].set_visible(False)` (already in the template above).

---

## Bezier Helper Functions for Curved Arrows

When generating figures with curved arrows (`connectionstyle='arc3'`), include these helper functions. They compute exact curve positions so labels can be placed precisely.

```python
import numpy as np

def arc3_control_point(x1, y1, x2, y2, rad):
    """Compute the quadratic Bezier control point for matplotlib's arc3 connectionstyle.
    Formula from matplotlib source: cx = mid_x + rad*dy, cy = mid_y - rad*dx
    """
    dx, dy = x2 - x1, y2 - y1
    cx = (x1 + x2) / 2 + rad * dy
    cy = (y1 + y2) / 2 - rad * dx
    return cx, cy

def find_t_for_x(target_x, x1, cx, x2, num_samples=1000):
    """Find the Bezier parameter t where x(t) is approximately target_x."""
    ts = np.linspace(0, 1, num_samples)
    xs = (1 - ts)**2 * x1 + 2 * (1 - ts) * ts * cx + ts**2 * x2
    return ts[np.argmin(np.abs(xs - target_x))]

def bezier_y_at_t(t, y1, cy, y2):
    """Y-coordinate of quadratic Bezier at parameter t."""
    return (1 - t)**2 * y1 + 2 * (1 - t) * t * cy + t**2 * y2
```

**When to use:** every time a matplotlib figure has `connectionstyle='arc3'` and labels near those arrows.

---

## Including Matplotlib Figures in the Deck

In the .tex file, reference matplotlib-generated figures with both width and height constraints:

```latex
\includegraphics[width=0.85\textwidth,height=0.68\textheight,keepaspectratio]{figures/fig1_descriptive_name}
```

Omit the file extension; pdflatex will find the .pdf automatically. Always include `keepaspectratio` to prevent distortion. The `height=0.68\textheight` constraint prevents tall figures from overflowing into the `\sourcecite` zone.

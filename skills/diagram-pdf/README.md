# Diagram PDF

Generate standalone TikZ diagrams compiled to PDF, with an independent audit agent that catches overlap and routing defects before delivery.

## Problem

Writing TikZ by hand is slow. Asking a language model to write TikZ in one pass is fast but unreliable: the model outputs syntactically correct code that looks plausible, compiles cleanly, and still renders with arrows crossing unrelated nodes, paired labels overlapping, or feedback loops routed straight through the middle of the diagram. The generating model cannot see these defects because it sees the code it intended, not the rendered output.

This skill treats diagram generation as a compile-then-audit loop. Positioning is algorithmic rather than guessed. Complex routing (feedback loops, cycles with cross-connections) uses a two-phase generation that extracts actual node coordinates from a first-pass compile before placing the routed arrows. Every diagram goes through an independent audit agent that performs coordinate arithmetic on the `.tex` source and reports defects with concrete fixes. Defects are fixed and the audit re-runs until the diagram is clean.

## Approach

Five design choices shape the skill:

1. **Algorithmic positioning, not eyeballed positioning.** For each layout type (pipeline, hierarchy, cycle, hub-and-spoke, thematic), the skill uses a fixed set of spacing constants and geometric rules. The generating model applies the rules rather than inventing coordinates.

2. **Two-phase generation for complex routing.** Feedback arrows and other routing that must navigate around unrelated nodes cannot be placed reliably without knowing where the nodes actually ended up. Phase 1 compiles the static elements and emits bounding box coordinates; Phase 2 uses those coordinates to compute safe corridors and place the routed arrows.

3. **Independent audit agent, not self-audit.** A separate agent receives only the compiled PDF, the `.tex` source, and the audit checklist. It performs coordinate arithmetic and reports defects with specific node names and proposed fixes. The generating model's beliefs about its own output are not on the table.

4. **Fix-and-re-audit loop with a convergence limit.** If the audit finds defects, the generating model fixes them, recompiles, and re-invokes the audit. Maximum three rounds. If defects persist, the skill hands the result over with remaining findings noted rather than looping forever.

5. **Style-guide-driven visuals.** Colors, typography, node shapes, and arrow styles are defined in a companion style guide. The skill reads the guide on every invocation and applies it consistently. Changing the style guide changes every diagram without changing the skill.

## The Flow

**Step 0: Verify LaTeX installation.** Check that `pdflatex` is available. If not, point the user to the appropriate installer for their OS.

**Step 1: Determine layout and content.** Either parse a free-text description into layout + elements, or auto-discover a workflow from a set of SKILL.md files.

**Step 2: Read the style guide.** Load colors, node styles, arrow styles, typography, and spacing constants. These drive every decision in Steps 3 through 6.

**Step 3: Generate the `.tex`.** Apply the layout-specific positioning rules. For simple layouts, write the full `.tex` in one pass. For complex layouts (feedback loops, cycles with cross-connections), run the two-phase procedure: compile a version with coordinate-extraction macros, parse the bounding boxes from the log, then compute safe corridors and write the final `.tex`.

**Step 4: Compile.** Run `pdflatex`. If compilation fails, fix the source and recompile. Do not proceed to the audit with a failed compilation.

**Step 5: Independent quality audit.** Hand the compiled PDF and `.tex` source to an independent agent with the audit checklist and style guide. The agent reports defects with specific node names, coordinates, and proposed fixes.

**Step 6: Fix, re-audit, and present.** Apply all defect fixes. Recompile. Re-run the audit (fresh agent, no memory of prior findings). Repeat up to three rounds. Deliver the final PDF to the user.

## Usage

**Trigger phrases:** `create a diagram`, `diagram this`, `workflow diagram`, `draw a diagram`, `visualize this workflow`, `diagram the themes`, `thematic diagram`, `concept map`, `org chart`, `process diagram`

**Good uses:**
- Visualizing a skill or process workflow with multiple steps, inputs, outputs, and handoffs
- Org charts, decision trees, or taxonomies with clear hierarchical structure
- Feedback loops or cyclical processes where routing matters
- Hub-and-spoke concept maps
- Thematic grouping of user-supplied ideas with relationships drawn between clusters

**Not good uses:**
- Quick sketches where visual precision is not required (a whiteboard photo is faster)
- Charts of numerical data (bar charts, line charts, scatter plots); use a charting workflow instead
- Diagrams with freeform geometry or hand-drawn style; TikZ is structural, not expressive

**Tips:**
- For auto-discovery mode, point the skill at a folder of `SKILL.md` files and ask it to build a workflow diagram. It will extract triggers, handoffs, and pipeline relationships.
- For thematic diagrams, give the skill a list of themes and sub-themes directly. The skill does not run document summarization; bring summarized themes in, or pair this skill with your own summary workflow.
- If an audit finds defects, let the skill run the fix-and-re-audit loop. Interrupting mid-loop usually produces a worse result than letting it converge.

## Installation

1. **Copy the skill files** to `~/.claude/skills/diagram-pdf/`:
   - `SKILL.md`
   - `audit-checklist.md`

2. **Install the style guide.** The skill reads a companion style guide for colors, typography, and node conventions. Two options:
   - Keep the repo structure: leave `style-guides/diagram-pdf/style-guide.md` in the repo and have the skill read it by its repo-relative path.
   - Copy it into your skills area: place `style-guide.md` somewhere Claude Code can read (for example `~/.claude/skills/diagram-pdf/style-guide.md`) and update the Step 2 path in `SKILL.md` accordingly.

3. **Verify `pdflatex` is installed.** macOS: `brew install --cask mactex-no-gui`. Linux: `sudo apt install texlive-full`. Windows: install MiKTeX from https://miktex.org/download. Then restart your terminal and check `pdflatex --version`.

4. **Restart Claude Code** (or start a new session). The skill activates on any trigger phrase above.

## Output

- **Primary deliverable:** `<descriptive-name>-diagram.pdf` in the current working directory (or a user-specified output folder).
- **Build artifacts:** `.tex`, `.pdf`, `.log`, `.aux` in `<output-folder>/diagram-build/`.
- The `.tex` source is the editable artifact. Open it, edit coordinates or content, and recompile with `pdflatex` to iterate outside the skill.

## Design Rationale

**Independent audit agent, not self-audit.** Testing confirmed that paired-node overlap defects (yshift spacing too tight) went undetected across multiple self-audit rounds but were immediately caught by a separate agent doing coordinate arithmetic. The generating model sees what it meant; the audit agent sees only what is there.

**Two-phase generation for feedback arrows.** Guessing corridor x-coordinates from estimated node positions fails reliably once the layout has more than a few elements. Extracting actual bounding boxes from a first-pass compile is the shortest path to routing that works on the first audit round.

**Convergence limit of three audit rounds.** Most defects are caught and fixed in round one. Rounds two and three catch secondary issues introduced by the fixes themselves. Beyond round three, defects are usually structural (wrong layout choice) and another audit pass will not fix them; the user needs to be told.

**Style guide separate from skill.** Colors, typography, and spacing change with branding or audience. Keeping them in a separate file means the skill does not need edits when the visual style changes, and other tools (for example a slides workflow) can share the same palette by reading the same guide.

**Algorithmic positioning over free generation.** Asking a language model to choose coordinates leads to cramped corners, asymmetric margins, and overlap at every scale. Fixing spacing constants into the skill produces diagrams that are symmetric and legible without per-diagram tuning.

# Skills Catalog

Each skill is a self-contained workflow that Claude Code loads on demand when your request matches its triggers. Install a skill by copying its `SKILL.md` into `~/.claude/skills/<skill-name>/SKILL.md`.

## Available Skills

### Content Creation

| Skill | What It Does |
|-------|-------------|
| [beamer](beamer/) | Generate LaTeX Beamer slide decks with TikZ figures and a four-step compile-audit-fix cycle |
| [slides-content](slides-content/) | End-to-end pipeline: source document (PDF, markdown, text) to compiled presentation slides |
| [diagram-pdf](diagram-pdf/) | Generate standalone TikZ diagrams (pipelines, hierarchies, cycles, hub-and-spoke, thematic) compiled to PDF, with an independent audit agent |

### Analysis

| Skill | What It Does |
|-------|-------------|
| [ai-council](ai-council/) | Pressure-test a decision or argument through a structured five-advisor deliberation |
| [ai-council-deep](ai-council-deep/) | Interactive variant of ai-council with three user checkpoints for high-stakes decisions such as term sheet evaluation and choosing between strategic pivots |
| [analyze-reply](analyze-reply/) | Fact-check a forwarded article, essay, or email, then draft a reply in your voice |

### Knowledge Management

| Skill | What It Does |
|-------|-------------|
| [split-pdf](split-pdf/) | Split and deeply read academic PDFs in 4-page chunks to avoid shallow comprehension |
| [knowledge-base](knowledge-base/) | Process, index, summarize, and query a personal document library |

### Process Guides

| Skill | What It Does |
|-------|-------------|
| [writing-voice-guide](writing-voice-guide/) | How to create a consistent writing voice layer for your AI environment (process guide, not a skill file) |
| [handoff-resume](handoff-resume/) | Session continuity protocol for carrying project context across Claude Code sessions |

## Dependencies

Some skills reference [style guides](../style-guides/) for formatting rules. If you install a skill that references a style guide, install the style guide too, or replace the reference with your own formatting standards.

## Customization

These skills are starting points. Adapt them to your own workflows:

- Change trigger phrases to match how you naturally ask for things
- Adjust quality gate criteria to match your standards
- Replace style guide references with your own formatting rules
- Add or remove pipeline steps as needed

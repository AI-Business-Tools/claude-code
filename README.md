# Claude Code

A getting-started guide and a skills library for business professionals and educators.

## Start here

New to this repository? Work through it in order:

1. **[Get started](getting-started/).** What Claude Code adds beyond Claude chat and Cowork, how to install it on Mac or Windows, and how to set up your first project.
2. **[Set up version history](skills/git-sync/).** Put your Claude Code environment under Git and sync two machines through a private GitHub repository, so every change to your skills and standards is tracked and reversible.
3. **[Adopt handoffs and resume](skills/handoff-resume/).** End each session with a structured summary so the next one picks up where you left off.
4. **[Browse the skills](skills/).** Reusable workflows for slides, documents, analysis, and knowledge management.

## About

This repository is maintained by [Ben Bentzin](https://www.linkedin.com/in/bentzin/), Associate Professor at the University of Texas at Austin McCombs School of Business. Ben teaches AI strategy to MBA students and corporate executives and serves as a McCombs Teaching Fellow focused on faculty AI integration. He writes about integrating AI into business at [businessai.substack.com](https://businessai.substack.com).

These skills were built to solve a practical problem: producing consistent, high-quality course materials (slide decks, exercises, case studies, analyses) across a full-semester MBA course on AI strategy. The tools here are the result of that work, generalized for anyone doing similar knowledge work with Claude Code.

## What This Is

A collection of Claude Code skills, style guides, and templates that turn ad-hoc AI prompting into structured, repeatable professional workflows. The skills were developed for MBA course development but apply to any knowledge worker who creates documents, presentations, analyses, and research summaries.

## Who This Is For

- **Business faculty** creating course materials (slides, exercises, cases, discussion outlines)
- **Knowledge workers** who produce recurring document types (presentations, proposals, reports)
- **Claude Code users** looking for practical skill examples beyond software development
- **Anyone** interested in building structured AI environments for professional work

## Philosophy

Most AI usage today is ad-hoc: each conversation starts from scratch, corrections are forgotten when the chat ends, and output quality depends entirely on the user's prompting skill in the moment.

A structured AI environment changes this. Corrections persist as feedback memories. Recurring tasks run as reusable skills with built-in quality gates. Project context carries forward through handoffs. The investment is not in learning to code; it is in encoding your professional judgment into rules, skills, and quality standards that compound over time.

This repository publishes the skills, templates, and methodology behind that approach.

### The Four-Layer Model

| Layer | Purpose | Example |
|-------|---------|---------|
| **Rules** (CLAUDE.md) | Declarative constraints loaded every session | Writing standards, routing tables, delivery gates |
| **Reinforcement** (Memories) | Corrections and preferences that persist across sessions | "Save each project's deliverables to the top level of its folder" |
| **Execution** (Skills) | Procedural workflows loaded on demand | PDF-to-slides pipeline, exercise generator |
| **Enforcement** (Audit Agents) | Post-hoc quality checks that catch what the compiler misses | Beamer overlay audit, anonymization checklist |

See [methodology.md](methodology.md) for the full design rationale.

## Set up your environment

The foundations the rest of this repository builds on. The [Getting Started guide](getting-started/) walks a newcomer through them, or you can go straight to each:

- **[git-sync](skills/git-sync/)** *(recipe)*. Version your `~/.claude` environment with Git and keep two machines in sync through a private GitHub repository. You get history, diffs, and one-command revert on your skills, standards, and memory. Point Claude Code at the directory and it can do the setup for you.
- **[handoff-resume](skills/handoff-resume/)** *(protocol)*. Carry project context across sessions: end with a structured summary, and start the next session by reading it back.
- **[CLAUDE-template](CLAUDE-template/CLAUDE.md)**. A starting `CLAUDE.md` to copy and customize for your identity, writing standards, and workflow.

## Skills

Task-specific workflows, each loaded on demand when your request matches its triggers. Most install by copying `SKILL.md` into `~/.claude/skills/<skill-name>/SKILL.md`; `writing-voice-guide` is a process guide you follow to build your own voice layer. Each skill's README documents its own install steps.

| Skill | Description | Details |
|-------|-------------|---------|
| [split-pdf](skills/split-pdf/) | Split and deeply read academic PDFs in 4-page chunks | Avoids shallow single-pass reads of long documents |
| [beamer](skills/beamer/) | Generate LaTeX Beamer slide decks with TikZ figures | Includes a four-step compile-audit-fix cycle |
| [slides-content](skills/slides-content/) | End-to-end: source content to compiled slides to PPTX | PDF, markdown, or text input; presentation output |
| [knowledge-base](skills/knowledge-base/) | Process, index, summarize, and query documents | Personal knowledge management pipeline |
| [ai-council](skills/ai-council/) | Five-advisor council with anonymous peer review | Pressure-test decisions with structured deliberation |
| [ai-council-deep](skills/ai-council-deep/) | Interactive variant with three user-in-the-loop checkpoints | High-stakes decisions: term sheets, pivots, pre-publication strategy memos |
| [analyze-reply](skills/analyze-reply/) | Fact-check a forwarded article, essay, or email and draft a reply in your voice | Pairs with a writing voice layer |
| [diagram-pdf](skills/diagram-pdf/) | Generate standalone TikZ diagrams (pipelines, hierarchies, cycles, hub-and-spoke, thematic) | Independent audit agent verifies layout |
| [writing-voice-guide](skills/writing-voice-guide/) | How to create your own writing voice layer | Process guide, not a skill file |

For the full catalog grouped by purpose, including `summary-academic`, `summary-general`, `knowledge-base-update`, and `skill-audit`, see [skills/README.md](skills/README.md).

## Style Guides

- [Beamer Style Guide](style-guides/beamer/): LaTeX setup, color palette, typography, and TikZ conventions
- [PPTX Style Guide](style-guides/pptx/): Python setup, PowerPoint formatting rules, and conversion workflow from Beamer

See [style-guides/README.md](style-guides/README.md) for how to adapt these to your own branding.

## Acknowledgments

Several skills in this repository build on work by others:

- **Scott Cunningham**, Professor of Economics, Baylor University. `split-pdf` and the Beamer slide generation approach originated in his [MixtapeTools](https://github.com/scunning1975/MixtapeTools) repository. [LinkedIn](https://www.linkedin.com/in/scott-cunningham-7788912/)
- **John Graff**, Assistant Professor of Instruction, UT Austin McCombs School of Business. The AI Council methodology is adapted from his original LLM Council skill. [LinkedIn](http://linkedin.com/in/johnmgraff/)
- **Andrej Karpathy**, Founder, Eureka Labs. The knowledge base pipeline draws on his approach to personal knowledge management. [GitHub](https://github.com/karpathy)
- **Freddy Gottesman**, GHP Labs. The `ai-council-deep` interactive variant adds three user-in-the-loop checkpoints (clarify, surface assumptions, iterate) to the AI Council methodology. [LinkedIn](https://www.linkedin.com/in/fgottesman/) | [GHP Labs](https://ghplabs.ai/)

## License

[MIT](LICENSE)

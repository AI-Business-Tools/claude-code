# Claude Code

Claude Code skills for business professionals and educators.

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
| **Reinforcement** (Memories) | Corrections and preferences that persist across sessions | "Do not mock the database in integration tests" |
| **Execution** (Skills) | Procedural workflows loaded on demand | PDF-to-slides pipeline, exercise generator |
| **Enforcement** (Audit Agents) | Post-hoc quality checks that catch what the compiler misses | Beamer overlay audit, anonymization checklist |

See [methodology.md](methodology.md) for the full design rationale.

## Quick Start

1. **Install Claude Code** from [Anthropic](https://docs.anthropic.com/en/docs/claude-code)
2. **Copy the template**: start with [CLAUDE-template/CLAUDE.md](CLAUDE-template/CLAUDE.md) and customize it for your identity, writing standards, and workflow
3. **Install skills**: copy any skill's `SKILL.md` into `~/.claude/skills/<skill-name>/SKILL.md`
4. **Start working**: skills activate automatically when your request matches their triggers

## Skills

| Skill | Description | Details |
|-------|-------------|---------|
| [split-pdf](skills/split-pdf/) | Split and deeply read academic PDFs in 4-page chunks | Avoids shallow single-pass reads of long documents |
| [beamer](skills/beamer/) | Generate LaTeX Beamer slide decks with TikZ figures | Includes a four-step compile-audit-fix cycle |
| [slides-content](skills/slides-content/) | End-to-end: source content to compiled slides to PPTX | PDF, markdown, or text input; presentation output |
| [knowledge-base](skills/knowledge-base/) | Process, index, summarize, and query documents | Personal knowledge management pipeline |
| [ai-council](skills/ai-council/) | Five-advisor council with anonymous peer review | Pressure-test decisions with structured deliberation |
| [ai-council-deep](skills/ai-council-deep/) | Interactive variant with three user-in-the-loop checkpoints | High-stakes decisions: term sheets, pivots, pre-publication strategy memos |
| [writing-voice-guide](skills/writing-voice-guide/) | How to create your own writing voice layer | Process guide, not a skill file |
| [handoff-resume](skills/handoff-resume/) | Session continuity: structured handoffs and context reconstruction | Protocol for multi-session projects |

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

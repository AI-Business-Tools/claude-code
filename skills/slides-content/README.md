# Slides from Content

End-to-end pipeline from source documents to compiled presentation slides, with optional PowerPoint conversion.

## Problem

Converting a research paper, article, or set of notes into a presentation requires multiple distinct steps: reading and extracting the key material, summarizing it in a structured format, designing slides that communicate the findings visually, and delivering a format the presenter can use. Doing each step manually is time-consuming, and skipping steps (summarizing directly into slides without structured extraction, or generating slides without a quality audit) produces weaker output. This skill chains the steps together into a single automated workflow.

## Approach

The skill runs four sequential steps without pausing between them:

1. **Read the source.** PDFs are split into 4-page chunks and read inside a subagent (the Agent Isolation Protocol from `../split-pdf/SKILL.md`). Non-PDF files are read directly using `textutil` for Word/RTF formats or the Read tool for markdown, text, and LaTeX. All extracted content is written to `notes.md` in the build subdirectory. **Reuse pre-flight:** if a `<content_name>_text.md` file already sits in the output directory (typically from a prior knowledge-base run or an earlier slide build), the skill copies it to `notes.md` and skips the expensive deep-read agent.

2. **Summarize.** The skill auto-detects whether the source is academic (peer-reviewed paper, working paper, dissertation, technical report) or general (news, blog, report, interview). It applies the matching summary format and writes a structured summary to `<content_name>_summary.md` as a deliverable alongside the source file. **Reuse pre-flight:** if `<content_name>_summary.md` already exists in the output directory, the skill reuses it and skips regeneration.

3. **Generate Beamer slides.** The skill reads `../beamer/SKILL.md` and the Beamer style guide in full before writing any LaTeX. It applies the full beamer compilation cycle: write, compile (two-pass pdflatex minimum), fix warnings, quality audit via a single merged agent on the sonnet tier, and recompile. Visual representations (TikZ diagrams, tables, charts) are preferred over bullet-heavy text slides. If the user passed an `audience=` parameter (`teaching`, `faculty`, `professional`, `consulting`, or `working`), it is forwarded to the beamer skill to select the matching domain pattern.

4. **Convert to PPTX (optional).** After confirming with the user, the skill reads `../../style-guides/pptx/style-guide.md` in full, presents a per-slide conversion plan for approval, and generates native PowerPoint objects (shapes, charts, tables) using python-pptx. Image embedding is a last resort only.

## Pipeline Steps

```
Source file
    │
    ▼
Step 1: Read + extract → notes.md (build dir)
    │
    ▼
Step 2: Summarize → <content_name>_summary.md (output dir)
    │
    ▼
Step 3: Beamer slides → <content_name>_slides.pdf (output dir)
    │
    ▼  [user confirms]
Step 4: PPTX conversion → <content_name>.pptx (output dir)
```

### Directory layout

```
<parent_folder>/
└── <content_name>/                     # output directory
    ├── <content_name>.<ext>            # original source file
    ├── <content_name>_summary.md       # structured summary (deliverable)
    ├── <content_name>_slides.pdf       # compiled Beamer PDF (deliverable)
    ├── <content_name>.pptx             # PowerPoint (deliverable, if generated)
    └── <content_name>_build/           # build subdirectory
        ├── split_<content_name>/       # PDF split chunks
        ├── figures/                    # extracted source figures
        ├── notes.md                    # deep-reading extraction notes
        ├── slides.tex                  # Beamer source
        └── [LaTeX artifacts]
```

## Design Rationale

**Why a build subdirectory?** LaTeX compilation produces `.aux`, `.log`, `.nav`, `.snm`, and other artifacts. Keeping them separate from deliverables makes it clear what to hand off and what to discard.

**Why split PDFs before reading?** Long PDFs exceed context limits if read in one pass. Splitting into 4-page chunks and reading them inside a subagent (per the Agent Isolation Protocol in `../split-pdf/SKILL.md`) keeps each read within bounds while still capturing the full document.

**Why a separate summary step?** The summary serves two purposes: it is a standalone deliverable the user may want independently, and it is structured input for the slide generator. Generating slides directly from raw notes produces weaker thematic organization. The summary step forces a synthesis pass before any design decisions are made.

**Why read the style guide before every step?** Each downstream step (beamer, PPTX) has a style guide with exact specifications: preamble code, color palettes, layout constants, font-fix functions, and quality checks. Relying on memory across sessions produces drift. Mandatory reads before each step enforce consistency.

**Why pause before PPTX conversion?** The Beamer PDF is a complete deliverable on its own. Some users want only the PDF. Pausing before Step 4 prevents unnecessary work and gives the user the option to review the slides first.

**Content-over-font-size rule.** When content overflows a slide, the skill reduces content (splits slides, removes bullets, tightens wording) rather than reducing font size. Slides too small to read on a projected screen are a common failure mode.

## Usage

Trigger the skill with any of these phrases:
- "slide this"
- "slides from this"
- "create slides from this"
- "make a deck from this"
- "turn this into slides"
- "slides from this paper"
- "presentation from this article"
- "build a deck"

You can optionally provide a file path, URL, or pasted content as an argument. If you provide nothing, the skill presents a menu.

Supported input types: `.pdf`, `.md`, `.txt`, `.docx`, `.doc`, `.rtf`, `.tex`, URLs (fetched via WebFetch), pasted text.

**Note on Word and RTF sources:** `textutil` extracts text only. Embedded charts, images, and shapes in the source are not captured and will not appear in the generated deck. If the source has substantive visual content, supply a PDF version of the document instead.

**Optional audience parameter:** Append `audience=teaching|faculty|professional|consulting|working` to the invocation to forward an audience pattern to the beamer skill. If omitted, the beamer skill defaults to teaching lecture.

### Dependencies

This skill calls three other skills in sequence:

| Step | Skill |
|------|-------|
| PDF splitting and subagent read | `../split-pdf/SKILL.md` |
| Beamer slide generation | `../beamer/SKILL.md` |
| PowerPoint conversion | `../../style-guides/pptx/style-guide.md` |

A separate academic summary skill and general summary skill are referenced in Step 2. These are not included in this repository; substitute your own structured summary format or adapt Step 2 to summarize directly using the extraction notes.

## Output

| File | Location | Description |
|------|----------|-------------|
| `<content_name>_summary.md` | output directory | Structured summary of the source material |
| `<content_name>_slides.pdf` | output directory | Compiled Beamer PDF |
| `<content_name>.pptx` | output directory | Native PowerPoint (optional, generated in Step 4) |
| `notes.md` | build subdirectory | Deep-reading extraction notes (working file) |
| `slides.tex` | build subdirectory | Beamer LaTeX source (working file) |

## Installation

1. Copy `SKILL.md` into `~/.claude/skills/slides-content/SKILL.md`.
2. Install the three skills this skill calls in sequence: `split-pdf`, `beamer`, and the `style-guides/pptx/` style guide. Each has its own install steps in its README.
3. Confirm Python and TeX Live are available on your `PATH` (used by `split-pdf` and `beamer` respectively).
4. Restart Claude Code (or run `/skills` to reload).
5. Trigger by saying "make slides from this paper," "turn this into a deck," or any other phrase listed under Usage.

The skill expects a structured summary format in Step 2. The default summary skills referenced are not included in this repository; either substitute your own summary skill or adapt Step 2 to summarize directly using the extraction notes from `split-pdf`.

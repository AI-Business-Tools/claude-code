# Domain-Specific Deck Patterns

Structural templates for the beamer skill, selected by the `structure=` parameter. Each pattern specifies slide count range, density guidelines, rhetoric balance (logos/ethos/pathos), whether to include a Devil's Advocate slide, structural template, and structure-specific rules.

**Default structure: `mba`.** When no `structure=` is passed, the skill loads the MBA / Executive entry below. The legacy `audience=` parameter is a deprecated alias for `structure=` (same value set), and `academic` and `default` are deprecated aliases for `mba`. Unrecognized values fall through to `mba`.

---

## Rhetoric Balance Reference

The logos/ethos/pathos percentages do not allocate slides to categories. They control the *tone and framing* of every slide: what comes first (sequencing), how findings are introduced (framing), and what gets a full slide vs. a footnote (emphasis).

- **Logos (Logic):** "Does this make sense?" Data, evidence, frameworks, causal reasoning.
- **Ethos (Credibility):** "Why should I trust this person?" Methodology, limitations acknowledged, Devil's Advocate, process shown.
- **Pathos (Emotion):** "Why should I care?" Stories, applications, career relevance, human impact, frustration validated.

| Context | Logos | Ethos | Pathos | Slides |
|---|---|---|---|---|
| **MBA / Executive** (default) | 50% | 25% | 25% | 8+ |
| **Business school teaching** | 45% | 15% | 40% | 10-18 |
| **Faculty development** | 35% | 35% | 30% | 12-20 |
| **Professional audience** | 40% | 25% | 35% | 10-15 |
| **Consulting workshop** | 30% | 25% | 45% | 8-15 |
| **Working deck** | 55% | 25% | 20% | any |

---

## MBA / Executive (default)

**Default structure: `mba`.** This is what the skill loads when no `structure=` is passed (and for the deprecated aliases `academic` and `default`). It is the research-paper-to-slides skeleton: turn a paper, report, or study into an evidence-forward deck for a business or executive reader. To make a different structure the default, repoint the "Default structure" marker in the intro above and in Step 0.5 of `SKILL.md`; nothing else needs to move.

Register defaults to `business` here, as everywhere: translate or gloss the source's domain vocabulary for a non-specialist reader (Step 0.5 register axis in `SKILL.md`). The structure is academic in shape; the register is not. Structure and register are separate axes, and this default pairs an academic structure with a business register. A keep-the-jargon deck for a specialist room is `register=technical` on this or any structure.

**Rhetoric balance: 50% logos / 25% ethos / 25% pathos.** Logos-forward: the findings and the evidence drive the deck. Ethos is meaningful because the skeleton puts Methodology and Limitations on their own slides (process and candor shown). Pathos is moderate, carried by the Application/implications slide (why the reader should care).

### Structural skeleton (8+ slides; one slide per distinct finding, no hard cap)

1. **Title slide** (dark accent, SlateNavy)
2. **Methodology slide, when appropriate** (titled to match the source, for example "Population and Methodology"). This is the first slide after the title; do not insert a hook, agenda, or definition slide ahead of it. **Skip when the source is not an empirical study, when the methodology is trivial or beside the point, or when the source is opinion/news/blog content.** Use judgment. **Structure: follow the Methodology Slide Template in `SKILL.md` Content Requirements** (two-column, seven-element layout with DeepTeal bold labels). The template's structure is itself the visual treatment; do not substitute a free-form flow diagram or single-column bullet list.
3. **Summary slide, when appropriate**, titled "Summary". A preview-style slide that summarizes the conclusions drawn from the source, modeled on the structured summary's Conclusions section. The Summary slide goes near the front of the deck (audience sees the conclusions first, then the evidence); the Conclusions slide at the back closes the deck (same content, restated after the findings). Skip the Summary slide when the source has no clear conclusions, when the conclusions are too granular to preview meaningfully, or when the source is short enough that previewing duplicates the closing Conclusions slide.
4. **Core findings** (one slide per distinct finding in the source). A finding is *distinct* when its magnitude, country, mechanism, or time period differs from every other finding. Count the distinct findings in the source's results section before slide writing; that count is the floor for the findings section. Compressing distinct findings into shared slides is a defect, not the design. One finding per slide, visual-first. **Diagnostic signal:** if the resulting deck has fewer than 8 slides total for an academic paper, working paper, long-form report, or whitepaper, that is a signal of probable under-rendering, not a target. Inspect every Step 0.7 Compress decision and restore distinct findings as their own slides. The deck size is whatever the content requires; the signal is "too few for the source," not "below a numerical floor."
5. **Application or implications** (case example, exercise connection, or practical interpretation)
6. **Limitations slide, when appropriate**, titled "Limitations". Include when the source has a substantive Issues or limitations section (for example, from `../summary-academic/SKILL.md` or `../summary-general/SKILL.md`). Format: 2-3 strongest objections, each as "what a skeptic would say / why the concern is reasonable / how it is addressed or acknowledged" (the Limitations Slide Template in `SKILL.md` Content Requirements).
7. **Conclusions slide, when appropriate**, that summarizes the key conclusions, modeled on the structured summary's Conclusions section. Distinct from Key Takeaways: Conclusions reflects what the source concluded; Takeaways reflects what the audience should remember. Skip when the source has no clear conclusions, when conclusions are obvious from the findings already shown, or when the takeaways slide already covers them. When both a Summary slide (position 3) and a Conclusions slide exist, the two are restatements of the same content bracketing the findings; that is intentional, not a defect.
8. **Key Takeaways** (numbered list, white background)
9. **Closing** (dark accent, one sentence the audience should remember)

**No facilitator prompts.** Do not include `\textit{Discuss:}`, `\textit{Activity:}`, `\textit{Reflect:}`, `\textit{Think about:}`, `\textit{Ask the room:}`, or similar facilitator/discussion prompts on any slide. These belong only in the `teaching` (or `lecture`) structure, which loads its own template below. An `mba`/default deck is read by the audience directly and has no facilitator.

### Rules

- Devil's Advocate: carried by the Limitations slide (skeleton item 6); no separate Devil's Advocate slide
- Code blocks: include only when the source itself is about code or technical workflows
- Narrative arc: Methodology and Summary first, then evidence; do not open with a definition or agenda slide

---

## Business School Teaching

**Primary examples:** undergraduate business courses, MBA electives and cores, Executive MBA, and executive education. Covers all flavors of business education.

Business school students, typically with some professional context. Ethos is low because credibility is established by position; students aren't evaluating the instructor, they're learning. High pathos through cases, applications, and career relevance. Moderate logos through evidence, frameworks, and data visualizations. Visual-first: default to charts and diagrams over bullet text.

The invocation should specify the student level (undergraduate, MBA, EMBA, exec ed) and institution when relevant. Use that context to tune within the pattern; do not change the rhetoric balance or structural template.

### Level tuning (within 45/15/40 envelope)

| Level | Pathos tilt | Density | Slide count | Notes |
|---|---|---|---|---|
| Undergraduate | Higher (career entry, identity formation) | Lower | 12-16 | More foundational context; longer setup for business concepts students may not have seen yet |
| MBA | Middle (mid-career, strategic framing) | Middle | 12-16 | Career stage and strategic lens both land; case-driven |
| EMBA | Lower pathos, higher applied logos | Higher | 10-14 | Senior professionals; pattern matching; skip primers; assume operational experience |
| Exec ed | Lower pathos, highest applied logos | Highest | 8-12 | Short format; one actionable takeaway; delivery-focused |

### Structural template (10-18 slides)

1. **Title slide** (dark accent, SlateNavy)
2. **Opening hook**: surprising finding, paradox, or concrete problem. NOT an agenda or definition.
3. **Context/stakes**: why this matters for these students given their level and career stage
4. **Core findings** (4-8 slides): each slide presents one finding visually. Sequence: narrative/application first, then framework/technical
5. **Application**: case example or exercise connection
6. **Implications**: what this means for practice
7. **Limitations and Critique** (if source has Issues section): 2-3 strongest objections
8. **Key Takeaways**: numbered list, white background
9. **Closing** (dark accent): one sentence the student should remember

### Rules

- Devil's Advocate: include when source material has an Issues section
- Code blocks: include when teaching about AI tools or technical workflows
- Narrative arc: Narrative then Application then Visual then Technical (never open with definitions)

---

## Faculty Development

**Primary examples:** faculty workshops (50-75 attendees), online sessions (15-25), one-on-one coaching.

Peers, not students. Ethos matters: faculty are evaluating whether the methods are credible and transferable to their own teaching. Show what works through specific examples and survey data. Pathos through shared frustration (time constraints, student resistance, institutional inertia) and shared aspiration (better teaching outcomes).

### Structural template (12-20 slides)

1. **Title slide**
2. **Opening**: a specific result from teaching or from a survey. NOT "why AI matters."
3. **The problem faculty face**: validate the frustrations (time, uncertainty, institutional barriers)
4. **What was tried** (3-5 slides): specific methods, tools, and results. Show the work.
5. **What the data shows** (2-3 slides): findings, student outcomes, adoption metrics
6. **How to start** (3-4 slides): practical steps faculty can take this semester
7. **Limitations and open questions**: what hasn't worked, what is still being figured out
8. **Key Takeaways**
9. **Closing**: one actionable commitment

### Rules

- Devil's Advocate: include (faculty audiences are skeptical by nature)
- Code blocks: include when demonstrating AI tool workflows
- Density: higher than Business School Teaching; faculty take notes differently
- Progressive revelation: permitted (`\pause`) for live demonstrations

---

## Professional Audience

**Primary examples:** advisory boards (75 min), corporate partner forums (20-30 min plus optional breakout).

Senior executives, advisory board members, corporate partners. Decision-makers who hire your graduates and advise on program direction. They want bottom-line findings and organizational relevance, not academic methodology. The archetype is a paradox or counterintuitive headline finding, evidence for why, and what leaders do differently.

### Structural template (10-15 slides)

1. **Title slide**
2. **The paradox or headline finding**: one surprising number, centered, no decoration
3. **Evidence** (3-5 slides): data visualizations showing the pattern. Charts over tables. One finding per slide.
4. **Why it happens** (2-3 slides): organizational barriers framed in business terms, not academic terms
5. **What leaders do differently** (1-2 slides): actionable interventions
6. **Discussion prompt** (if format includes breakout): one question for table discussion
7. **One actionable takeaway** (closing): not "questions?"

### Rules

- Devil's Advocate: optional (depends on whether the talk makes a claim or reports findings)
- Code blocks: never (this audience does not write code)
- Narrative arc: open with a surprising finding or paradox, not a literature review
- Closing: one actionable takeaway, not "questions?"
- Keep under 15 slides; these audiences have short time slots and high expectations per minute

---

## Consulting Workshop

**Primary examples:** board education programs (90 min, 100+ board members), corporate half-day workshops.

Interactive, hands-on, exercise-based. High pathos through realistic scenarios participants recognize from their professional roles. Ethos is partially established by the hiring organization. Logos is enough evidence to be credible but not academic. Many participants may have zero AI experience.

### Structural template (8-15 slides)

1. **Title slide**
2. **Why this matters for you** (1-2 slides): framed for the specific audience's role (board governance, team leadership, etc.)
3. **AI primer** (1-2 slides): just enough context for participants to use the tools. Prompting basics, confidentiality boundaries.
4. **Exercise setup** (1-2 slides): scenario description, QR code to a shared document, instructions
5. **[Exercise happens: no slides needed during table work]**
6. **Debrief** (2-3 slides): one per scenario or theme. Denser than setup slides; capture what was learned. AI strengths vs. where human judgment is essential.
7. **Synthesis** (1-2 slides): principles that emerged from the exercise
8. **Closing**: one takeaway, resources for continued learning

### Rules

- Devil's Advocate: built into the exercise debrief (AI strengths vs. where human judgment is essential)
- Code blocks: never (participants use AI through chat interfaces, not code)
- Slides support spoken delivery: minimal text, maximum visual anchoring
- Exercise scaffolding: QR codes, shared document references, starter prompts on slides
- Debrief slides are denser than setup slides

---

## Working Deck

**Primary examples:** course planning, skill development, internal collaboration.

For your own use and for collaborators. Document choices and rationale. Preserve uncertainty: flag what's unverified with a consistent visual marker. More detail and text density acceptable. Date everything. Include backup or appendix slides. Not meant for live presentation.

### Structural template (any length)

No fixed structure. Organize by topic or decision sequence. Use `\appendix` for backup material.

### Rules

- Devil's Advocate: not needed (this is a thinking tool, not a performance)
- Code blocks: include when documenting technical workflows
- Density: highest of all contexts; information retrieval is the goal
- Assertion titles: still required (they carry the argument when revisited later)
- Date every slide or section
- Flag uncertainty: use a consistent visual marker (e.g., `\colorbox{WarmAmber!20}{\small ?}` next to unverified claims)
- Include the "why" behind choices, not just the "what"

# Domain-Specific Deck Patterns

Audience-specific structural templates for the beamer skill. Each pattern specifies slide count range, density guidelines, rhetoric balance (logos/ethos/pathos), whether to include a Devil's Advocate slide, structural template, and audience-specific rules.

---

## Rhetoric Balance Reference

The logos/ethos/pathos percentages do not allocate slides to categories. They control the *tone and framing* of every slide: what comes first (sequencing), how findings are introduced (framing), and what gets a full slide vs. a footnote (emphasis).

- **Logos (Logic):** "Does this make sense?" Data, evidence, frameworks, causal reasoning.
- **Ethos (Credibility):** "Why should I trust this person?" Methodology, limitations acknowledged, Devil's Advocate, process shown.
- **Pathos (Emotion):** "Why should I care?" Stories, applications, career relevance, human impact, frustration validated.

| Context | Logos | Ethos | Pathos | Slides |
|---|---|---|---|---|
| **Business school teaching** (default) | 45% | 15% | 40% | 10-18 |
| **Faculty development** | 35% | 35% | 30% | 12-20 |
| **Professional audience** | 40% | 25% | 35% | 10-15 |
| **Consulting workshop** | 30% | 25% | 45% | 8-15 |
| **Working deck** | 55% | 25% | 20% | any |

---

## Business School Teaching (Default)

**Primary examples:** undergraduate business courses, MBA electives and cores, Executive MBA, and executive education. Default pattern when no audience is specified. Covers all flavors of business education.

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

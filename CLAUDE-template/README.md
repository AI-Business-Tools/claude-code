# CLAUDE.md Template: Setup Guide

This folder contains a starter `CLAUDE.md` file for Claude Code. Copy it to your project directory and customize each section.

## What CLAUDE.md Does

Claude Code reads `CLAUDE.md` at the start of every session. It is the "rules" layer of the four-layer model: persistent instructions that apply to everything Claude does in your project. Without it, every session starts from a blank slate.

## How to Use This Template

1. Copy `CLAUDE.md` to the root of your project directory
2. Replace all `[BRACKETED TEXT]` with your own details
3. Remove sections you do not need
4. Delete the HTML comments once you are done customizing

## Section-by-Section Guide

### User Identity

Tell Claude who you are and what you do. This is not vanity; it changes how Claude responds. A data scientist gets different explanations than a first-year MBA student. Include your role, your audience, and any working patterns Claude should know about (e.g., "I work across multiple sessions on the same project").

### Global Writing Standards

Rules that apply to every piece of text Claude generates. These prevent the most common corrections: inconsistent formatting, wrong citation style, unwanted tone. Start with a few rules you care about and add more as you discover patterns you need to correct.

### Workflow Discipline

How Claude should approach tasks. The two most important rules here are "diagnose and propose, then wait" (prevents Claude from making changes without approval) and "backup before major changes" (prevents loss of work). Add rules that match how you want to collaborate.

### Skill Routing Rules

If you install skills from this repository, add routing rules so Claude knows which skill to use for each type of request. Without routing rules, Claude may produce ad-hoc output instead of using the skill's quality-gated workflow.

### Delivery Gates

Quality checks that apply to all output. These catch recurring problems: overwriting files without backup, fixing one instance of a defect while leaving others, shipping without re-reading after structural edits. Start with the four included gates and add your own as you discover failure patterns.

### Handoff Protocol

The mechanism for carrying context across sessions. When you finish a session, tell Claude to "write a handoff." When you start the next session, type "resume." The full protocol is available in the [handoff-resume](../skills/handoff-resume/) skill.

### Build Directory Convention

A naming convention for working files (LaTeX intermediates, PDF splits, conversion scripts). Keeps deliverables clean by isolating build artifacts in a predictable location.

## What to Do Next

After customizing the template:

1. Install any skills you want from the [skills catalog](../skills/)
2. Copy the corresponding [style guides](../style-guides/) if the skill references them
3. Start a Claude Code session in your project directory and try a task
4. When Claude does something you want to correct, correct it; then save the correction as a feedback memory so it persists

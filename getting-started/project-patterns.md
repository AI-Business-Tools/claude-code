# Project Patterns for Claude Code

Optional companion to the [getting-started guide](README.md). That guide covers the few habits you need to begin. This file collects fuller patterns: folder layouts, naming conventions, a project state file, and sample files you can copy or point Claude Code at. None of it is required. Adopt what fits the way you work, and ignore the rest.

You can also point Claude Code at this file and ask it to set a project up this way for you. See the last section.

## A folder per project

Keep everything for one piece of work in a single folder, and start Claude Code from inside it so it can see the whole thing.

A layout that scales well:

```
my-project/
  CLAUDE.md              project instructions Claude reads every session
  CLAUDE.local.md        rolling state: what is done, what is next (optional)
  sources/               inputs you were given (PDFs, data, references)
  my-project_build/      working files and intermediates Claude generates
  (your finished deliverables sit at the top level, easy to find)
```

The names are a suggestion, not a rule. The point is that inputs, working files, and finished output each have a predictable home, so you and Claude can both find things in a later session.

## CLAUDE.md: instructions Claude reads every session

A file named CLAUDE.md at the top of a project is loaded automatically every time you start Claude Code in that folder. It is where you put anything you would otherwise re-explain each session. A short, useful CLAUDE.md covers:

- **What this project is.** One or two sentences of context.
- **How to name and place files.** Where output goes, what naming pattern to use.
- **Standards to follow.** Writing style, formatting rules, things to avoid.
- **How you want Claude to work.** When to ask before acting, when to just proceed.

A minimal starting point:

```markdown
# Project: [name]

## What this is
[One or two sentences.]

## Output
- Save deliverables to the top level of this folder.
- Name new files with a YYYY-MM-DD prefix and a short descriptive name.
- Keep working files in [project]_build/.

## Standards
- [Your writing or formatting rules.]
- Ask before overwriting an existing file.
```

The repository's [CLAUDE-template](../CLAUDE-template/CLAUDE.md) is a longer, structured example you can copy and trim.

## A project state file (CLAUDE.local.md)

For work that spans several sessions, a second file is useful: a rolling record of what has been done and what is next. By convention people keep this in a file named CLAUDE.local.md and use it for working notes they do not want shared or version-controlled (the name is commonly added to .gitignore). Claude Code loads it automatically alongside CLAUDE.md.

Keep it short. After a working session, a few lines is enough:

```markdown
## 2026-01-15 - [what you worked on]
- Summary: [one or two sentences on what changed].
- Status: [done / in progress / blocked].
- Next: [the next concrete step].
```

This pairs naturally with the [handoff-resume](../skills/handoff-resume/) recipe, which formalizes the same idea: end a session by writing down where you are, and start the next by reading it back.

## Naming conventions that keep sessions coordinated

When more than one session, or more than one machine, touches the same project, consistent names prevent confusion:

- **Date-prefix new files** you create where there is no other convention: `2026-01-15 proposal draft.docx`. They sort in order and the date is visible.
- **Use descriptive names, not generic ones.** `q1-board-deck.md` beats `notes.md`.
- **Name working folders predictably.** A common pattern is to suffix the project name: a folder named `q1-report/` gets a working subfolder `q1-report_build/`. Predictable suffixes mean any session can find the working files.

## Back up before overwriting

A habit worth keeping: before regenerating or rebuilding a file that already exists, save a copy of the current version first, named with a timestamp (for example, `report 2026-01-15.docx`). Minor edits do not need it; full rebuilds and format conversions do. It costs a few seconds and prevents the occasional irreversible mistake. You can write this rule into your CLAUDE.md so Claude Code does it for you.

Version history with Git (see [git-sync](../skills/git-sync/)) gives you this automatically for tracked files; a manual timestamped copy covers everything else, including large binaries that Git is not tracking.

## Let Claude Code apply these for you

You do not have to set this up by hand. Open Claude Code in a new or existing project folder, point it at this repository, and say something like:

> Read getting-started/project-patterns.md and set this folder up that way: create a CLAUDE.md and a CLAUDE.local.md from the samples, ask me what this project is and how I want files named, and create a working subfolder.

Claude Code will draft the files from your answers and show them to you before saving.

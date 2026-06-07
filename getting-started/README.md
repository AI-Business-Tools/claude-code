# Getting Started with Claude Code

This guide is for someone who already uses Claude in the browser (the chat at claude.ai, and maybe Cowork) and wants to add Claude Code. You do not need to be a programmer. If you have never opened a terminal, the steps below walk you through it. By the end you will know what Claude Code adds beyond chat and Cowork, how to install it on a Mac or a Windows PC, and how to set up your first project so the tool works the way you do.

You can read this yourself. You can also, once Claude Code is installed, point Claude Code at this guide and have it walk you through the setup. See "Let Claude Code set you up" near the end.

## What Claude Code adds, and when to use which

All three are Claude. They differ in how much they do on their own, and in how much you can shape and reuse how they work.

**Claude chat (claude.ai).** A conversation in your browser. You bring it text and questions; it answers. It does not reach into the files on your computer. Best for thinking something through, drafting, and quick questions.

**Cowork.** Anthropic's desktop agent. You give it a goal and a folder, and it works through a multi-step task on your own computer, reading and editing your local files and applications, and hands back a finished deliverable. No coding required. Best for handing off a self-contained job and letting Claude run it start to finish.

**Claude Code.** Also works directly in your local files, but it is the tool for building a setup you control and reuse. On top of doing the work, it lets you write your standards once in a file it reads every session, turn recurring tasks into reusable "skills," keep version history of everything you build, and run the same process the same way every time. Best when you want a structured environment you own, not just one job done.

Reach for chat to think and draft, Cowork to hand off a self-contained job and get back a finished file, and Claude Code when you want to build, control, and reuse your own standards, skills, and version-controlled setup.

Like Cowork, Claude Code works in your own folders and does multi-step work on its own. What it adds is control and reuse:

- **It remembers your standards.** A file named CLAUDE.md in a project states your rules once, and Claude reads it every session.
- **It turns recurring work into skills.** Tasks you do repeatedly become workflows you trigger by name and run the same way every time. More on skills below.
- **It keeps version history.** With Git set up (see below), every change to your skills and standards is tracked and reversible.
- **You see and approve each step.** It runs in the terminal or your editor and asks permission before it edits a file or runs a command, so you stay in control.

## Install Claude Code

Claude Code requires a paid Claude plan (Pro, Max, Team, or Enterprise) or API billing through the Anthropic Console; the free Claude.ai plan does not include it. You install it once, then start it by typing `claude` inside a folder.

### Mac

1. Open the Terminal app (press Cmd+Space, type "Terminal," press Return).
2. Paste this and press Return:
   ```
   curl -fsSL https://claude.ai/install.sh | bash
   ```
3. When it finishes, close and reopen Terminal.

### Windows

1. Open PowerShell (press Start, type "PowerShell," press Return).
2. Paste this and press Return:
   ```
   irm https://claude.ai/install.ps1 | iex
   ```
3. When it finishes, close and reopen PowerShell.

On Windows, it also helps to install Git for Windows from [git-scm.com](https://git-scm.com). It lets Claude Code run a wider set of commands, and you will want Git anyway for the version-history step further down.

This native installer keeps itself up to date, so you install once and do not have to think about updates. If you already manage software with Homebrew on a Mac (`brew install --cask claude-code`) or WinGet on Windows (`winget install Anthropic.ClaudeCode`), those work too, but you have to update them manually.

Prefer not to use a terminal at all? Claude Code also comes as a desktop app for Mac and Windows, as extensions for VS Code and JetBrains if you use those, and as a browser version at [claude.ai/code](https://claude.ai/code) that runs in the cloud with no install. The terminal is the most complete starting point and is what the rest of this guide assumes.

### Start it the first time

1. Make a folder for your work and move into it. In your home directory, this creates one named "my-project" and enters it:
   ```
   mkdir my-project
   cd my-project
   ```
   (If you already made a folder in Finder or File Explorer, use `cd` with its name instead.)
2. Type `claude` and press Return.
3. The first time, it opens your browser to log in with your Claude account. Log in once; it remembers you after that.
4. You are now in a Claude Code session. Ask it something in plain language, then type `/exit` when you are done (pressing Ctrl-C twice also exits).

Claude Code asks permission before it edits a file or runs a command, so you can see what it proposes and approve or decline.

Current install details and troubleshooting: [code.claude.com/docs](https://code.claude.com/docs).

## Set up your first project

Claude Code does its best work when each project lives in its own folder and that folder tells Claude how you want it to work. A few habits go a long way:

- **One project, one folder.** Keep everything for a piece of work (sources, drafts, and output) in a single folder, and start Claude Code from inside it. Claude can see the whole folder, so it keeps its work consistent.
- **Add a CLAUDE.md.** A plain-text file named CLAUDE.md at the top of the folder is where you write your instructions for that project: what it is, how you want files named, and standards to follow. Claude Code reads it automatically every session, so you set your preferences once instead of re-explaining them. The repository's [CLAUDE-template](../CLAUDE-template/CLAUDE.md) is a starting point you can copy and edit.
- **Give working files a predictable home.** Decide where drafts, intermediate files, and output go, and name things consistently (a date prefix, a clear descriptive name). Predictable names mean Claude, and you, can find things later.
- **Keep a record of changes.** Once a project is underway, version history is worth setting up so you can see what changed and undo a bad edit. See the next section.

Want a fuller set of folder layouts, naming conventions, a project state file, and a sample CLAUDE.md to copy or point Claude Code at? See [project-patterns.md](project-patterns.md) in this folder. It is optional; the habits above are enough to start.

## Add version history and session continuity

Two short setups make multi-session work much smoother, especially once you are using two computers. Both are documented as ready-to-use recipes in this repository.

- **Version history with Git.** Turn the folder Claude Code keeps its configuration in into a versioned repository, so you have a history of every change to your skills and standards, can undo precisely, and can keep two computers in sync. Recipe: [git-sync](../skills/git-sync/). You can point Claude Code at it and let it do the setup.
- **Handoffs and resume.** A simple protocol for ending a session with a short written summary, so the next session, or the next day, picks up exactly where you left off instead of starting cold. Recipe: [handoff-resume](../skills/handoff-resume/).

## What skills are

A skill is a saved, reusable workflow. When you find yourself pasting the same multi-step instructions into Claude again and again ("take this PDF, pull out the key points, draft slides, and check them against these rules"), you can write those steps once as a skill. After that, a short request triggers the whole process, with your quality checks built in.

Mechanically, a skill is a folder under `~/.claude/skills/` with a file named SKILL.md describing what to do. Claude Code loads it only when it is relevant, so you can keep many skills without slowing anything down. You trigger a skill by name (for example, typing `/skill-name`) or by asking for the task it handles.

For business and knowledge work, skills are most useful for tasks you repeat: a slide-building process, a document summarizer, a decision pressure-test, and a writing-voice layer that keeps everything sounding like you.

The skills in this repository are working examples you can read for ideas or adopt directly. Browse the [skills catalog](../skills/) to see how they are built. A few that need no coding background to use: [writing-voice-guide](../skills/writing-voice-guide/) (teach Claude to write in your voice), [summary-general](../skills/summary-general/) (turn an article, video, or podcast into a clean summary), and [ai-council](../skills/ai-council/) (pressure-test a decision through five distinct advisors).

## Let Claude Code set you up

Once Claude Code is installed, you do not have to do the rest by hand. Open Claude Code in a folder, point it at this repository (clone it, or give Claude the file's web address), and say something like:

> Read getting-started/README.md and getting-started/project-patterns.md, help me set up my first project folder with a CLAUDE.md, and walk me through adopting the git-sync and handoff-resume recipes.

Claude Code can create the project folder, draft a starting CLAUDE.md from your answers, set up version history, and explain the daily routine, asking your approval at each step.

## Where to go next

- [CLAUDE-template](../CLAUDE-template/CLAUDE.md): a starting CLAUDE.md to copy and customize.
- [project-patterns.md](project-patterns.md): optional, fuller folder and naming patterns with sample files.
- [Skills catalog](../skills/): every skill in this repository, grouped by purpose.
- [methodology.md](../methodology.md): the design thinking behind a structured AI environment.
- [Style guides](../style-guides/): formatting conventions for slides and documents.

# Narrated Video

Turn a slide deck into a short narrated video with captions, from the deck alone or with speaker notes, an outline, or a transcript of the talk.

## Problem

A presentation often needs to reach people who did not attend it: a team that missed the meeting, a client in another time zone, or colleagues reviewing it later. Recording narration over the slides yourself takes a quiet room and several takes, and each correction means recording again.

## Approach

Claude Code, or Codex, writes the narration from your deck and whatever else you have: speaker notes, an outline, or a transcript of the talk as you delivered it. You read and approve that script before the skill records any audio, because every later step reads from it. Google's Gemini text-to-speech service then reads it aloud, one sentence at a time, and the skill assembles the video with ffmpeg, a free video tool.

The captions come from the approved script rather than from a program listening to the audio, so the captions spell names and figures exactly as you approved them, and each caption stays on screen while its sentence plays. Because each sentence is a separate recording, a correction re-records only the sentence that changed.

## Steps

1. **Set up the tools and the Gemini key.** The skill checks Python, ffmpeg, and four Python packages, installs what is missing (you install Homebrew on a Mac and Python on Windows), gives the steps for storing your Gemini key, and voices one test sentence to confirm the key works.
2. **Prepare the deck and any notes.** You export a copy of the deck as a PDF after removing hidden and backup slides and anything else the video should not show. Optional: speaker notes from the `.pptx`, an outline, or a transcript. Before the agent reads a transcript, a program removes its time stamps, replaces each speaker label it recognizes with Me or Other, and removes those speakers' names and any names you list. The agent asks how many people spoke and compares that with the number the program found, since the program can miss a speaker, and you read the cleaned version first.
3. **Confirm the slides and draft the script.** The skill makes one image per slide from the PDF, and you confirm the count. The agent then drafts one scene per slide, at about 150 spoken words a minute, with numbers written as they are said and nothing your deck and material do not support, and a separate check flags unsupported claims.
4. **Approve the script.** You edit the script where you want and approve it; the skill records none of it before you do.
5. **Choose the voice and build the video.** You compare three voices on one scene, and the skill records the script, one clip per sentence. It then builds caption files in `.srt` and `.vtt`, the formats video sites accept, and an MP4 with the captions on a band below each slide, with the narration's loudness evened from scene to scene. A later change re-records only the sentences it changes.

## Usage

In the folder that contains the deck, ask in your own words:

- "Make a narrated video from deck.pdf"
- "Turn my presentation into a three-minute video with captions"
- "Use the speaker notes in deck.pptx for the narration"

**Suited to**
- A project report, a campaign review, or a briefing for people who missed a meeting
- A recorded version of a talk you gave, built from its transcript

**Not suited to**
- A software demonstration, which calls for a screen recording
- A talk whose value is the speaker on camera, such as a pitch or a personal story
- A copy of any real person's voice, which this skill never makes; it uses Google's stock voices only

## Requirements

- Claude Code, or Codex, on a Mac or a Windows computer
- On a Mac, Homebrew (https://brew.sh)
- On Windows, the agent running in Windows itself (PowerShell or Git Bash), not inside WSL (the Windows Subsystem for Linux)
- On Windows with Codex, administrator permission, which Windows asks for the first time Codex sets up its sandbox
- Python 3.9 or later, and ffmpeg; the skill checks for both and installs what is missing, except Homebrew on a Mac and Python on Windows
- A Gemini API key from Google AI Studio (https://aistudio.google.com/apikey), created with a personal Google account; a university or employer account may block AI Studio

## Installation

**Codex.** Codex opens an ordinary folder (one not tracked by Git) as read-only, and in that mode it cannot run the download below, so start it in Auto mode in the folder that contains the deck: `codex --sandbox workspace-write --ask-for-approval on-request`. In Auto mode Codex asks before any command that reaches the internet or writes outside that folder: the download below, the package and ffmpeg installs, the skill's own copy of its Python packages, and every voice request. Approve each request when Codex asks. If the setup check reports the key missing under Codex, look at `[shell_environment_policy]` in `~/.codex/config.toml`: an `exclude` or `include_only` list there, or an `inherit` value other than `"all"`, can keep `GEMINI_API_KEY` from Codex's commands.

Ask Claude Code, or Codex:

> Install the narrated-video skill from https://github.com/AI-Business-Tools/claude-code/tree/main/skills/narrated-video into my personal skills folder.

The skill needs its whole folder, `SKILL.md` and `scripts/`, at `~/.claude/skills/narrated-video/` for Claude Code, or at `~/.agents/skills/narrated-video/` for Codex. These are the commands the agent runs to put it there, and you can run them yourself; for Codex, use them with `.agents` in place of `.claude`.

On a Mac (Terminal):

```
curl -L -o "$HOME/Downloads/claude-code-main.zip" "https://github.com/AI-Business-Tools/claude-code/archive/refs/heads/main.zip"
tar -xf "$HOME/Downloads/claude-code-main.zip" -C "$HOME/Downloads"
mkdir -p "$HOME/.claude/skills"
cp -R "$HOME/Downloads/claude-code-main/skills/narrated-video" "$HOME/.claude/skills/"
```

On Windows in Git Bash, where Claude Code runs its commands when Git for Windows is installed, the same four commands work with the second one changed to use Windows' own `tar`, since the `tar` that comes with Git Bash cannot open a zip file:

```
"/c/Windows/System32/tar.exe" -xf "$HOME/Downloads/claude-code-main.zip" -C "$HOME/Downloads"
```

On Windows in PowerShell:

```
$ProgressPreference = "SilentlyContinue"
Invoke-WebRequest -UseBasicParsing -Uri "https://github.com/AI-Business-Tools/claude-code/archive/refs/heads/main.zip" -OutFile "$env:USERPROFILE\Downloads\claude-code-main.zip"
Expand-Archive -Path "$env:USERPROFILE\Downloads\claude-code-main.zip" -DestinationPath "$env:USERPROFILE\Downloads" -Force
New-Item -ItemType Directory -Force -Path "$env:USERPROFILE\.claude\skills" | Out-Null
Copy-Item -Recurse -Force "$env:USERPROFILE\Downloads\claude-code-main\skills\narrated-video" "$env:USERPROFILE\.claude\skills\"
```

Where the agent does not find the skill, start a new session. The same commands update the skill to a newer version.

The first run sets up the rest: the skill checks the computer, installs the Python packages, and gives the steps for storing your Gemini key. You type the key-storing commands yourself, in your own terminal window, so the key never enters the conversation; the commands store it in the Mac Keychain or in your Windows account settings, never in a file. The skill's programs read it from there, so run the check again after storing it; where the check still reports it missing, restart the agent.

## Output

Each video has its own folder:

- `video.mp4`: 1920 by 1080, H.264 video with AAC audio, which phones and web browsers play
- `captions.srt` and `captions.vtt`: the captions, for sites that accept a captions file
- `script.md`: the approved narration, one scene per slide
- `slides/` and `audio/`: the slide images and the recorded sentences, kept so a later correction re-records only what changed
- `samples/`: one scene read in each voice you compared
- `voice-test.wav`: the test sentence from the setup check

## Cost and Privacy

- **Paid tier, recommended:** you link a billing account to your key in AI Studio, and Google does not use what it receives to improve its products. Google prices the audio by length, so a three-minute video costs $0.04 to $0.08 at Google's published prices. The skill reports an estimate before recording and the cost of each recording afterward.
- **Free tier, the fallback:** no charge and no billing account. Google may use what it receives on the free tier to improve its products, so send nothing confidential there. The free tier also caps requests each day, at a limit AI Studio shows, and a three-minute video sends about 34 requests (one per sentence, plus the voice samples and the setup test), so the cap can stop a recording partway. Run the same request the next day, or once you link billing, and the recording continues where it stopped.
- **Data each service receives:** the agent, Claude Code or Codex, reads your slides and material to write the script, as it reads any file you work on with it. Google receives only the approved script's words, for the voice.

## Design Rationale

**You approve the script before the skill records any of it.** Every later step reads it, it is the only content sent to the voice service, and a change costs least before any audio exists. The approval is a line in the script file (`Status: approved`), which the recording program checks before it sends anything.

**One clip per sentence.** Each caption's timing comes from its own sentence's recording, so no speech-recognition program is needed, and a correction re-records only what changed.

**The captions come from the script.** A speech-recognition program can mishear a name or a figure; the script contains the words exactly as approved.

**The captions sit on a band below the slide.** They never cover a chart or a figure. Python draws them, so they work with any ffmpeg build.

**A program cleans the transcript before any AI reads it.** An instruction to an AI to ignore a name arrives too late once the name is in the conversation, so a program removes names first.

**Few installs.** The slide images come from the PDF through PyMuPDF, a PDF library that installs with pip, Python's package tool, on a Mac or Windows, so the skill needs no PowerPoint, Keynote, or LibreOffice. The voice requests use Python's standard library, so they need no Google software beyond the key.

**The deck alone is enough.** Notes, an outline, or a transcript add the speaker's own phrasing; without them, the narration follows the slides.

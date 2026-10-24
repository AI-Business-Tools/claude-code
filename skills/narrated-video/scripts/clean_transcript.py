#!/usr/bin/env python3
"""clean_transcript.py: strip a meeting or talk transcript before any AI reads it (step 2).

Usage:
  python3 clean_transcript.py RAW_TRANSCRIPT [--me "Your Name"] [--only-me]
                              [--names NAMES.txt] [--folder VIDEO_FOLDER]

Reads a transcript exported from Zoom, Teams, Otter, or a similar tool (.vtt, .srt, or
.txt) and writes transcript-clean.txt in the video's folder, with:
  - cue numbers, time stamps, and formatting tags removed;
  - speaker labels replaced: the user's own label (--me, as the transcript spells it)
    becomes "Me:", every other speaker becomes "Other:"; without --me, speakers become
    "Speaker 1:", "Speaker 2:", in order of first appearance. Labels are recognized in
    Zoom's "Name:" form (pronouns in parentheses included), Teams' voice tags and
    "Last, First" form, Otter's "Name  0:14" header lines, and names with particles
    ("Ana de la Cruz"); --me matches with or without pronouns and in either name order;
  - every other speaker's name, as their label spells it, replaced with [name] wherever
    it appears in the text, and each part of it (a first name alone, for example);
  - every name listed in NAMES.txt (one per line) replaced with [name] as well;
  - with --only-me, every line but the user's own removed.

The script prints counts only, never names or transcript text, so running it puts
none of the transcript into the conversation. What it cannot catch (a name it was not
given, a client, a figure, a personal detail) the user removes by reading the cleaned
file before any AI reads it.

Exit codes: 0 done; 1 --me was given but no speaker label matched it; 2 the file is
missing or holds no text.
"""

from __future__ import annotations

import argparse
import re
import sys
from collections import Counter
from pathlib import Path

sys.dont_write_bytecode = True      # leave no cache files in the skill's folder
sys.path.insert(0, str(Path(__file__).resolve().parent))
import nv_common as nv  # noqa: E402

TIME = r"(?:\d{1,2}:)?\d{1,2}:\d{2}(?:[.,]\d{1,3})?"
CUE_TIME_RE = re.compile(rf"^\s*{TIME}\s*-->\s*{TIME}.*$")
SPEAKER_TIME_RE = re.compile(rf"^\s*(?P<name>[^\d\s:][^:]{{0,60}}?)\s+\(?{TIME}\)?\s*$")
LEADING_TIME_RE = re.compile(rf"^\s*[\[(]?{TIME}[\])]?\s*[-:]?\s*")
VOICE_TAG_RE = re.compile(r"<v(?:\.[\w.-]+)?\s+([^>]+)>")
TAG_RE = re.compile(r"</?[a-zA-Z][^>]*>")
# A speaker label: "Lee Roe:", "Roe, Lee:" (Teams), "Ana de la Cruz:".
LABEL_RE = re.compile(r"^\s*(?P<name>[A-Za-z][\w.,'\- ]{0,40}?)\s*:\s+(?P<text>\S.*)$")
BRACKET_LABEL_RE = re.compile(r"^\s*\[(?P<name>[^\]\d]{1,40})\]\s*(?P<text>.*)$")
# Pronouns or a role after a display name, directly before the colon or at the end of
# a name: "Lee Roe (he/him):", "<v Lee Roe (Guest)>".
LABEL_PARENS_RE = re.compile(r"^(?P<name>[^:()]{1,60}?)\s*\([^()]{1,30}\)\s*:\s+(?P<text>.*)$")
TRAILING_PARENS_RE = re.compile(r"\s*\([^()]{1,30}\)\s*$")
PARTICLES = "de|da|del|della|di|du|dos|das|la|le|van|von|der|den|ten|ter|bin|ibn|al|el|y"
# One to four capitalized words, allowing name particles and a Teams "Last, First".
NAME_LIKE_RE = re.compile(rf"^[A-Z][\w.,'\-]*(?: (?:[A-Z][\w.,'\-]*|\d+|{PARTICLES})){{0,3}}$")
# Any one to four words of letters, in any case ("ingrid haugen").
WORDS_RE = re.compile(r"^[^\W\d_][\w.,'\-]*(?: [^\W\d_][\w.,'\-]*){0,3}$")
NOT_SPEAKERS = {"note", "question", "answer", "update", "example", "summary", "agenda",
                "action", "next steps", "q", "a"}


def bare_name(name: str) -> str:
    """A display name without its trailing parenthetical: 'Lee Roe (he/him)' -> 'Lee Roe'."""
    return TRAILING_PARENS_RE.sub("", name).strip()


def name_key(name: str) -> tuple:
    """The name's words, lowercased and sorted, so 'Roe, Lee' matches 'Lee Roe'."""
    return tuple(sorted(w.lower() for w in re.split(r"[\s,]+", bare_name(name)) if w))


def segments(raw: str) -> list[tuple[str | None, str, bool, str | None]]:
    """(speaker label or None, text, starts a cue, speaker from the line's context) for
    each line of speech, in order. The context speaker comes from an Otter header line
    or a Teams voice tag, and stands where a 'Words:' opening proves not to be a label."""
    lines = raw.split("\n")
    # A "Name 0:03" line (Otter's form) is a speaker line where that name heads at
    # least two such lines, or where it reads as a name and the file has two or more
    # such lines; a spoken sentence that happens to end in a time stays text.
    heads = Counter()
    for line in lines:
        m = SPEAKER_TIME_RE.match(line.strip())
        if m and len(bare_name(m.group("name")).split()) <= 4:
            heads[bare_name(m.group("name"))] += 1
    total_heads = sum(heads.values())
    # A line directly before a time-range line is a cue identifier (a number, or a
    # code such as Teams writes), never speech.
    cue_ids = {i for i in range(len(lines) - 1)
               if lines[i].strip() and CUE_TIME_RE.match(lines[i + 1].strip())}
    out: list[tuple[str | None, str, bool, str | None]] = []
    skip_block = False
    speaker = None
    cue_start = False
    for i, line in enumerate(lines):
        s = line.strip()
        if not s:
            skip_block = False
            continue
        if skip_block:
            continue
        if s.upper().startswith("WEBVTT") or s.split(" ")[0] in ("NOTE", "STYLE", "REGION"):
            skip_block = True
            continue
        if i in cue_ids or s.isdigit():
            continue
        if CUE_TIME_RE.match(s):
            cue_start = True
            continue
        m = SPEAKER_TIME_RE.match(s)
        if m and not LABEL_RE.match(s):
            head = bare_name(m.group("name"))
            # Otter puts each header after a blank line, so in a file of headers a
            # one-time header in any case ('ingrid haugen  0:14') counts there too.
            after_blank = i == 0 or not lines[i - 1].strip()
            if heads[head] >= 2 or (total_heads >= 2 and (
                    NAME_LIKE_RE.match(head) or (after_blank and WORDS_RE.match(head)))):
                speaker = head
                continue
        v = VOICE_TAG_RE.search(s)
        if v:
            speaker = bare_name(v.group(1))
        s = TAG_RE.sub("", s).strip()
        s = LEADING_TIME_RE.sub("", s).strip()
        if not s:
            continue
        p = LABEL_PARENS_RE.match(s)
        if p:
            s = f"{p.group('name').strip()}: {p.group('text')}"
        m = LABEL_RE.match(s) or BRACKET_LABEL_RE.match(s)
        if m:
            out.append((m.group("name").strip(), m.group("text").strip(), cue_start, speaker))
        else:
            out.append((speaker, s, cue_start, speaker))
        cue_start = False
    return out


def resolve_labels(segs, me: list[str]):
    """Keep a 'Name:' prefix as a speaker label where it is the user's own, labels at
    least two lines, or reads as a name (one to four capitalized words, such as 'Lee Roe',
    'Roe, Lee', 'Ana de la Cruz', or 'Speaker 3'). In a captions file where most cues
    open with a speaker label, a cue that opens with one to four words and a colon is a
    label too, in any case ('ingrid haugen:'). Otherwise the colon belonged to the
    sentence. Returns the segments, the speakers, and the count of lines whose opening
    words looked like a label but were kept as text."""
    counts = Counter(name for name, _, _, _ in segs if name)
    me_keys = {name_key(m) for m in me}

    def accepted(n: str, c: int) -> bool:
        if name_key(n) in me_keys:
            return True
        return n.lower() not in NOT_SPEAKERS and (c >= 2 or bool(NAME_LIKE_RE.match(n)))

    real = {n for n, c in counts.items() if accepted(n, c)}
    real |= {ctx for _, _, _, ctx in segs if ctx}    # Otter headers and Teams voice tags
    cue_starts = [(n, s) for n, _, s, _ in segs if s]
    labeled = sum(1 for n, _ in cue_starts if n in real)
    if cue_starts and labeled >= len(cue_starts) / 2:
        real |= {n for n, _, s, _ in segs if s and n and n.lower() not in NOT_SPEAKERS
                 and WORDS_RE.match(n)}
    fixed, last, doubtful = [], None, 0
    for name, text, _, context in segs:
        if name and name not in real:
            # The opening words were not a label: the line belongs to the speaker its
            # context names (an Otter header or a Teams voice tag), else the one before.
            text, name = f"{name}: {text}", (context or last)
            doubtful += 1
        fixed.append((name, text))
        last = name if name else last
    real |= {n for n, _ in fixed if n}
    return fixed, real, doubtful


def name_parts(name: str) -> list[str]:
    name = bare_name(name)
    parts = [name] + [p for p in re.split(r"[\s.,\-]+", name) if len(p) >= 3]
    if "," in name:                      # "Roe, Lee" is also said as "Lee Roe"
        last, _, first = name.partition(",")
        parts.append(f"{first.strip()} {last.strip()}")
    return sorted(set(p for p in parts if p), key=len, reverse=True)


def main() -> int:
    ap = argparse.ArgumentParser(description="Strip a transcript before an AI reads it.")
    ap.add_argument("transcript", help="the raw transcript file (.vtt, .srt, or .txt)")
    ap.add_argument("--me", action="append", default=[],
                    help="your speaker label as the transcript spells it (repeatable)")
    ap.add_argument("--only-me", action="store_true", help="keep only your own lines")
    ap.add_argument("--names", help="a text file of other names to remove, one per line")
    ap.add_argument("--folder", help="the video's folder (default: the current folder)")
    args = ap.parse_args()

    folder = nv.folder_arg(args.folder)
    src = Path(args.transcript).expanduser()
    if not src.is_file():
        raise nv.Stop(f"no transcript found at {src}", 2)
    if src.suffix.lower() in (".docx", ".pdf"):
        raise nv.Stop("save the transcript as a .txt or .vtt file first (most meeting tools "
                      "offer one), then run this again.", 2)
    if args.only_me and not args.me:
        raise nv.Stop("--only-me needs --me, your speaker label as the transcript spells it.", 2)

    args.me = [bare_name(m) for m in args.me]
    segs, speakers, doubtful = resolve_labels(segments(nv.read_text(src)), args.me)
    if not segs:
        raise nv.Stop("no transcript text was found in that file.", 2)

    me_keys = {name_key(m) for m in args.me}
    mine = {s for s in speakers if name_key(s) in me_keys}
    others = [s for s in speakers if s not in mine]
    order = list(dict.fromkeys(n for n, _ in segs if n))

    def label(name):
        if name is None:
            return None
        if args.me:
            return "Me" if name in mine else "Other"
        return f"Speaker {order.index(name) + 1}"

    remove = []
    for o in others:
        remove += name_parts(o)
    if args.names:
        npath = Path(args.names).expanduser()
        if not npath.is_file():
            raise nv.Stop(f"no names file found at {npath}", 2)
        for line in nv.read_text(npath).split("\n"):
            if line.strip() and not line.strip().startswith("#"):
                remove += name_parts(line.strip())
    keep_own = {p.lower() for m in mine for p in name_parts(m)}
    remove = [r for r in dict.fromkeys(sorted(remove, key=len, reverse=True))
              if r.lower() not in keep_own]
    # A full name matches in any case; a single part of one ('Lee') only as written or
    # capitalized, so a name that is also a common word ('will', 'mark') stays in
    # ordinary use while 'Ingrid' is caught from a label written 'ingrid haugen'.
    patterns = []
    for r in remove:
        if " " in r:
            patterns.append(re.compile(r"(?<!\w)" + re.escape(r) + r"(?!\w)", re.IGNORECASE))
        else:
            forms = sorted({r, r[:1].upper() + r[1:]}, key=len, reverse=True)
            patterns.append(re.compile(r"(?<!\w)(?:" + "|".join(map(re.escape, forms))
                                       + r")(?!\w)"))

    paragraphs: list[tuple[str | None, list[str]]] = []
    replaced = dropped = 0
    for name, text in segs:
        lab = label(name)
        if args.only_me and lab != "Me":
            dropped += 1
            continue
        for p in patterns:
            text, n = p.subn("[name]", text)
            replaced += n
        if paragraphs and paragraphs[-1][0] == lab:
            paragraphs[-1][1].append(text)
        else:
            paragraphs.append((lab, [text]))

    body = []
    for lab, texts in paragraphs:
        joined = " ".join(texts)
        body.append(f"{lab}: {joined}" if lab else joined)
    out = folder / "transcript-clean.txt"
    nv.write_text(out, "\n\n".join(body) + "\n")

    words = sum(len(" ".join(t).split()) for _, t in paragraphs)
    nv.say(f"Wrote {out.name}: {len(paragraphs)} paragraphs, {words} words.")
    nv.say(f"Speakers found: {len(speakers)}" + (f" ({len(mine)} matched to you)" if args.me else ""))
    nv.say(f"Names replaced with [name]: {replaced}. Other speakers' lines removed: {dropped}.")
    if doubtful:
        nv.say(f"Lines that open with words and a colon but were kept as speech: {doubtful}. "
               "Where one of these is another speaker, the script missed that speaker: list "
               "the name in a --names file and run this again.")
    nv.say("Compare the speaker count with the number of people who spoke. A lower count "
           "means the script missed someone, whose words may sit in your own paragraphs.")
    nv.say("The cleaned file still needs a read-through before any AI reads it: names this "
           "script was not given, clients, figures that are not yours to share, and personal "
           "details.")
    if args.me and not mine:
        nv.say("Your speaker label was not found. Check its spelling as the transcript shows it.")
        return 1
    return 0


if __name__ == "__main__":
    nv.run_main(main)

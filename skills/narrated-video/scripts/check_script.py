#!/usr/bin/env python3
"""check_script.py: mechanical checks on script.md before the user reads it (step 4).

Usage:
  python3 check_script.py [--folder VIDEO_FOLDER] [--minutes N]

Checks, against the slide images in slides/:
  - one '## Slide N' scene for every slide image, numbered 1 to N in order (an error);
  - the word count, and the length it implies at 150 spoken words a minute; with
    --minutes, whether that is within 10 percent of the target;
  - digits and symbols the voice may read differently from what is meant (numbers are
    written as they are said: "forty-two percent", not "42%");
  - words in capitals, which the voice may spell out or say as a word;
  - sentences over 35 words, hard to say and to caption;
  - scenes with no narration, which show their slide silently for three seconds;
  - the 'Status:' line.

Prints the findings by slide. Exit codes: 0 no errors (warnings may remain); 1 errors;
2 no script or no slide images.
"""

from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path

sys.dont_write_bytecode = True      # leave no cache files in the skill's folder
sys.path.insert(0, str(Path(__file__).resolve().parent))
import nv_common as nv  # noqa: E402

SYMBOLS = "%$&/@#+=~<>|€£"
LONG_SENTENCE = 35
CAPS_OK = {"I", "A", "OK"}


def main() -> int:
    ap = argparse.ArgumentParser(description="Check script.md before it is read aloud.")
    ap.add_argument("--folder", help="the video's folder (default: the current folder)")
    ap.add_argument("--minutes", type=float, help="the planned length in minutes")
    args = ap.parse_args()
    folder = nv.folder_arg(args.folder)
    doc = nv.parse_script(folder / nv.SCRIPT_FILE)
    images = nv.slide_images(folder)
    if not images:
        raise nv.Stop(f"no slide images in {nv.SLIDES_DIR}/; run slides_to_images.py first.", 2)

    errors, warnings = [], []
    scenes = doc["scenes"]
    numbers = [s["slide"] for s in scenes]
    expected = list(range(1, len(images) + 1))
    if numbers != expected:
        missing = sorted(set(expected) - set(numbers))
        extra = sorted(set(numbers) - set(expected))
        dupes = sorted({n for n in numbers if numbers.count(n) > 1})
        if missing:
            errors.append(f"no scene for slide(s) {nv.listing(map(str, missing))}")
        if extra:
            errors.append(f"scene(s) for slide(s) {nv.listing(map(str, extra))}, but there "
                          f"are only {len(images)} slide images")
        if dupes:
            errors.append(f"more than one scene for slide(s) {nv.listing(map(str, dupes))}")
        if not (missing or extra or dupes):
            errors.append("the scenes are not in slide order")

    total_words = 0
    for sc in scenes:
        text = sc["text"]
        where = f"slide {sc['slide']}"
        if not text:
            warnings.append(f"{where}: no narration; the slide shows silently for three seconds")
            continue
        total_words += nv.word_count(text)
        digits = sorted(set(re.findall(r"\S*\d\S*", text)))
        if digits:
            warnings.append(f"{where}: digits {', '.join(digits)}; write numbers as they are said")
        symbols = sorted({c for c in text if c in SYMBOLS})
        if symbols:
            warnings.append(f"{where}: symbol(s) {' '.join(symbols)}; write them as words")
        caps = sorted({w.strip(".,;:!?\"'()") for w in text.split()
                       if re.fullmatch(r"[A-Z]{2,}s?", w.strip(".,;:!?\"'()"))} - CAPS_OK)
        if caps:
            warnings.append(f"{where}: capitals {', '.join(caps)}; listen for these in the "
                            "samples, and add a line to pronounce.txt if the voice misreads one")
        for s in nv.split_sentences(text):
            n = nv.word_count(s)
            if n > LONG_SENTENCE:
                warnings.append(f"{where}: a sentence of {n} words, starting "
                                f"\"{' '.join(s.split()[:6])} ...\"; consider splitting it")

    minutes = total_words / nv.WORDS_PER_MINUTE_PLAN
    nv.say(f"{nv.SCRIPT_FILE}: {len(scenes)} scenes for {len(images)} slide images, "
           f"{total_words} words, about {minutes:.1f} minutes at "
           f"{nv.WORDS_PER_MINUTE_PLAN} words a minute.")
    if args.minutes:
        if abs(minutes - args.minutes) > 0.1 * args.minutes:
            target = round(args.minutes * nv.WORDS_PER_MINUTE_PLAN)
            warnings.append(f"the planned length is {args.minutes:g} minutes, about {target} "
                            f"words; the script has {total_words}")
    status = doc["status"] or "missing"
    nv.say(f"Status line: {status}.")
    if status not in ("draft", "approved"):
        warnings.append("add a 'Status: draft' line under the title; it becomes "
                        "'Status: approved' once the user approves the script")
    for e in errors:
        nv.say(f"ERROR   {e}")
    for w in warnings:
        nv.say(f"CHECK   {w}")
    if not errors and not warnings:
        nv.say("No findings.")
    return 1 if errors else 0


if __name__ == "__main__":
    nv.run_main(main)

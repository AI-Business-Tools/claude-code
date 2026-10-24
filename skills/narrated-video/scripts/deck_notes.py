#!/usr/bin/env python3
"""deck_notes.py: the speaker notes from a PowerPoint file, one entry per shown slide (step 2).

Usage:
  python3 deck_notes.py DECK.pptx [--folder VIDEO_FOLDER] [--pdf DECK.pdf]

Writes notes.md in the video's folder: a '## Slide N' heading for each slide that is
not hidden, numbered in the order the slides are shown, so the numbers match the
pages of a PDF exported without hidden slides; the slide's speaker notes sit beneath.
Hidden slides are left out entirely, notes included.

With --pdf, compares the count of shown slides with the PDF's page count and says
when they differ (a PDF exported with hidden slides, or from an older version).

Prints counts only, never the notes themselves.

Exit codes: 0 done; 2 the file is missing or not a .pptx; 4 python-pptx is missing.
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

sys.dont_write_bytecode = True      # leave no cache files in the skill's folder
sys.path.insert(0, str(Path(__file__).resolve().parent))
import nv_common as nv  # noqa: E402


def main() -> int:
    ap = argparse.ArgumentParser(description="Extract speaker notes from a .pptx.")
    ap.add_argument("pptx", help="the deck as a PowerPoint (.pptx) file")
    ap.add_argument("--folder", help="the video's folder (default: the current folder)")
    ap.add_argument("--pdf", help="the exported PDF, to compare slide counts")
    args = ap.parse_args()
    nv.need_modules(["pptx"], __file__)
    from pptx import Presentation

    folder = nv.folder_arg(args.folder)
    path = Path(args.pptx).expanduser()
    if not path.is_file():
        raise nv.Stop(f"no file found at {path}", 2)
    if path.suffix.lower() != ".pptx":
        raise nv.Stop("speaker notes are read from a .pptx file. Keynote and Google Slides "
                      "can export one (File, then Export or Download, then PowerPoint).", 2)
    try:
        prs = Presentation(str(path))
    except Exception as e:
        raise nv.Stop(f"the file could not be read as a PowerPoint deck ({type(e).__name__}).", 2)

    parts = ["# Speaker notes", "",
             f"From {path.name}, shown slides only, numbered as they appear in the video.", ""]
    shown = hidden = with_notes = 0
    for slide in prs.slides:
        if slide._element.get("show") == "0":
            hidden += 1
            continue
        shown += 1
        text = ""
        if slide.has_notes_slide:
            frame = slide.notes_slide.notes_text_frame
            text = (frame.text if frame is not None else "").strip()
        if text:
            with_notes += 1
        body = "\n".join(line.strip() for line in text.splitlines() if line.strip())
        parts += [f"## Slide {shown}", "", body or "(no notes)", ""]
    nv.write_text(folder / "notes.md", "\n".join(parts))

    nv.say(f"Wrote notes.md: {shown} shown slides, {with_notes} with speaker notes; "
           f"{hidden} hidden slide(s) left out.")
    if args.pdf:
        nv.need_modules(["pymupdf"], __file__)
        import pymupdf
        pdf = Path(args.pdf).expanduser()
        if not pdf.is_file():
            raise nv.Stop(f"no PDF found at {pdf}", 2)
        pages = pymupdf.open(str(pdf)).page_count
        if pages == shown:
            nv.say(f"The PDF has {pages} pages, matching the {shown} shown slides.")
        else:
            nv.say(f"The PDF has {pages} pages but the deck shows {shown} slides. Export the "
                   "PDF again from this deck, leaving hidden slides out, before going on.")
            return 1
    return 0


if __name__ == "__main__":
    nv.run_main(main)

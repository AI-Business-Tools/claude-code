#!/usr/bin/env python3
"""slides_to_images.py: one image per slide from the deck's PDF (step 3).

Usage:
  python3 slides_to_images.py DECK.pdf [--folder VIDEO_FOLDER] [--width 1920]

Writes slides/slide-01.png, slide-02.png, ... (one per PDF page, in page order) and
slides/slides-text.md (each page's text under a '## Slide N' heading, for writing the
script) in the video's folder. Earlier slide-NN.png files in slides/ are replaced, so a
re-export with fewer pages leaves no stray image behind.

Uses PyMuPDF only: no PowerPoint, Keynote, or LibreOffice is needed.

Exit codes: 0 done; 2 the PDF is missing or unreadable; 4 PyMuPDF is missing.
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

sys.dont_write_bytecode = True      # leave no cache files in the skill's folder
sys.path.insert(0, str(Path(__file__).resolve().parent))
import nv_common as nv  # noqa: E402


def main() -> int:
    ap = argparse.ArgumentParser(description="Turn each PDF page into a slide image.")
    ap.add_argument("pdf", help="the deck exported as a PDF")
    ap.add_argument("--folder", help="the video's folder (default: the current folder)")
    ap.add_argument("--width", type=int, default=1920, help="image width in pixels")
    args = ap.parse_args()
    nv.need_modules(["pymupdf"], __file__)
    import pymupdf

    folder = nv.folder_arg(args.folder)
    pdf = Path(args.pdf).expanduser()
    if not pdf.is_absolute():
        pdf = (Path.cwd() / pdf).resolve()
    if not pdf.is_file():
        raise nv.Stop(f"no PDF found at {pdf}", 2)
    try:
        doc = pymupdf.open(str(pdf))
    except Exception as e:
        raise nv.Stop(f"the PDF could not be opened ({type(e).__name__}).", 2)
    if doc.page_count == 0:
        raise nv.Stop("the PDF has no pages.", 2)

    out_dir = folder / nv.SLIDES_DIR
    out_dir.mkdir(parents=True, exist_ok=True)
    for old in out_dir.glob("slide-*.png"):
        old.unlink()

    text_parts = ["# Slide text", "",
                  f"Text from each page of {pdf.name}, for writing the script.", ""]
    shapes = set()
    for i, page in enumerate(doc, 1):
        zoom = args.width / page.rect.width
        pix = page.get_pixmap(matrix=pymupdf.Matrix(zoom, zoom), alpha=False)
        pix.save(str(out_dir / f"slide-{i:02d}.png"))
        shapes.add((pix.width, pix.height))
        words = " ".join(page.get_text("text").split())
        text_parts += [f"## Slide {i}", "", words or "(no text on this slide)", ""]
    nv.write_text(out_dir / "slides-text.md", "\n".join(text_parts))

    w, h = max(shapes)
    ratio = w / h
    nv.say(f"Made {doc.page_count} slide images in {nv.SLIDES_DIR}/ ({w} x {h} pixels) and "
           f"{nv.SLIDES_DIR}/slides-text.md.")
    if abs(ratio - 16 / 9) > 0.02:
        nv.say(f"Note: the slides are {ratio:.2f} to 1, not 16 to 9 widescreen; the video "
               "shows them centered with dark bars at the sides.")
    if len(shapes) > 1:
        nv.say("Note: the pages are not all the same size; check the PDF is the slide deck.")
    nv.say("Check this count against the slides meant for the video. A higher count means "
           "hidden or backup slides reached the PDF.")
    return 0


if __name__ == "__main__":
    nv.run_main(main)

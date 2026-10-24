#!/usr/bin/env python3
"""build_video.py: captions and the finished MP4 from the slides and the recorded voice
(steps 6 and 7).

Usage (run in the video's folder, or pass --folder):
  python3 build_video.py [--no-burn] [--scene-gap 0.6] [--keep-work] [--font FONT.ttf]

Reads slides/slide-NN.png, script.md, and audio/clips.json (from voice.py), and writes:
  captions.srt and captions.vtt  the script's own words, each sentence on screen while
                                 its clip plays, at most two lines of 42 characters;
                                 a longer sentence is split into captions at a natural
                                 break, its time divided by length
  video.mp4                      1920 x 1080, H.264 video and AAC audio, which phones and
                                 web browsers play; the captions are drawn on a band
                                 below the slide, so they never cover it

--no-burn draws no captions: each slide fills the frame, and the captions travel as a
track the viewer can switch on (and as the two files, for sites that take one).

The timeline: half a second before the first word, then each scene in slide order, its
sentences one after another with a short pause between them, --scene-gap seconds of
silence between scenes (the slide changes halfway through it), and one second at the
end. A scene with no narration shows its slide for three seconds.

The audio is joined in Python to the sample, so caption times are exact; ffmpeg then
evens the loudness and encodes the video. The frames and the joined audio go in the
system's temporary folder and are removed at the end; --keep-work keeps them in work/
in the video's folder instead.

Exit codes: 0 done; 1 ffmpeg failed or the video could not be written; 2 the script,
the slides, and the recorded voice do not match (the message says which step to run
again); 4 a Python package is missing; 5 ffmpeg is missing.
"""

from __future__ import annotations

import argparse
import json
import os
import re
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

sys.dont_write_bytecode = True      # leave no cache files in the skill's folder
sys.path.insert(0, str(Path(__file__).resolve().parent))
import nv_common as nv  # noqa: E402

WIDTH, HEIGHT = 1920, 1080
FPS = 30
BAND = 190                 # caption band below the slide, in pixels
FONT_SIZE = 52
LINE_CHARS = 42            # common caption guidance: two lines of about 42 characters
CUE_CHARS = 2 * LINE_CHARS
LEAD_IN, END_HOLD, SENTENCE_GAP = nv.LEAD_IN, nv.END_HOLD, nv.SENTENCE_GAP
CLIP_PAD_IN, CLIP_PAD_OUT, SILENT_HOLD = nv.CLIP_PAD_IN, nv.CLIP_PAD_OUT, nv.SILENT_HOLD
LINGER = 0.3               # a caption stays this long after its words end
BG = (0, 0, 0)
TEXT = (255, 255, 255)

# Where a caption may break, scored low (good) to high (bad).
AFTER_BAD = set("""a an the this that these those my your his her its our their to of in on at
by for with from into onto about over under than as and or but nor so if is are was were be
been being has have had do does did will would can could should may might must not very
such each every some any no per via""".split())
BEFORE_GOOD = set("""and but or nor so yet because although though while when whenever where
which who whom whose that if unless until than as since to for with from in on at by of about
into through after before during without""".split())
DESCRIBERS = set("""new old high low large small big more most less least first second third
fourth fifth sixth seventh eighth ninth tenth last next key main major top strong weak early
late long short good bad best better worse worst same other several many few total average
annual quarterly monthly weekly daily higher lower larger smaller faster slower""".split())
NUMBER_WORDS = set("""zero one two three four five six seven eight nine ten eleven twelve
thirteen fourteen fifteen sixteen seventeen eighteen nineteen twenty thirty forty fifty sixty
seventy eighty ninety hundred thousand million billion trillion half""".split())
DESCRIBER_ENDINGS = ("al", "ive", "ous", "ful", "able", "ible", "ic", "less", "ary", "est")


def bare(word: str) -> str:
    return word.strip(".,;:!?\"'()[]\u201c\u201d\u2018\u2019").lower()


def break_cost(words: list[str], i: int) -> float:
    """Cost of a break between words[i-1] and words[i]."""
    prev, nxt = words[i - 1], words[i]
    if prev.rstrip("\"')\u201d\u2019").endswith((".", "!", "?", ";", ":")):
        return 0
    if prev.rstrip("\"')\u201d\u2019").endswith(","):
        return 1
    p, n = bare(prev), bare(nxt)
    if p in AFTER_BAD or p.endswith("'s") or p.endswith("\u2019s"):
        return 60
    if p.split("-")[-1] in NUMBER_WORDS:
        return 45
    if prev[:1].isupper() and nxt[:1].isupper():
        return 45            # likely a name or a title
    if p in DESCRIBERS or (len(p) > 4 and p.endswith(DESCRIBER_ENDINGS)):
        return 30
    if "-" in p.strip("-") and n not in BEFORE_GOOD:
        return 30            # a hyphenated describing word ("at-risk") before its noun
    if n in BEFORE_GOOD:
        return 4
    return 15


def text_len(words: list[str]) -> int:
    return len(" ".join(words))


def best_lines(words: list[str]) -> tuple[float, list[str]] | None:
    """One or two lines of at most LINE_CHARS characters, broken where it reads best."""
    if text_len(words) <= LINE_CHARS:
        return 0.0, [" ".join(words)]
    if len(words) == 1:          # one word longer than a line (a web address): alone
        return 50.0, [words[0]]
    best = None
    for i in range(1, len(words)):
        top, bottom = words[:i], words[i:]
        lt, lb = text_len(top), text_len(bottom)
        if lt > LINE_CHARS or lb > LINE_CHARS:
            continue
        cost = break_cost(words, i) * 2 + abs(lt - lb) * 0.3 + (2 if lt > lb + 8 else 0)
        if best is None or cost < best[0]:
            best = (cost, [" ".join(top), " ".join(bottom)])
    return best


def layout_sentence(sentence: str) -> list[list[str]]:
    """Split a sentence into captions (each a list of one or two lines)."""
    words = sentence.split()
    n = len(words)
    if text_len(words) <= LINE_CHARS:
        return [[sentence]]
    inf = float("inf")
    cost = [inf] * (n + 1)
    choice: list[tuple[int, list[str]] | None] = [None] * (n + 1)
    cost[0] = 0.0
    for b in range(1, n + 1):
        for a in range(b - 1, -1, -1):
            if b - a > 1 and text_len(words[a:b]) > CUE_CHARS:
                break
            lines = best_lines(words[a:b])
            if lines is None or cost[a] == inf:
                continue
            c = cost[a] + 20 + lines[0]
            if b < n:
                c += break_cost(words, b) * 3
            chars = text_len(words[a:b])
            if chars < 20:
                c += 40          # a caption this short flashes past
            if c < cost[b]:
                cost[b], choice[b] = c, (a, lines[1])
    if cost[n] == inf:           # no layout fits (not expected): one word a caption
        return [[w] for w in words]
    cues, b = [], n
    while b > 0:
        a, lines = choice[b]
        cues.append(lines)
        b = a
    return list(reversed(cues))


# --------------------------------------------------------------------------- inputs

def load(folder: Path):
    images = nv.slide_images(folder)
    if not images:
        raise nv.Stop(f"no slide images in {nv.SLIDES_DIR}/; run slides_to_images.py first.", 2)
    doc = nv.parse_script(folder / nv.SCRIPT_FILE)
    scenes = doc["scenes"]
    if [s["slide"] for s in scenes] != list(range(1, len(images) + 1)):
        raise nv.Stop(f"{nv.SCRIPT_FILE} needs one scene per slide image, slides 1 to "
                      f"{len(images)} in order; run check_script.py for details.", 2)
    manifest_path = folder / nv.AUDIO_DIR / nv.CLIPS_FILE
    if not manifest_path.is_file():
        raise nv.Stop("no recorded voice yet; run voice.py script first.", 2)
    manifest = json.loads(nv.read_text(manifest_path))
    recorded = {s["slide"]: s["sentences"] for s in manifest.get("scenes", [])}
    pairs = nv.load_pronunciations(folder)
    out = []
    for sc in scenes:
        sentences = nv.split_sentences(sc["text"]) if sc["text"] else []
        clips = recorded.get(sc["slide"], [])
        if [c["text"] for c in clips] != sentences:
            raise nv.Stop(f"slide {sc['slide']}'s scene in {nv.SCRIPT_FILE} differs from what "
                          "was recorded. Run voice.py script again (it sends only the "
                          "changed sentences), then run this again.", 2)
        if [c["spoken"] for c in clips] != [nv.spoken_form(t, pairs) for t in sentences]:
            raise nv.Stop(f"{nv.PRONOUNCE_FILE} changed how slide {sc['slide']}'s scene is "
                          "said since it was recorded. Run voice.py script again, then run "
                          "this again.", 2)
        for c in clips:
            if not (folder / c["file"]).is_file():
                raise nv.Stop(f"a recorded clip for slide {sc['slide']} is missing; run "
                              "voice.py script again.", 2)
        out.append({"slide": sc["slide"], "image": images[sc["slide"] - 1], "clips": clips})
    return out


# --------------------------------------------------------------------------- timeline

def build_timeline(folder: Path, scenes: list[dict], scene_gap: float):
    """Place every clip; return (audio frames, captions, scene spans, total seconds)."""
    rate = nv.SAMPLE_RATE
    bytes_per = nv.SAMPLE_WIDTH * nv.CHANNELS
    audio = bytearray()
    captions = []          # (start s, end s, lines, scene index)
    spans = []             # (start s, end s) for each scene's slide
    half_gap = scene_gap / 2

    def pad_to(seconds: float):
        target = int(round(seconds * rate)) * bytes_per
        if target > len(audio):
            audio.extend(b"\x00" * (target - len(audio)))

    t = 0.0
    for k, sc in enumerate(scenes):
        scene_start = t
        t += LEAD_IN if k == 0 else half_gap
        if not sc["clips"]:
            t += SILENT_HOLD
        for j, clip in enumerate(sc["clips"]):
            if j:
                t += SENTENCE_GAP
            params, frames = nv.read_wav((folder / clip["file"]).read_bytes())
            if params != (nv.CHANNELS, nv.SAMPLE_WIDTH, rate):
                raise nv.Stop("a recorded clip is not in the expected format; run voice.py "
                              f"script --redo {sc['slide']}.", 2)
            total = len(frames) / (rate * bytes_per)
            start, end = clip.get("speech_start"), clip.get("speech_end")
            if start is None or end is None:
                start, end = nv.speech_bounds(frames, rate)
            cut_in = max(0.0, start - CLIP_PAD_IN)
            cut_out = min(total, end + CLIP_PAD_OUT)
            a = int(round(cut_in * rate)) * bytes_per
            b = int(round(cut_out * rate)) * bytes_per
            pad_to(t)
            t = len(audio) / (rate * bytes_per)
            audio.extend(frames[a:b])
            speak_from = t + (start - cut_in)
            speak_to = t + (end - cut_in)
            t = len(audio) / (rate * bytes_per)
            cues = layout_sentence(clip["text"])
            span = speak_to - speak_from
            chars = [sum(len(x) for x in c) for c in cues]
            whole = sum(chars) or 1
            c0 = speak_from
            for lines, n in zip(cues, chars):
                c1 = c0 + span * n / whole
                captions.append([c0, c1, lines, k])
                c0 = c1
        t += END_HOLD if k == len(scenes) - 1 else half_gap
        pad_to(t)
        t = len(audio) / (rate * bytes_per)
        spans.append((scene_start, t))

    # Hold each caption a little past its words, and bridge short pauses inside a
    # scene so the band does not flicker between sentences.
    for i, cap in enumerate(captions):
        nxt = captions[i + 1] if i + 1 < len(captions) else None
        end = cap[1] + LINGER
        if nxt and nxt[3] == cap[3] and nxt[0] - cap[1] < 0.8:
            end = nxt[0]
        if nxt:
            end = min(end, nxt[0])
        end = min(end, spans[cap[3]][1])
        cap[1] = max(end, cap[1])
    return bytes(audio), captions, spans, t


def stamp(seconds: float, sep: str) -> str:
    ms = int(round(seconds * 1000))
    h, ms = divmod(ms, 3_600_000)
    m, ms = divmod(ms, 60_000)
    s, ms = divmod(ms, 1000)
    return f"{h:02d}:{m:02d}:{s:02d}{sep}{ms:03d}"


def write_captions(folder: Path, captions) -> None:
    srt, vtt = [], ["WEBVTT", ""]
    for i, (a, b, lines, _) in enumerate(captions, 1):
        srt += [str(i), f"{stamp(a, ',')} --> {stamp(b, ',')}", *lines, ""]
        vtt += [f"{stamp(a, '.')} --> {stamp(b, '.')}", *lines, ""]
    nv.write_text(folder / "captions.srt", "\n".join(srt), newline="\r\n")
    nv.write_text(folder / "captions.vtt", "\n".join(vtt), newline="\n")


# --------------------------------------------------------------------------- frames

FONT_CANDIDATES = [
    "/System/Library/Fonts/Supplemental/Arial.ttf",
    "/Library/Fonts/Arial.ttf",
    "/System/Library/Fonts/Helvetica.ttc",
    os.path.join(os.environ.get("WINDIR", r"C:\Windows"), "Fonts", "arial.ttf"),
    os.path.join(os.environ.get("WINDIR", r"C:\Windows"), "Fonts", "segoeui.ttf"),
    "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
    "/usr/share/fonts/dejavu/DejaVuSans.ttf",
    "/usr/share/fonts/truetype/liberation/LiberationSans-Regular.ttf",
]


def load_font(path: str | None, size: int):
    from PIL import ImageFont
    for candidate in ([path] if path else []) + FONT_CANDIDATES:
        if candidate and Path(candidate).is_file():
            try:
                return ImageFont.truetype(candidate, size)
            except OSError:
                continue
    try:
        return ImageFont.load_default(size=size)
    except TypeError:
        nv.warn("Note: no scalable font was found, so the captions use a small built-in "
                "font; pass --font with the path to a .ttf file for a larger one.")
        return ImageFont.load_default()


class Frames:
    def __init__(self, work: Path, burn: bool, font_path: str | None):
        from PIL import Image
        self.Image = Image
        self.dir = work / "frames"
        self.dir.mkdir(parents=True, exist_ok=True)
        self.burn = burn
        self.font = load_font(font_path, FONT_SIZE) if burn else None
        self.slides: dict[Path, object] = {}
        self.made: dict[tuple, str] = {}

    def _slide(self, path: Path):
        if path not in self.slides:
            img = self.Image.open(path).convert("RGB")
            area_h = HEIGHT - BAND if self.burn else HEIGHT
            scale = min(WIDTH / img.width, area_h / img.height)
            size = (max(1, round(img.width * scale)), max(1, round(img.height * scale)))
            self.slides[path] = (img.resize(size, self.Image.LANCZOS), area_h)
        return self.slides[path]

    def get(self, image: Path, lines: tuple | None) -> str:
        key = (str(image), lines)
        if key in self.made:
            return self.made[key]
        from PIL import ImageDraw
        frame = self.Image.new("RGB", (WIDTH, HEIGHT), BG)
        slide, area_h = self._slide(image)
        frame.paste(slide, ((WIDTH - slide.width) // 2, (area_h - slide.height) // 2))
        if lines:
            draw = ImageDraw.Draw(frame)
            font = self.font
            line_h = int(FONT_SIZE * 1.25)
            top = HEIGHT - BAND + (BAND - line_h * len(lines)) // 2
            for n, line in enumerate(lines):
                w = draw.textlength(line, font=font)
                draw.text(((WIDTH - w) / 2, top + n * line_h), line, font=font, fill=TEXT)
        name = f"frame-{len(self.made) + 1:04d}.png"
        frame.save(self.dir / name, compress_level=1)
        self.made[key] = name
        return name


def segments(spans, captions, total: float):
    """(start, end, scene index, caption lines or None) covering the whole video."""
    cuts = {0.0, total}
    for a, b in spans:
        cuts.update((a, b))
    for a, b, _, _ in captions:
        cuts.update((a, b))
    cuts = sorted(c for c in cuts if 0 <= c <= total)
    out = []
    for a, b in zip(cuts, cuts[1:]):
        if b - a < 1e-4:
            continue
        mid = (a + b) / 2
        k = next((i for i, (s, e) in enumerate(spans) if s <= mid < e), len(spans) - 1)
        cap = next((tuple(c[2]) for c in captions if c[0] <= mid < c[1]), None)
        if out and out[-1][2] == k and out[-1][3] == cap:
            out[-1][1] = b
        else:
            out.append([a, b, k, cap])
    return out


# --------------------------------------------------------------------------- encode

def encode(folder: Path, work: Path, list_path: Path, wav: Path, total: float,
           burn: bool) -> Path:
    ffmpeg = nv.need_tool("ffmpeg")
    out = folder / "video.mp4"
    tmp = folder / "video.partial.mp4"
    cmd = [ffmpeg, "-nostdin", "-y", "-v", "error",
           "-f", "concat", "-safe", "0", "-i", str(list_path), "-i", str(wav)]
    if not burn:
        cmd += ["-i", str(folder / "captions.srt")]
    cmd += ["-map", "0:v:0", "-map", "1:a:0"]
    if not burn:
        cmd += ["-map", "2:s:0", "-c:s", "mov_text", "-metadata:s:s:0", "language=eng"]
    cmd += ["-r", str(FPS), "-c:v", "libx264", "-preset", "medium", "-tune", "stillimage",
            "-crf", "20", "-pix_fmt", "yuv420p",
            "-af", "loudnorm=I=-16:TP=-1.5:LRA=11", "-ar", "48000",
            "-c:a", "aac", "-b:a", "160k",
            "-t", f"{total:.3f}", "-movflags", "+faststart", "-f", "mp4", str(tmp)]
    proc = subprocess.run(cmd, capture_output=True, text=True, errors="replace")
    if proc.returncode != 0:
        tmp.unlink(missing_ok=True)
        detail = (proc.stderr or "").strip().splitlines()[-3:]
        raise nv.Stop("ffmpeg could not make the video: " + " | ".join(detail), 1)
    try:
        os.replace(tmp, out)
    except PermissionError:
        raise nv.Stop("video.mp4 is open in another program. Close it and run this again; "
                      "the new version is saved as video.partial.mp4 meanwhile.", 1)
    return out


def probe(path: Path) -> dict:
    ffprobe = nv.find_tool("ffprobe")
    if not ffprobe:
        return {}
    proc = subprocess.run([ffprobe, "-v", "error", "-show_entries",
                           "format=duration:stream=codec_type,codec_name,width,height",
                           "-of", "json", str(path)], capture_output=True, text=True,
                          errors="replace")
    try:
        return json.loads(proc.stdout)
    except json.JSONDecodeError:
        return {}


def main() -> int:
    ap = argparse.ArgumentParser(description="Build captions and the narrated MP4.")
    ap.add_argument("--folder", help="the video's folder (default: the current folder)")
    ap.add_argument("--no-burn", action="store_true",
                    help="no captions drawn on the picture; a switchable caption track instead")
    ap.add_argument("--scene-gap", type=float, default=nv.SCENE_GAP, help="seconds between scenes")
    ap.add_argument("--keep-work", action="store_true",
                    help="keep the frames and joined audio in work/ in the video's folder")
    ap.add_argument("--font", help="a .ttf font file for the captions")
    args = ap.parse_args()
    nv.need_modules(["PIL"], __file__)
    nv.need_tool("ffmpeg")

    folder = nv.folder_arg(args.folder)
    burn = not args.no_burn
    scenes = load(folder)
    audio, captions, spans, total = build_timeline(folder, scenes, args.scene_gap)
    write_captions(folder, captions)

    # Frames and the joined audio go in the system's temporary folder, not the video's
    # folder, which may be synced by OneDrive, iCloud, or Dropbox.
    if args.keep_work:
        work = folder / "work"
        shutil.rmtree(work, ignore_errors=True)
        work.mkdir(exist_ok=True)
    else:
        work = Path(tempfile.mkdtemp(prefix="narrated-video-"))
    try:
        wav = work / "narration.wav"
        nv.write_wav(wav, audio)

        frames = Frames(work, burn, args.font)
        entries = []
        shown = captions if burn else []
        for a, b, k, cap in segments(spans, shown, total):
            dur = round(b, 3) - round(a, 3)
            if dur < 0.001:
                continue
            entries.append((frames.get(scenes[k]["image"], cap), dur))
        lines = ["ffconcat version 1.0"]
        for name, dur in entries:
            lines += [f"file '{name}'", f"duration {dur:.3f}"]
        lines.append(f"file '{entries[-1][0]}'")     # the concat reader needs the last one twice
        list_path = frames.dir / "list.txt"
        nv.write_text(list_path, "\n".join(lines) + "\n", newline="\n")

        nv.say(f"Timeline: {total:.1f} seconds, {len(scenes)} scenes, {len(captions)} "
               f"captions; {len(frames.made)} distinct frames. Encoding ...")
        out = encode(folder, work, list_path, wav, total, burn)
    finally:
        if not args.keep_work:
            shutil.rmtree(work, ignore_errors=True)

    info = probe(out)
    dur = float(info.get("format", {}).get("duration", 0) or 0)
    kinds = [f"{s.get('codec_type')} {s.get('codec_name')}" +
             (f" {s.get('width')}x{s.get('height')}" if s.get("width") else "")
             for s in info.get("streams", [])]
    size_mb = out.stat().st_size / 1_000_000
    whole = int(round(dur))
    nv.say(f"Wrote video.mp4: {whole} seconds ({whole // 60}:{whole % 60:02d}), "
           f"{size_mb:.1f} MB; streams: {', '.join(kinds) or 'unknown'}.")
    nv.say(f"Wrote captions.srt and captions.vtt: {len(captions)} captions"
           + ("; drawn on the video below the slides." if burn
              else "; also inside the video as a switchable track."))
    if dur and abs(dur - total) > 0.2:
        nv.warn(f"Note: the video runs {dur:.2f} seconds against a planned {total:.2f}.")
    return 0


if __name__ == "__main__":
    nv.run_main(main)

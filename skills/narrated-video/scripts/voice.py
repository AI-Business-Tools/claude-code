#!/usr/bin/env python3
"""voice.py: read the approved script aloud with a Gemini text-to-speech voice (step 5).

Usage (run in the video's folder, or pass --folder):
  python3 voice.py samples [--scene N] [--voices Charon,Kore,Puck] [--style TEXT]
      Reads one scene (the longest, unless --scene names a slide number) once in each
      voice, into samples/slide-NN-<voice>.wav, and reports each reading's length and
      pace, so the user can choose a voice by ear before the whole script is recorded.

  python3 voice.py script [--voice Charon] [--style TEXT] [--redo N [N ...]] [--dry-run]
      Records one audio clip per sentence into audio/, and writes audio/clips.json,
      which build_video.py reads. A sentence already recorded with the same words,
      voice, and style is reused, never sent again, so after a script edit only the
      changed sentences are sent; --redo N records every sentence of slide N's scene
      again (for a misread word with no text change). --dry-run sends nothing and
      reports what a run would send and cost.

  python3 voice.py test
      Reads one short sentence into voice-test.wav in the video's folder (used by
      check_setup.py --test-voice).

Common options: --model (default gemini-3.8-flash-tts), --folder, --pause SECONDS
between requests (for a free-tier key that hits a per-minute limit).

The request goes to Gemini's Interactions endpoint over HTTPS with Python's standard
library, so this script needs no extra package. Only the script's words are sent:
never the slides, notes, outline, or transcript. The key is read from the
GEMINI_API_KEY environment variable, or else from where SKILL.md's key-storing commands
put it (nv_common.get_key), and is never printed or saved. A pronounce.txt
beside the script ('written = spoken', one pair per line) changes how a word is said
without changing the captions. Costs are reported from the token counts Google
returns, at the paid-tier price.

Exit codes: 0 done; 1 the service refused or failed (the message says why, and a run
again resumes where it stopped); 2 the script or arguments are not usable; 3 the
script is not yet marked approved; 5 ffmpeg is missing.
"""

from __future__ import annotations

import argparse
import base64
import json
import os
import re
import ssl
import subprocess
import sys
import tempfile
import time
import urllib.error
import urllib.request
from pathlib import Path

sys.dont_write_bytecode = True      # leave no cache files in the skill's folder
sys.path.insert(0, str(Path(__file__).resolve().parent))
import nv_common as nv  # noqa: E402

ENDPOINT = "https://generativelanguage.googleapis.com/v1beta/interactions"
TEST_SENTENCE = "This is a test of the narration voice."
RETRY_WAITS = (10, 30, 60)          # seconds; covers a per-minute limit or a brief outage
RETRY_CODES = {408, 429, 500, 502, 503, 504}
TIMEOUT = 180                       # seconds for one request


# --------------------------------------------------------------------------- service

def tls_contexts() -> list:
    """The system's certificates first; then certifi's, where the system has none that
    Python can use (python.org's Python on a Mac before 'Install Certificates' is run)."""
    contexts = [ssl.create_default_context()]
    try:
        import certifi
        contexts.append(ssl.create_default_context(cafile=certifi.where()))
    except Exception:
        pass
    return contexts


class Sender:
    """Sends one piece of text to Gemini and returns 24 kHz mono 16-bit audio frames,
    keeping count of the tokens Google reports."""

    def __init__(self, model: str, voice: str, style: str | None, pause: float = 0.0):
        key, _ = nv.get_key()
        if not key:
            raise nv.Stop(f"no Gemini key was found: {nv.KEY_VARIABLE} is not set, and no key "
                          "is stored where SKILL.md, Step 1, 'Storing the key', puts it. Store "
                          "it there and run this again.", 1)
        self.key = key
        self.model, self.voice, self.style, self.pause = model, voice, style, pause
        self.sent = 0
        self.text_tokens = 0
        self.audio_tokens = 0
        self.contexts = tls_contexts()
        if voice not in nv.KNOWN_VOICES:
            nv.warn(f"Note: {voice} is not on the list of Gemini voices this skill knows; "
                    "trying it anyway.")

    def _post(self, body: dict):
        """(response document, None) or (None, (code, status, message))."""
        data = json.dumps(body).encode("utf-8")
        last_tls = None
        for ctx in self.contexts:
            req = urllib.request.Request(ENDPOINT, data=data, method="POST", headers={
                "Content-Type": "application/json", "x-goog-api-key": self.key})
            try:
                with urllib.request.urlopen(req, timeout=TIMEOUT, context=ctx) as resp:
                    return json.loads(resp.read().decode("utf-8")), None
            except urllib.error.HTTPError as e:
                try:
                    err = json.loads(e.read().decode("utf-8", "replace")).get("error", {})
                except Exception:
                    err = {}
                return None, (e.code, err.get("status"), str(err.get("message") or "")[:300])
            except urllib.error.URLError as e:
                if isinstance(e.reason, ssl.SSLCertVerificationError):
                    last_tls = e
                    continue
                return None, (503, type(e.reason).__name__, "could not reach Google; check "
                              "the internet connection, and that commands may use the network")
            except (TimeoutError, OSError) as e:
                return None, (503, type(e).__name__, "could not reach Google; check the "
                              "internet connection, and that commands may use the network")
            except (ValueError, UnicodeDecodeError):
                return None, (None, "BAD_RESPONSE", "Google's reply could not be read")
        return None, (None, "CERTIFICATE", f"this Python could not verify Google's certificate "
                      f"({type(last_tls).__name__}). On a Mac with Python from python.org, run "
                      "'Install Certificates.command' in the Python folder under Applications; "
                      "or run check_setup.py --install, which adds certifi.")

    def _once(self, text: str):
        content = {"type": "text", "text": text}
        if self.style:
            content["annotations"] = [{"type": "speech_metadata", "style": self.style}]
        body = {"model": self.model,
                "input": [{"type": "user_input", "content": [content]}],
                "response_format": {"type": "audio"},
                "generation_config": {"speech_config": [{"voice": self.voice}]},
                "store": False}
        doc, err = self._post(body)
        if err:
            return None, err
        audio = None
        for step in reversed(doc.get("steps") or []):
            if step.get("type") != "model_output":
                continue
            for item in reversed(step.get("content") or []):
                if item.get("type") == "audio" and item.get("data"):
                    audio = item
                    break
            if audio:
                break
        if audio is None:
            return None, (None, "NO_AUDIO", f"Google returned no audio "
                                            f"(status {doc.get('status')})")
        usage = doc.get("usage") or {}
        for part in usage.get("input_tokens_by_modality") or []:
            self.text_tokens += int(part.get("tokens") or 0)
        for part in usage.get("output_tokens_by_modality") or []:
            if part.get("modality") == "audio":
                self.audio_tokens += int(part.get("tokens") or 0)
        return audio, None

    def send(self, text: str, label: str) -> bytes:
        if self.sent and self.pause > 0:
            time.sleep(self.pause)
        for attempt in range(len(RETRY_WAITS) + 1):
            audio, err = self._once(text)
            if audio is not None:
                self.sent += 1
                return to_frames(audio)
            code, status, message = err
            if code in RETRY_CODES and attempt < len(RETRY_WAITS):
                wait = RETRY_WAITS[attempt]
                nv.warn(f"  Google answered {code} {status or ''} on {label}; "
                        f"trying again in {wait} seconds.")
                time.sleep(wait)
                continue
            raise nv.Stop(explain(code, status, message, self.model, label), 1)
        raise nv.Stop("unreachable", 1)

    def cost(self) -> float:
        text_rate, audio_rate, _ = nv.price_today()
        return (self.text_tokens * text_rate + self.audio_tokens * audio_rate) / 1_000_000


def explain(code, status, message, model, label) -> str:
    where = f"while voicing {label}"
    if code == 404:
        return (f"Google does not recognize the model name {model} ({where}). Google may "
                "have renamed it; check https://ai.google.dev/gemini-api/docs/speech-generation "
                "and pass the current name with --model.")
    if code in (401, 403) or status in ("PERMISSION_DENIED", "UNAUTHENTICATED"):
        return (f"Google refused the key ({code} {status}) {where}. Check that "
                f"{nv.KEY_VARIABLE} holds the key from Google AI Studio, with nothing added.")
    if code == 429:
        return (f"Google's usage limit was reached {where} ({message}). The clips recorded "
                "so far are kept: wait (AI Studio shows the free tier's limits) or link a "
                "billing account, then run the same command again to continue.")
    if code == 400:
        return (f"Google rejected the request {where} ({status}: {message}). A misspelled "
                "voice name is the usual cause.")
    return f"Google's speech service failed {where} ({code} {status}: {message})."


def to_frames(audio: dict) -> bytes:
    """Gemini's audio block, as WAV or raw 16-bit PCM, to 24 kHz mono 16-bit frames."""
    raw = base64.b64decode(audio["data"])
    mime = (audio.get("mime_type") or "").lower()
    if raw[:4] == b"RIFF":
        params, frames = nv.read_wav(raw)
    else:
        m = re.search(r"rate=(\d+)", mime)
        rate = audio.get("sample_rate") or (int(m.group(1)) if m else nv.SAMPLE_RATE)
        params = (audio.get("channels") or 1, 2, int(rate))
        frames = raw
    if params == (nv.CHANNELS, nv.SAMPLE_WIDTH, nv.SAMPLE_RATE):
        return frames
    return convert(frames, params)


def convert(frames: bytes, params) -> bytes:
    """Any channel count or rate to 24 kHz mono 16-bit, through ffmpeg."""
    ffmpeg = nv.need_tool("ffmpeg")
    channels, width, rate = params
    with tempfile.TemporaryDirectory() as tmp:
        src, dst = Path(tmp) / "in.wav", Path(tmp) / "out.wav"
        nv.write_wav(src, frames, rate=rate, channels=channels, width=width)
        proc = subprocess.run([ffmpeg, "-nostdin", "-y", "-v", "error", "-i", str(src),
                               "-ac", "1", "-ar", str(nv.SAMPLE_RATE), "-c:a", "pcm_s16le",
                               str(dst)], capture_output=True, text=True, errors="replace")
        if proc.returncode != 0:
            raise nv.Stop("ffmpeg could not convert the audio Google returned.", 1)
        return nv.read_wav(dst.read_bytes())[1]


# --------------------------------------------------------------------------- script

def approved_scenes(folder: Path) -> list[dict]:
    doc = nv.parse_script(folder / nv.SCRIPT_FILE)
    if doc["status"] != "approved":
        raise nv.Stop(f"{nv.SCRIPT_FILE} is not marked 'Status: approved'. This script sends "
                      "nothing to the voice service until the user has read and approved the "
                      "script.", 3)
    if not doc["scenes"]:
        raise nv.Stop(f"{nv.SCRIPT_FILE} has no '## Slide N' scenes.", 2)
    return doc["scenes"]


def plan(folder: Path, model: str, voice: str, style: str | None) -> list[dict]:
    pairs = nv.load_pronunciations(folder)
    scenes = []
    for sc in approved_scenes(folder):
        sentences = []
        for s in nv.split_sentences(sc["text"]):
            spoken = nv.spoken_form(s, pairs)
            key = nv.clip_key(model, voice, style, spoken)
            sentences.append({"text": s, "spoken": spoken, "file": f"{nv.AUDIO_DIR}/{key}.wav"})
        scenes.append({"slide": sc["slide"], "sentences": sentences})
    return scenes


def money(x: float) -> str:
    return f"${x:.3f}" if x < 1 else f"${x:.2f}"


def price_note() -> str:
    text_rate, audio_rate, period = nv.price_today()
    return (f"at Google's paid-tier price (${audio_rate:.2f} per million audio tokens "
            f"{period}); the free tier charges nothing")


# --------------------------------------------------------------------------- commands

def cmd_test(args) -> int:
    folder = nv.folder_arg(args.folder)
    sender = Sender(args.model, args.voice or nv.DEFAULT_VOICE, args.style)
    frames = sender.send(TEST_SENTENCE, "the test sentence")
    out = folder / "voice-test.wav"
    nv.write_wav(out, frames)
    secs = nv.wav_seconds(out)
    nv.say(f"Voice test: {secs:.1f} seconds of speech saved as {out} "
           f"({args.voice or nv.DEFAULT_VOICE} voice, model {args.model}).")
    return 0


def cmd_samples(args) -> int:
    folder = nv.folder_arg(args.folder)
    scenes = approved_scenes(folder)
    spoken = [s for s in scenes if s["text"]]
    if not spoken:
        raise nv.Stop("every scene in the script is empty.", 2)
    if args.scene is not None:
        match = [s for s in scenes if s["slide"] == args.scene]
        if not match or not match[0]["text"]:
            raise nv.Stop(f"slide {args.scene} has no narration in the script.", 2)
        scene = match[0]
    else:
        scene = max(spoken, key=lambda s: nv.word_count(s["text"]))
    voices = [v.strip() for v in args.voices.split(",") if v.strip()]
    if not voices:
        raise nv.Stop("name at least one voice with --voices.", 2)
    pairs = nv.load_pronunciations(folder)
    text = " ".join(nv.spoken_form(s, pairs) for s in nv.split_sentences(scene["text"]))
    words = nv.word_count(scene["text"])
    nv.say(f"Reading slide {scene['slide']}'s scene ({words} words) in {len(voices)} "
           f"voice(s): {nv.listing(voices)}.")
    sender = Sender(args.model, voices[0], args.style, args.pause)
    for v in voices:
        if v not in nv.KNOWN_VOICES and v != voices[0]:
            nv.warn(f"Note: {v} is not on the list of Gemini voices this skill knows; "
                    "trying it anyway.")
        sender.voice = v
        frames = sender.send(text, f"the {v} sample")
        out = folder / "samples" / f"slide-{scene['slide']:02d}-{v}.wav"
        nv.write_wav(out, frames)
        secs = nv.wav_seconds(out)
        nv.say(f"  {v:<14} {secs:5.1f} seconds, {words / (secs / 60):.0f} words a minute  "
               f"samples/{out.name}")
    nv.say(f"Cost of these samples: about {money(sender.cost())}, {price_note()}.")
    return 0


def cmd_script(args) -> int:
    folder = nv.folder_arg(args.folder)
    voice = args.voice or nv.DEFAULT_VOICE
    scenes = plan(folder, args.model, voice, args.style)
    redo = set(args.redo or [])
    unknown = redo - {s["slide"] for s in scenes}
    if unknown:
        raise nv.Stop(f"--redo names slide(s) not in the script: "
                      f"{', '.join(str(n) for n in sorted(unknown))}", 2)
    to_send, reused = [], 0
    seen = set()
    for sc in scenes:
        for i, s in enumerate(sc["sentences"], 1):
            path = folder / s["file"]
            fresh = sc["slide"] in redo and s["file"] not in seen
            if path.is_file() and not fresh:
                reused += 1
            elif s["file"] in seen:
                reused += 1        # the same sentence earlier in this run
            else:
                to_send.append((sc["slide"], i, s))
            seen.add(s["file"])
    words_to_send = sum(nv.word_count(s["spoken"]) for _, _, s in to_send)
    chars_to_send = sum(len(s["spoken"]) for _, _, s in to_send)
    est_s = words_to_send / nv.WORDS_PER_MINUTE_PLAN * 60
    n_sentences = sum(len(sc["sentences"]) for sc in scenes)
    if args.dry_run:
        nv.say(f"Dry run, {voice} voice: {n_sentences} sentences in {len(scenes)} scenes; "
               f"{len(to_send)} to send ({words_to_send} words, about {est_s:.0f} seconds of "
               f"speech), {reused} already recorded.")
        nv.say(f"Estimated cost: about {money(nv.estimate_cost(est_s, chars_to_send))}, "
               f"{price_note()}. Nothing was sent.")
        return 0

    sender = Sender(args.model, voice, args.style, args.pause) if to_send else None
    if to_send:
        nv.say(f"Recording {len(to_send)} sentence(s) in the {voice} voice; "
               f"{reused} already recorded.")
    else:
        nv.say(f"Nothing new to record: all {n_sentences} sentences are already recorded "
               f"in the {voice} voice. Nothing was sent.")
    sent_seconds = 0.0
    for slide, i, s in to_send:
        frames = sender.send(s["spoken"], f"slide {slide}, sentence {i}")
        nv.write_wav(folder / s["file"], frames)
        sent_seconds += len(frames) / (nv.SAMPLE_RATE * nv.SAMPLE_WIDTH)
        nv.say(f"  slide {slide}, sentence {i}: done")

    # The manifest build_video.py reads: every sentence's clip, length, and speech span.
    total_words = 0
    report = []
    for sc in scenes:
        for s in sc["sentences"]:
            params, frames = nv.read_wav((folder / s["file"]).read_bytes())
            secs = len(frames) / (params[2] * params[1] * params[0])
            start, end = nv.speech_bounds(frames, params[2])
            s.update({"seconds": round(secs, 3), "speech_start": round(start, 3),
                      "speech_end": round(end, 3)})
            total_words += nv.word_count(s["text"])
        scene_s = nv.planned_length([sc]) - nv.LEAD_IN - nv.END_HOLD
        report.append((sc["slide"], scene_s, len(sc["sentences"])))
    length = nv.planned_length(scenes)
    wpm = total_words / (length / 60) if length else 0.0
    nv.write_json(folder / nv.AUDIO_DIR / nv.CLIPS_FILE, {
        "version": 1, "model": args.model, "voice": voice, "style": args.style,
        "scenes": scenes, "planned_seconds": round(length, 2), "words": total_words,
        "words_per_minute": round(wpm, 1)})

    nv.say("")
    for slide, secs, n in report:
        nv.say(f"  slide {slide:>2}: {secs:5.1f} seconds, {n} sentence(s)")
    whole = int(round(length))
    nv.say(f"Video length with pauses: about {whole} seconds ({whole // 60}:{whole % 60:02d}), "
           f"{total_words} words, {wpm:.0f} words a minute.")
    if to_send:
        nv.say(f"Sent this run: {len(to_send)} sentence(s), {sent_seconds:.1f} seconds of "
               f"audio, {sender.audio_tokens} audio tokens, about {money(sender.cost())}, "
               f"{price_note()}.")
    nv.say(f"Wrote {nv.AUDIO_DIR}/{nv.CLIPS_FILE}. Next: build_video.py.")
    return 0


def main() -> int:
    ap = argparse.ArgumentParser(description="Voice the approved script with Gemini.")
    ap.add_argument("command", choices=("samples", "script", "test"))
    ap.add_argument("--folder", help="the video's folder (default: the current folder)")
    ap.add_argument("--model", default=nv.DEFAULT_MODEL)
    ap.add_argument("--voice", help=f"voice for 'script' and 'test' (default {nv.DEFAULT_VOICE})")
    ap.add_argument("--voices", default="Charon,Kore,Puck", help="voices for 'samples'")
    ap.add_argument("--scene", type=int, help="slide number of the scene 'samples' reads")
    ap.add_argument("--style", help="optional reading direction, e.g. 'at a calm, measured pace'")
    ap.add_argument("--redo", type=int, nargs="+", metavar="SLIDE",
                    help="record these slides' scenes again even if unchanged")
    ap.add_argument("--dry-run", action="store_true", help="report what would be sent; send nothing")
    ap.add_argument("--pause", type=float, default=0.0, help="seconds to wait between requests")
    args = ap.parse_args()
    return {"test": cmd_test, "samples": cmd_samples, "script": cmd_script}[args.command](args)


if __name__ == "__main__":
    nv.run_main(main)

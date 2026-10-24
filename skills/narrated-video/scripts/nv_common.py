"""nv_common.py: helpers shared by the narrated-video scripts. Imported, never run.

Holds the script.md format, sentence splitting, pronunciation fixes, the location of
ffmpeg and ffprobe, the optional private Python environment, and the voice service's
model name and prices, so every script agrees on them.
"""

from __future__ import annotations

import hashlib
import io
import json
import os
import re
import shutil
import subprocess
import sys
from pathlib import Path

# --------------------------------------------------------------------------- settings

# Google's Gemini text-to-speech model. If Google renames it, pass --model to voice.py
# with the name on https://ai.google.dev/gemini-api/docs/speech-generation.
DEFAULT_MODEL = "gemini-3.8-flash-tts"
DEFAULT_VOICE = "Charon"
KEY_VARIABLE = "GEMINI_API_KEY"
# Where SKILL.md's key-storing commands put the key: a Mac Keychain item with this
# service name and the user's account name, or a Windows user environment variable.
KEYCHAIN_SERVICE = "GEMINI_API_KEY"


def get_key() -> tuple[str, str]:
    """(key, where it was found), or ('', '') when it is in none of the places below.
    The environment variable first; then, so that a session started before the key was
    stored needs no restart, the Mac Keychain item or the Windows account setting that
    the key-storing commands write. The value is never printed."""
    value = os.environ.get(KEY_VARIABLE, "").strip()
    if value:
        return value, "the environment"
    if sys.platform == "darwin":
        account = os.environ.get("USER") or ""
        try:
            import getpass
            account = account or getpass.getuser()
            proc = subprocess.run(["security", "find-generic-password", "-a", account,
                                   "-s", KEYCHAIN_SERVICE, "-w"],
                                  capture_output=True, text=True, timeout=20)
            if proc.returncode == 0 and proc.stdout.strip():
                return proc.stdout.strip(), "the Mac Keychain"
        except (OSError, subprocess.SubprocessError, KeyError):
            pass
    if os.name == "nt":
        try:
            import winreg
            with winreg.OpenKey(winreg.HKEY_CURRENT_USER, "Environment") as k:
                stored, _ = winreg.QueryValueEx(k, KEY_VARIABLE)
            if isinstance(stored, str) and stored.strip():
                return stored.strip(), "the Windows account settings"
        except OSError:
            pass
    return "", ""

# The 30 prebuilt voices listed on Google's speech-generation page, October 2026. A name
# not on this list is tried anyway, with a warning, in case Google has added voices.
KNOWN_VOICES = (
    "Zephyr", "Puck", "Charon", "Kore", "Fenrir", "Leda", "Orus", "Aoede", "Callirrhoe",
    "Autonoe", "Enceladus", "Iapetus", "Umbriel", "Algieba", "Despina", "Erinome",
    "Algenib", "Rasalgethi", "Laomedeia", "Achernar", "Alnilam", "Schedar", "Gacrux",
    "Pulcherrima", "Achird", "Zubenelgenubi", "Vindemiatrix", "Sadachbia", "Sadaltager",
    "Sulafat",
)

# Paid-tier prices for the default model (https://ai.google.dev/gemini-api/docs/pricing,
# checked October 2026), in US dollars per million tokens. Audio is counted at 25 tokens
# a second. The free tier charges nothing. Each row: (first day it applies, text, audio,
# how the period is described).
PRICES = (
    ("2026-01-01", 0.50, 9.00, "through December 31, 2026"),
    ("2027-01-01", 1.00, 18.00, "from January 1, 2027"),
)
AUDIO_TOKENS_PER_SECOND = 25

WORDS_PER_MINUTE_PLAN = 150     # planning pace for a script; a voice's own pace is measured

# The video's timeline (build_video.py), held here so voice.py can predict the length.
LEAD_IN = 0.5              # seconds before the first word
END_HOLD = 1.0             # seconds after the last word
SENTENCE_GAP = 0.25        # pause added between sentences in a scene
SCENE_GAP = 0.6            # pause between scenes; the slide changes halfway through it
CLIP_PAD_IN = 0.05         # silence kept before a clip's first sound
CLIP_PAD_OUT = 0.15        # and after its last
SILENT_HOLD = 3.0          # a scene with no narration


def planned_length(scenes: list[dict], scene_gap: float = SCENE_GAP) -> float:
    """Seconds of video for recorded scenes (each {'sentences': [{'speech_start',
    'speech_end'}, ...]}), on build_video.py's timeline."""
    total = LEAD_IN + END_HOLD + scene_gap * max(len(scenes) - 1, 0)
    for sc in scenes:
        clips = sc["sentences"]
        if not clips:
            total += SILENT_HOLD
            continue
        total += SENTENCE_GAP * (len(clips) - 1)
        for c in clips:
            total += (c["speech_end"] - c["speech_start"]) + CLIP_PAD_IN + CLIP_PAD_OUT
    return total

SAMPLE_RATE = 24000             # Gemini's speech output: 24 kHz, mono, 16-bit
SAMPLE_WIDTH = 2
CHANNELS = 1

SCRIPT_FILE = "script.md"
PRONOUNCE_FILE = "pronounce.txt"
SLIDES_DIR = "slides"
AUDIO_DIR = "audio"
CLIPS_FILE = "clips.json"


class Stop(Exception):
    """A stop with an exit code and a plain-language message."""

    def __init__(self, message: str, code: int = 1):
        super().__init__(message)
        self.code = code


def safe_console() -> None:
    """Keep a Windows console from failing on a character it cannot show."""
    for stream in (sys.stdout, sys.stderr):
        try:
            stream.reconfigure(errors="replace")
        except (AttributeError, ValueError):
            pass


def listing(items) -> str:
    """'a', 'a and b', or 'a, b, and c'."""
    items = list(items)
    if len(items) < 3:
        return " and ".join(items)
    return ", ".join(items[:-1]) + ", and " + items[-1]


def say(msg: str = "") -> None:
    print(msg, flush=True)


def warn(msg: str) -> None:
    print(msg, file=sys.stderr, flush=True)


def run_main(main) -> None:
    """Run a script's main(), turning a Stop into its message and exit code."""
    safe_console()
    try:
        code = main()
    except Stop as e:
        warn(f"Stopped: {e}")
        code = e.code
    except KeyboardInterrupt:
        warn("Stopped by the user.")
        code = 130
    except PermissionError as e:
        where = e.filename or "a file"
        warn(f"Stopped: {where} could not be written. Close it if another program has it "
             "open (a media player, for example), check that this folder is one you can "
             "write to, and run the command again.")
        code = 1
    sys.exit(code or 0)


# --------------------------------------------------------------------------- python env

def venv_dir() -> Path:
    """Where check_setup.py --install puts a private Python environment when the
    computer's own Python cannot take new packages. NARRATED_VIDEO_VENV overrides it."""
    override = os.environ.get("NARRATED_VIDEO_VENV", "").strip()
    if override:
        return Path(override).expanduser()
    return Path.home() / ".narrated-video" / "venv"


def venv_python(base: Path | None = None) -> Path:
    base = base or venv_dir()
    if os.name == "nt":
        return base / "Scripts" / "python.exe"
    return base / "bin" / "python"


def missing_modules(modules: list[str]) -> list[str]:
    missing = []
    for name in modules:
        try:
            __import__(name)
        except Exception:
            missing.append(name)
    return missing


def need_modules(modules: list[str], script: str) -> None:
    """Import the packages a script needs. Where this Python lacks them and the private
    environment exists, run the same command again inside it; otherwise stop and say
    how to install them."""
    missing = missing_modules(modules)
    if not missing:
        return
    vpy = venv_python()
    if vpy.is_file() and os.environ.get("NARRATED_VIDEO_RELAUNCHED") != "1":
        env = dict(os.environ, NARRATED_VIDEO_RELAUNCHED="1")
        proc = subprocess.run([str(vpy), str(Path(script).resolve()), *sys.argv[1:]], env=env)
        sys.exit(proc.returncode)
    names = listing(PACKAGE_FOR.get(m, m) for m in missing)
    raise Stop(f"this Python is missing {names}. Run check_setup.py --install, "
               f"then run this command again.", 4)


# Import name to the package's own name, and to what pip installs. PyMuPDF 2 pulls in
# onnxruntime and has no build for Intel Macs or Windows on ARM, so it is held at 1.x.
PACKAGE_FOR = {"pymupdf": "PyMuPDF", "PIL": "Pillow", "pptx": "python-pptx",
               "certifi": "certifi"}
INSTALL_SPEC = {"pymupdf": "pymupdf<2", "PIL": "pillow", "pptx": "python-pptx",
                "certifi": "certifi"}


# --------------------------------------------------------------------------- tools

def _windows_ffmpeg_candidates(name: str) -> list[Path]:
    out = []
    local = os.environ.get("LOCALAPPDATA")
    if local:
        out.append(Path(local) / "Microsoft" / "WinGet" / "Links" / f"{name}.exe")
        pkgs = Path(local) / "Microsoft" / "WinGet" / "Packages"
        if pkgs.is_dir():
            out += sorted(pkgs.glob(f"Gyan.FFmpeg*/*/bin/{name}.exe"), reverse=True)
    program_files = Path(os.environ.get("ProgramFiles", r"C:\Program Files"))
    out.append(program_files / "WinGet" / "Links" / f"{name}.exe")
    machine_pkgs = program_files / "WinGet" / "Packages"
    if machine_pkgs.is_dir():
        out += sorted(machine_pkgs.glob(f"Gyan.FFmpeg*/*/bin/{name}.exe"), reverse=True)
    for root in (os.environ.get("ProgramData", r"C:\ProgramData"),):
        out.append(Path(root) / "chocolatey" / "bin" / f"{name}.exe")
    out.append(Path.home() / "scoop" / "shims" / f"{name}.exe")
    out.append(Path(r"C:\ffmpeg\bin") / f"{name}.exe")
    return out


def find_tool(name: str) -> str | None:
    """ffmpeg or ffprobe: on the PATH, else where the usual installers put it (a new
    install on Windows is often not on the PATH until a new terminal is opened)."""
    found = shutil.which(name)
    if found:
        return found
    if os.name == "nt":
        candidates = _windows_ffmpeg_candidates(name)
    else:
        candidates = [Path("/opt/homebrew/bin") / name, Path("/usr/local/bin") / name,
                      Path("/opt/homebrew/opt/ffmpeg-full/bin") / name]
    for c in candidates:
        if c.is_file():
            return str(c)
    return None


def need_tool(name: str) -> str:
    exe = find_tool(name)
    if not exe:
        raise Stop(f"{name} was not found on this computer. Run check_setup.py to see how "
                   f"to install ffmpeg (it includes {name}).", 5)
    return exe


# --------------------------------------------------------------------------- files

def read_text(path: Path) -> str:
    """Text written on any computer: UTF-8 with or without a byte-order mark, UTF-16
    (Notepad's and Windows PowerShell's 'Unicode'), Windows or Mac line endings."""
    data = Path(path).read_bytes()
    encodings = ["utf-8-sig", "cp1252"]
    if data[:2] in (b"\xff\xfe", b"\xfe\xff"):
        encodings.insert(0, "utf-16")
    elif data[:200].count(b"\x00") > len(data[:200]) // 4:
        encodings.insert(0, "utf-16-le" if data[1:2] == b"\x00" else "utf-16-be")
    for enc in encodings:
        try:
            text = data.decode(enc)
            break
        except UnicodeDecodeError:
            continue
    else:
        text = data.decode("utf-8", errors="replace")
    return text.replace("\r\n", "\n").replace("\r", "\n")


def write_text(path: Path, text: str, newline: str = "\n") -> None:
    """Write UTF-8 with the given line ending on every system (Python would otherwise
    turn each \\n into \\r\\n on Windows)."""
    Path(path).parent.mkdir(parents=True, exist_ok=True)
    tmp = Path(str(path) + ".part")
    with open(tmp, "w", encoding="utf-8", newline=newline) as f:
        f.write(text)
    replace_file(tmp, Path(path))


def replace_file(tmp: Path, dst: Path) -> None:
    """Move a finished file into place. On Windows a file another program has open
    (a media player, a virus scan, a sync client) refuses to be replaced, often only
    for a moment, so try for about two seconds before stopping with a plain message."""
    import time
    for attempt in range(8):
        try:
            os.replace(tmp, dst)
            return
        except PermissionError:
            time.sleep(0.25)
    try:
        tmp.unlink()
    except OSError:
        pass
    raise Stop(f"{dst.name} is open in another program. Close it and run the command again.", 1)


def write_json(path: Path, doc) -> None:
    write_text(path, json.dumps(doc, indent=2, ensure_ascii=False) + "\n")


def folder_arg(value: str | None) -> Path:
    folder = Path(value).expanduser() if value else Path.cwd()
    if not folder.is_dir():
        raise Stop(f"the folder does not exist: {folder}", 2)
    return folder.resolve()


# --------------------------------------------------------------------------- script.md

HEADING_RE = re.compile(r"^\s*#{2,3}\s*slide\s+(\d+)\b.*$", re.IGNORECASE)
STATUS_RE = re.compile(r"^\s*status\s*:\s*(\w+)", re.IGNORECASE)


def parse_script(path: Path) -> dict:
    """script.md: an optional title and a 'Status: draft' or 'Status: approved' line,
    then one '## Slide N' heading per slide with the words the voice reads beneath it.
    Returns {"status": str or None, "scenes": [{"slide": N, "text": str}, ...]}."""
    if not Path(path).is_file():
        raise Stop(f"no script found at {path}", 2)
    status = None
    scenes: list[dict] = []
    current = None
    # Drop HTML comments, a single line or several, so a note left in the file is
    # never read aloud or sent to the voice service.
    body = re.sub(r"<!--.*?(-->|\Z)", "", read_text(path), flags=re.DOTALL)
    for line in body.split("\n"):
        m = HEADING_RE.match(line)
        if m:
            current = {"slide": int(m.group(1)), "lines": []}
            scenes.append(current)
            continue
        if current is None:
            s = STATUS_RE.match(line)
            if s:
                status = s.group(1).lower()
            continue
        stripped = line.strip()
        if not stripped or stripped.startswith("#"):
            continue
        current["lines"].append(stripped)
    for sc in scenes:
        text = " ".join(sc.pop("lines"))
        text = text.replace("**", "").replace("__", "")
        text = re.sub(r"(?<!\w)\*(\S[^*]*?)\*(?!\w)", r"\1", text)
        sc["text"] = re.sub(r"\s+", " ", text).strip()
    return {"status": status, "scenes": scenes}


ABBREVIATIONS = {"mr.", "mrs.", "ms.", "dr.", "prof.", "st.", "vs.", "etc.", "e.g.", "i.e.",
                 "inc.", "co.", "corp.", "ltd.", "jr.", "sr.", "no.", "approx.", "dept."}
_CLOSERS = "\"')]}\u201d\u2019"
_NEXT_STARTS = re.compile(r"^[\"'(\[\u201c\u2018]?[A-Z0-9]")


def split_sentences(text: str) -> list[str]:
    """Split narration into sentences, one audio clip each."""
    words = text.split()
    out, cur = [], []
    for i, w in enumerate(words):
        cur.append(w)
        core = w.rstrip(_CLOSERS)
        if not core.endswith((".", "!", "?")):
            continue
        if core.lower() in ABBREVIATIONS or re.fullmatch(r"(?:[A-Za-z]\.){2,}", core):
            continue
        nxt = words[i + 1] if i + 1 < len(words) else None
        if nxt is None or _NEXT_STARTS.match(nxt):
            out.append(" ".join(cur))
            cur = []
    if cur:
        out.append(" ".join(cur))
    return out


def load_pronunciations(folder: Path) -> list[tuple[str, str]]:
    """pronounce.txt: one 'written = spoken' pair per line, for words the voice misreads.
    The spoken form goes to the voice; the captions keep the written form."""
    path = folder / PRONOUNCE_FILE
    if not path.is_file():
        return []
    pairs = []
    for n, line in enumerate(read_text(path).split("\n"), 1):
        line = line.strip()
        if not line or line.startswith("#"):
            continue
        if "=" not in line:
            raise Stop(f"{PRONOUNCE_FILE} line {n} has no '=': write it as  written = spoken", 2)
        written, spoken = (p.strip() for p in line.split("=", 1))
        if written and spoken:
            pairs.append((written, spoken))
    return pairs


def spoken_form(sentence: str, pairs: list[tuple[str, str]]) -> str:
    out = sentence
    for written, spoken in pairs:
        out = re.sub(r"(?<!\w)" + re.escape(written) + r"(?!\w)", lambda m: spoken, out)
    return out


def word_count(text: str) -> int:
    return len(text.split())


# --------------------------------------------------------------------------- slides

def slide_images(folder: Path) -> list[Path]:
    d = folder / SLIDES_DIR
    if not d.is_dir():
        return []
    return sorted(d.glob("slide-*.png"), key=lambda p: int(re.sub(r"\D", "", p.stem) or 0))


# --------------------------------------------------------------------------- audio

def clip_key(model: str, voice: str, style: str | None, spoken: str) -> str:
    blob = json.dumps([model, voice, style or "", spoken], ensure_ascii=False)
    return hashlib.sha256(blob.encode("utf-8")).hexdigest()[:16]


def price_today(today: str | None = None) -> tuple[float, float, str]:
    """(text, audio) dollars per million tokens on the paid tier, and the period's description."""
    from datetime import date
    today = today or date.today().isoformat()
    row = PRICES[0]
    for r in PRICES:
        if today >= r[0]:
            row = r
    return row[1], row[2], row[3]


def estimate_cost(audio_seconds: float, text_chars: int) -> float:
    text_rate, audio_rate, _ = price_today()
    audio_tokens = audio_seconds * AUDIO_TOKENS_PER_SECOND
    text_tokens = text_chars / 4.0
    return (audio_tokens * audio_rate + text_tokens * text_rate) / 1_000_000


def read_wav(data: bytes):
    """(params, frames) of a WAV held in memory."""
    import wave
    with wave.open(io.BytesIO(data), "rb") as w:
        return (w.getnchannels(), w.getsampwidth(), w.getframerate()), w.readframes(w.getnframes())


def write_wav(path: Path, frames: bytes, rate: int = SAMPLE_RATE,
              channels: int = CHANNELS, width: int = SAMPLE_WIDTH) -> None:
    import wave
    Path(path).parent.mkdir(parents=True, exist_ok=True)
    tmp = Path(str(path) + ".part")
    with wave.open(str(tmp), "wb") as w:
        w.setnchannels(channels)
        w.setsampwidth(width)
        w.setframerate(rate)
        w.writeframes(frames)
    replace_file(tmp, Path(path))


def wav_seconds(path: Path) -> float:
    import wave
    with wave.open(str(path), "rb") as w:
        return w.getnframes() / float(w.getframerate())


def speech_bounds(frames: bytes, rate: int = SAMPLE_RATE, window_s: float = 0.01,
                  floor: float = 0.02) -> tuple[float, float]:
    """Seconds from the clip's start to the first and the last stretch of speech:
    the first and last 10 ms window whose peak passes 2 percent of the clip's peak."""
    import array
    samples = array.array("h")
    samples.frombytes(frames[: len(frames) - len(frames) % 2])
    if sys.byteorder == "big":
        samples.byteswap()
    n = len(samples)
    if n == 0:
        return 0.0, 0.0
    peak = max(abs(min(samples)), abs(max(samples))) or 1
    limit = max(int(peak * floor), 200)
    step = max(int(rate * window_s), 1)
    first = last = None
    for start in range(0, n, step):
        chunk = samples[start:start + step]
        if max(abs(min(chunk)), abs(max(chunk))) >= limit:
            if first is None:
                first = start
            last = min(start + step, n)
    if first is None:
        return 0.0, n / rate
    return first / rate, last / rate

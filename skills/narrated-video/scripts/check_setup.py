#!/usr/bin/env python3
"""check_setup.py: confirm this computer can make a narrated video (step 1).

Usage:
  python3 check_setup.py                 report what is present and what is missing
  python3 check_setup.py --install       also install the missing Python packages
  python3 check_setup.py --test-voice    also voice one short sentence as voice-test.wav
                                         in the video's folder (--folder, default the
                                         current folder; needs the key)

Checks: Python 3.9 or later; ffmpeg and ffprobe, and ffmpeg's H.264 encoder; the
Python packages PyMuPDF, Pillow, python-pptx, and certifi; and whether the Gemini key
can be found: in the GEMINI_API_KEY environment variable, or else where SKILL.md's
key-storing commands put it (a Mac Keychain item named GEMINI_API_KEY, or the Windows
user environment), so a session started before the key was stored needs no restart.
The key's value is never printed. The voice step itself uses only Python's standard
library.

--install puts the packages in this Python. Where this Python refuses new packages
(Homebrew's Python on a Mac does), it makes a private environment in
~/.narrated-video/venv instead and installs them there; the other scripts find it
on their own. NARRATED_VIDEO_VENV moves that environment elsewhere. PyMuPDF is held
below version 2, whose extra dependencies have no installable build for several
common computers (Intel Macs, Windows on ARM, and the newest Python).

Exit codes: 0 ready; 1 something is missing (the report says what and how to fix it).
"""

from __future__ import annotations

import argparse
import os
import platform
import shutil
import subprocess
import sys
from pathlib import Path

sys.dont_write_bytecode = True      # leave no cache files in the skill's folder
sys.path.insert(0, str(Path(__file__).resolve().parent))
import nv_common as nv  # noqa: E402

REQUIRED = ["pymupdf", "PIL", "pptx", "certifi"]


def ffmpeg_report(lines: list[str], problems: list[str]) -> None:
    ffmpeg = nv.find_tool("ffmpeg")
    ffprobe = nv.find_tool("ffprobe")
    if not ffmpeg or not ffprobe:
        problems.append("ffmpeg")
        lines.append("ffmpeg:    not found")
        return
    try:
        first = subprocess.run([ffmpeg, "-hide_banner", "-version"], capture_output=True,
                               text=True, errors="replace", timeout=60).stdout.splitlines()[0]
        encoders = subprocess.run([ffmpeg, "-hide_banner", "-encoders"], capture_output=True,
                                  text=True, errors="replace", timeout=60).stdout
    except (OSError, subprocess.SubprocessError, IndexError):
        problems.append("ffmpeg")
        lines.append(f"ffmpeg:    found at {ffmpeg} but it did not run")
        return
    lines.append(f"ffmpeg:    {first.strip()}  ({ffmpeg})")
    if " libx264 " not in encoders:
        problems.append("libx264")
        lines.append("           this ffmpeg has no H.264 encoder (libx264); install the full build")
    if not shutil.which("ffmpeg"):
        lines.append("           (not on the PATH yet; the scripts find it anyway, and a new "
                     "terminal will too)")


def python_report(lines: list[str], problems: list[str]) -> list[str]:
    v = sys.version_info
    lines.append(f"Python:    {v.major}.{v.minor}.{v.micro}  ({sys.executable})")
    if v < (3, 9):
        problems.append("python")
        lines.append("           Python 3.9 or later is needed")
    missing = nv.missing_modules(REQUIRED)
    vpy = nv.venv_python()
    if missing and vpy.is_file():
        probe = subprocess.run([str(vpy), "-c", "import " + ", ".join(REQUIRED)],
                               capture_output=True, text=True, errors="replace")
        if probe.returncode == 0:
            lines.append(f"Packages:  installed in the private environment ({vpy})")
            return []
    if missing:
        lines.append(f"Packages:  missing {nv.listing(nv.PACKAGE_FOR[m] for m in missing)}")
    else:
        lines.append("Packages:  PyMuPDF, Pillow, python-pptx, and certifi are installed")
    return missing


def externally_managed() -> bool:
    import sysconfig
    stdlib = sysconfig.get_paths().get("stdlib", "")
    return bool(stdlib) and (Path(stdlib) / "EXTERNALLY-MANAGED").is_file()


def pip_install(python: str, packages: list[str]) -> bool:
    cmd = [python, "-m", "pip", "install", "--upgrade", "--prefer-binary",
           *[nv.INSTALL_SPEC[p] for p in packages]]
    return subprocess.run(cmd).returncode == 0


def install(missing: list[str]) -> bool:
    if not externally_managed() and os.environ.get("NARRATED_VIDEO_VENV") is None:
        nv.say(f"Installing {nv.listing(nv.PACKAGE_FOR[m] for m in missing)} into this Python ...")
        if pip_install(sys.executable, missing):
            return True
        nv.say("Installing into this Python failed; trying a private environment instead.")
    target = nv.venv_dir()
    vpy = nv.venv_python(target)
    if not vpy.is_file():
        nv.say(f"Making a private Python environment at {target} ...")
        if subprocess.run([sys.executable, "-m", "venv", str(target)]).returncode != 0:
            nv.warn("Could not make the private environment. On Linux, install the "
                    "python3-venv package; elsewhere, reinstall Python from python.org.")
            return False
    nv.say(f"Installing {nv.listing(nv.PACKAGE_FOR[m] for m in REQUIRED)} there ...")
    subprocess.run([str(vpy), "-m", "pip", "install", "--quiet", "--upgrade", "pip"])
    return pip_install(str(vpy), REQUIRED)


def key_report(lines: list[str], problems: list[str]) -> bool:
    value, where = nv.get_key()
    if not value:
        problems.append("key")
        lines.append(f"Gemini key: not found ({nv.KEY_VARIABLE} is not set, and no key is "
                     "stored in the Mac Keychain or the Windows account settings)")
        return False
    if any(c in value for c in " \"'\n\t"):
        problems.append("key")
        lines.append(f"Gemini key: found in {where} but it contains spaces or quote marks; "
                     "store it again without them")
        return False
    lines.append(f"Gemini key: found in {where} (value not shown)")
    return True


def test_voice(folder: Path) -> int:
    script = Path(__file__).resolve().parent / "voice.py"
    return subprocess.run([sys.executable, str(script), "test", "--folder",
                           str(folder)]).returncode


def main() -> int:
    ap = argparse.ArgumentParser(description="Check the tools a narrated video needs.")
    ap.add_argument("--install", action="store_true", help="install missing Python packages")
    ap.add_argument("--test-voice", action="store_true",
                    help="voice one short sentence as voice-test.wav in the video's folder")
    ap.add_argument("--folder", help="the video's folder (default: the current folder)")
    args = ap.parse_args()

    lines: list[str] = [f"Computer:  {platform.system()} {platform.release()} "
                        f"({platform.machine()})"]
    problems: list[str] = []
    missing = python_report(lines, problems)
    ffmpeg_report(lines, problems)
    key_ok = key_report(lines, problems)
    for line in lines:
        nv.say(line)

    if missing and args.install:
        nv.say("")
        if install(missing):
            nv.say("Packages installed.")
            missing = []
        else:
            nv.warn("The package install failed; the messages above say why.")
    if missing:
        problems.append("packages")

    if args.test_voice:
        nv.say("")
        if not key_ok:
            nv.say("Voice test skipped: the Gemini key was not found.")
        elif test_voice(nv.folder_arg(args.folder)) != 0:
            problems.append("voice")

    nv.say("")
    if not problems:
        nv.say("Ready: every tool the video needs is in place.")
        return 0
    fixes = {
        "python": "Install Python 3 (Mac: brew install python; Windows: the Python install "
                  "manager from python.org/downloads), then open a new terminal.",
        "ffmpeg": "Install ffmpeg (Mac: brew install ffmpeg; Windows: winget install --id "
                  "Gyan.FFmpeg -e --accept-source-agreements --accept-package-agreements), "
                  "then run this check again; the scripts find a new install without a "
                  "restart.",
        "libx264": "This ffmpeg cannot write the video format phones and browsers play "
                   "(H.264); install the standard build (Mac: brew install ffmpeg; Windows: "
                   "winget install --id Gyan.FFmpeg -e --accept-source-agreements "
                   "--accept-package-agreements).",
        "packages": "Run this script again with --install.",
        "key": "Store the Gemini key (SKILL.md, Step 1, 'Storing the key') and run this "
               "check again.",
        "voice": "The voice test failed; the message above says why.",
    }
    nv.say("Not ready yet. To fix:")
    for p in dict.fromkeys(problems):
        nv.say(f"- {fixes[p]}")
    return 1


if __name__ == "__main__":
    nv.run_main(main)

#!/usr/bin/env python3
"""
log_run.py: Append-only JSONL run log for skill self-improvement signal.

Derived from the script archetypes in skill-engineer-master by Antony Evans (edge-brain-lite,
https://github.com/antonyevans/edge-brain-lite), CC BY 4.0.

Archetype. Copy into [skill]/scripts/ and rename if needed.

Usage:
  python log_run.py --log references/run-log.jsonl --status ok --note "3 options presented"
  echo '{"extra": "field"}' | python log_run.py --log references/run-log.jsonl --status fail --stdin-merge

Appends one JSONL line per call. Uses O_APPEND for crash-safe concurrent writes.
Never write secrets; log the fact of the run and structural outcomes, not user input.

Error taxonomy:
  exit 0: line appended
  exit 1: write failed (permissions, disk full, bad path)
  exit 2: bad arguments
"""

import argparse
import json
import os
import sys
from datetime import datetime, timezone
from pathlib import Path


def append_jsonl(path: Path, record: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    flags = os.O_WRONLY | os.O_CREAT | os.O_APPEND
    fd = os.open(str(path), flags, 0o644)  # O_APPEND: atomic concurrent appends on POSIX, safe-ish on Windows for small records.
    try:
        line = json.dumps(record, ensure_ascii=False) + "\n"
        os.write(fd, line.encode("utf-8"))
    finally:
        os.close(fd)


def main():
    parser = argparse.ArgumentParser(description="Append a run log entry")
    parser.add_argument("--log", required=True, help="Path to JSONL log file (relative to skill or absolute)")
    parser.add_argument("--status", required=True, choices=["ok", "fail", "partial"], help="Run outcome")
    parser.add_argument("--note", default="", help="One-line human-readable note")
    parser.add_argument("--phase", default="", help="Phase or step name where this event originated")
    parser.add_argument("--stdin-merge", action="store_true", help="Merge extra JSON from stdin (dict only)")
    ns = parser.parse_args()

    record = {
        "ts": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "status": ns.status,
    }
    if ns.note:
        record["note"] = ns.note
    if ns.phase:
        record["phase"] = ns.phase

    if ns.stdin_merge and not sys.stdin.isatty():
        try:
            extra = json.load(sys.stdin)
            if isinstance(extra, dict):
                for k, v in extra.items():
                    if k not in record:  # Core fields win to preserve the schema contract.
                        record[k] = v
            else:
                print("Error: --stdin-merge expects a JSON object. Got array or scalar.", file=sys.stderr)
                sys.exit(2)
        except json.JSONDecodeError as e:
            print(f"Error: --stdin-merge got invalid JSON ({e}). Pipe a valid JSON object or omit the flag.", file=sys.stderr)
            sys.exit(2)

    try:
        append_jsonl(Path(ns.log), record)
    except OSError as e:
        print(f"Error: could not append to {ns.log}: {e}. Check permissions and that the parent directory is writable.", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()

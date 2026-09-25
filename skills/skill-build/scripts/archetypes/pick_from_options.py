#!/usr/bin/env python3
"""
pick_from_options.py: Present N options and capture a structured choice.

Derived from the script archetypes in skill-engineer-master by Antony Evans (edge-brain-lite,
https://github.com/antonyevans/edge-brain-lite), CC BY 4.0.

Archetype. Copy into [skill]/scripts/ and rename (e.g., present_angle_options.py).

This script emits a structured JSON block describing the options. The calling
skill is expected to present those options to the user via AskUserQuestion (or
similar) and pass the selected index back via --confirm.

Two-phase usage (the skill runs this twice):

  Phase 1, propose:
    python pick_from_options.py propose --options options.json --output proposal.json

  Phase 2, confirm:
    python pick_from_options.py confirm --proposal proposal.json --choice 2 --output selection.json

Where options.json is a list of option objects:
  [
    {"label": "Option A", "summary": "Short pitch", "detail": "Long form"},
    ...
  ]

Error taxonomy:
  exit 0: proposal or confirmation succeeded
  exit 1: choice out of range or proposal missing
  exit 2: bad arguments or malformed options file
"""

import argparse
import json
import sys
from pathlib import Path

MIN_OPTIONS = 3  # Output-variation rule: never present fewer than 3 options at a decision point.
MAX_OPTIONS = 5  # More than 5 reliably overwhelms the chooser; keep the set small.


def cmd_propose(ns):
    try:
        options = json.loads(Path(ns.options).read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as e:
        print(f"Error: could not read options file {ns.options}: {e}", file=sys.stderr)
        sys.exit(2)

    if not isinstance(options, list):
        print("Error: options file must be a JSON array of option objects.", file=sys.stderr)
        sys.exit(2)

    if not (MIN_OPTIONS <= len(options) <= MAX_OPTIONS):
        print(
            f"Error: got {len(options)} options. Must be between {MIN_OPTIONS} and {MAX_OPTIONS} per the "
            f"output-variation rule; produce more variety or consolidate.",
            file=sys.stderr,
        )
        sys.exit(2)

    for idx, opt in enumerate(options):
        if not isinstance(opt, dict) or "label" not in opt or "summary" not in opt:
            print(
                f"Error: option {idx} missing required fields 'label' and 'summary'. "
                f"Got: {opt}",
                file=sys.stderr,
            )
            sys.exit(2)

    proposal = {
        "kind": "option-set",
        "options": [
            {"index": i, "label": o["label"], "summary": o["summary"], "detail": o.get("detail", "")}
            for i, o in enumerate(options)
        ],
    }

    if ns.output:
        Path(ns.output).write_text(json.dumps(proposal, indent=2), encoding="utf-8")
    print(json.dumps(proposal, indent=2))


def cmd_confirm(ns):
    try:
        proposal = json.loads(Path(ns.proposal).read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as e:
        print(f"Error: could not read proposal {ns.proposal}: {e}", file=sys.stderr)
        sys.exit(2)

    opts = proposal.get("options", [])
    if not (0 <= ns.choice < len(opts)):
        print(
            f"Error: choice {ns.choice} out of range (0..{len(opts) - 1}). "
            f"Re-present the options and capture a valid index.",
            file=sys.stderr,
        )
        sys.exit(1)

    selection = {"kind": "selection", "choice": opts[ns.choice]}
    if ns.output:
        Path(ns.output).write_text(json.dumps(selection, indent=2), encoding="utf-8")
    print(json.dumps(selection, indent=2))


def main():
    parser = argparse.ArgumentParser(description="Present N options and capture a choice")
    sub = parser.add_subparsers(dest="cmd", required=True)

    p_prop = sub.add_parser("propose", help="Emit a structured option set")
    p_prop.add_argument("--options", required=True, help="Path to JSON array of options")
    p_prop.add_argument("--output", help="Write proposal to this path (also prints to stdout)")
    p_prop.set_defaults(func=cmd_propose)

    p_conf = sub.add_parser("confirm", help="Resolve a choice against a proposal")
    p_conf.add_argument("--proposal", required=True, help="Proposal JSON produced by 'propose'")
    p_conf.add_argument("--choice", required=True, type=int, help="Zero-based index of the chosen option")
    p_conf.add_argument("--output", help="Write selection to this path (also prints to stdout)")
    p_conf.set_defaults(func=cmd_confirm)

    ns = parser.parse_args()
    ns.func(ns)


if __name__ == "__main__":
    main()

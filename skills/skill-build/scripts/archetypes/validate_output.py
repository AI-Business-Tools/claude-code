#!/usr/bin/env python3
"""
validate_output.py: Validate an output file against a JSON schema or a structural template.

Derived from the script archetypes in skill-engineer-master by Antony Evans (edge-brain-lite,
https://github.com/antonyevans/edge-brain-lite), CC BY 4.0.

Archetype. Copy into [skill]/scripts/ and rename to validate_<artifact>.py before editing.

Usage:
  python validate_output.py <output-file> --schema <schema.json>
  python validate_output.py <output-md-file> --sections "Summary,Plan,Risks"

Output: PASS summary to stdout on success. On failure: a self-correction message
explaining exactly what's missing, what was expected, and how to fix.

Error taxonomy:
  exit 0: output conforms
  exit 1: output does not conform (printed as self-correcting diagnosis)
  exit 2: bad arguments or unreadable files
"""

import argparse
import json
import re
import sys
from pathlib import Path


def validate_json_schema(output_path: Path, schema_path: Path) -> list[str]:
    """Validate a JSON output against a JSON Schema. Returns list of error messages (empty = pass)."""
    try:
        import jsonschema  # Optional dependency; only loaded if the skill needs JSON validation.
    except ImportError:
        return [
            "Required package 'jsonschema' not installed. "
            "Install it with `python3 -m pip install jsonschema` in the Python environment "
            "that runs this skill, then retry."
        ]

    try:
        output = json.loads(output_path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as e:
        return [f"{output_path} is not valid JSON ({e}). Fix JSON syntax before re-running."]
    except OSError as e:
        return [f"Could not read {output_path}: {e}. Check path and permissions."]

    try:
        schema = json.loads(schema_path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as e:
        return [f"Schema file {schema_path} is invalid ({e}). Fix the schema, not the output."]

    validator = jsonschema.Draft202012Validator(schema)
    errors = []
    for err in sorted(validator.iter_errors(output), key=lambda e: e.path):
        path = "$" + "".join(f".{p}" if isinstance(p, str) else f"[{p}]" for p in err.path)
        errors.append(f"{path}: {err.message}")
    return errors


def validate_markdown_sections(output_path: Path, required: list[str]) -> list[str]:
    """Ensure each required section (## Heading) appears in the markdown file."""
    try:
        text = output_path.read_text(encoding="utf-8")
    except OSError as e:
        return [f"Could not read {output_path}: {e}. Check path and permissions."]

    headings = set(re.findall(r"^##\s+(.+?)\s*$", text, re.MULTILINE))
    missing = [s for s in required if s not in headings]
    if missing:
        return [
            f"Missing required section(s): {', '.join(missing)}. "
            f"Add an `## {missing[0]}` heading (and any others) to the output and re-run."
        ]
    return []


def main():
    parser = argparse.ArgumentParser(description="Validate a skill output artifact")
    parser.add_argument("output", help="Path to output artifact")
    parser.add_argument("--schema", help="Path to JSON schema (for JSON outputs)")
    parser.add_argument("--sections", help="Comma-separated required markdown sections")
    ns = parser.parse_args()

    out_path = Path(ns.output)
    if not out_path.exists():
        print(f"Error: output file {out_path} does not exist. Check the path.", file=sys.stderr)
        sys.exit(2)

    if not ns.schema and not ns.sections:
        print("Error: pass --schema or --sections to specify what to validate against.", file=sys.stderr)
        sys.exit(2)

    errors = []
    if ns.schema:
        errors.extend(validate_json_schema(out_path, Path(ns.schema)))
    if ns.sections:
        required = [s.strip() for s in ns.sections.split(",") if s.strip()]
        errors.extend(validate_markdown_sections(out_path, required))

    if errors:
        print(f"FAIL: {len(errors)} validation error(s) in {out_path}")
        for e in errors:
            print(f"  - {e}")
        print()
        print("Fix the listed issues in the output file and re-run this validator.")
        sys.exit(1)

    print(f"PASS: {out_path} conforms.")


if __name__ == "__main__":
    main()

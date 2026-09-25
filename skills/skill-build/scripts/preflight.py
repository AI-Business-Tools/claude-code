#!/usr/bin/env python3
"""
preflight.py: automated pre-flight check for a Claude Code skill folder.

Usage: python3 preflight.py <path-to-skill-dir>
       python3 preflight.py ~/.claude/skills/my-skill

Output: markdown report to stdout. Exit 0 if no hard fails, 1 otherwise, 2 on bad arguments.

This is adapted from skill-engineer-master's preflight (Antony Evans, edge-brain-lite,
https://github.com/antonyevans/edge-brain-lite, CC BY 4.0) and deliberately differs from it:
the four checks that HARD-fail on a missing ## Gotchas section, references/learnings.md,
references/edge-cases.md, and evals/evals.json are removed, because a working skill needs none
of them and the source script would reject most real skills. In their place, the invariants a
skill needs to load and be read are HARD, and house-style conventions are surfaced as warnings.

Checks (HARD = must fix before shipping; warn = review, not a blocker):
  HARD:
  - SKILL.md exists and is <= 500 lines
  - Frontmatter present with `name` and `description`
  - `name` matches the directory name and is lowercase/numbers/hyphens, <= 64 chars
  - `description` is a single flat line (not YAML folded `>`), <= 1536 chars
    (warns over 500; the design target is about 400)
  - No nested reference chains (references/X/Y.md)
  - No CHANGELOG.md in the skill root
  warn:
  - description is third person and contains a negative trigger
  - `when_to_use` present
  - a `triggers:` or `category:` key, which Claude Code does not read
  - SKILL.md body <= 150 lines
  - `## Gotchas` section present (recommended, not required)
  - README.md in the skill root (fine in a published copy; Claude Code does not read it)
  - name prefix, only when REQUIRED_NAME_PREFIX is set (off by default)
  info:
  - `## Session Log` section present
"""

import re
import sys
from pathlib import Path

HARD_LINE_LIMIT = 500   # SKILL.md: over this, fail (every line costs tokens on every invocation)
WARN_LINE_LIMIT = 150   # SKILL.md: over this, warn (design intent is a routing layer)
DESCRIPTION_TARGET_CHARS = 400   # design target: enough for artifact, triggers, and negatives
DESCRIPTION_WARN_CHARS = 500     # over this, the description is buying reach with length
# 1536 is Claude Code's default skill-listing description limit (skillListingMaxDescChars): past
# it the skill listing truncates the description silently, with no error. It is the point where
# text stops being read, not an allowance to write toward.
DESCRIPTION_MAX_CHARS = 1536

# Optional house convention: a prefix every skill name in your suite carries (for example "acme-").
# Empty string turns the check off, which is the default because Claude Code requires no prefix.
# When set, a name without it produces a warning, never a hard fail.
REQUIRED_NAME_PREFIX = ""

# Frontmatter keys that some suites carry but Claude Code never reads. A routing phrase kept only
# in one of these does nothing at fire time; the warning says so. Keep a key if your own tooling
# (a skill index generator, for example) reads it.
UNREAD_KEYS = ("triggers", "category")


class Report:
    def __init__(self):
        self.hard_fails = []
        self.warnings = []
        self.passes = []

    def hard(self, msg):
        self.hard_fails.append(msg)

    def warn(self, msg):
        self.warnings.append(msg)

    def ok(self, msg):
        self.passes.append(msg)

    def render(self, skill_dir):
        out = [f"# Preflight report: {skill_dir.name}", ""]
        if self.hard_fails:
            out.append("## HARD FAILS (fix before proceeding)")
            out.extend(f"- {m}" for m in self.hard_fails)
            out.append("")
        if self.warnings:
            out.append("## Warnings (review, not blocking)")
            out.extend(f"- {m}" for m in self.warnings)
            out.append("")
        if self.passes:
            out.append("## Passes")
            out.extend(f"- {m}" for m in self.passes)
            out.append("")
        status = "FAIL" if self.hard_fails else ("WARN" if self.warnings else "PASS")
        out.append(
            f"**Status:** {status}: {len(self.hard_fails)} hard fail(s), "
            f"{len(self.warnings)} warning(s), {len(self.passes)} pass(es)"
        )
        return "\n".join(out)


def read_text(p: Path) -> str:
    return p.read_text(encoding="utf-8")


def parse_frontmatter(skill_md_text: str):
    """Return (frontmatter_dict, body_text). Minimal YAML: flat key: value plus folded `>`."""
    if not skill_md_text.startswith("---"):
        return None, skill_md_text
    parts = skill_md_text.split("---", 2)
    if len(parts) < 3:
        return None, skill_md_text
    raw = parts[1]
    body = parts[2].lstrip("\n")
    fm = {}
    raw_lines = raw.splitlines()
    i = 0
    while i < len(raw_lines):
        line = raw_lines[i]
        if not line.strip() or line.strip().startswith("#"):
            i += 1
            continue
        m = re.match(r"^([a-zA-Z_][\w-]*)\s*:\s*(.*)$", line)
        if not m:
            i += 1
            continue
        key, rest = m.group(1), m.group(2).strip()
        if rest in (">", "|", ">-", "|-"):
            folded = []
            i += 1
            while i < len(raw_lines) and (raw_lines[i].startswith((" ", "\t")) or not raw_lines[i].strip()):
                folded.append(raw_lines[i].strip())
                i += 1
            fm[key] = {"value": " ".join(x for x in folded if x), "folded": True, "quote": None}
            continue
        quote = None
        if rest.startswith('"') and rest.endswith('"') and len(rest) >= 2:
            quote = '"'
            rest = rest[1:-1]
        elif rest.startswith("'") and rest.endswith("'") and len(rest) >= 2:
            # YAML escapes a literal apostrophe inside a single-quoted scalar by doubling it, so
            # un-double it here; otherwise the measured length over-counts by one per apostrophe.
            quote = "'"
            rest = rest[1:-1].replace("''", "'")
        fm[key] = {"value": rest, "folded": False, "quote": quote}
        i += 1
    return fm, body


# Negative-trigger detection, in two passes because case matters for one half and not the other.
#
# Lowercase forms are matched case-insensitively: they are unambiguous wherever they appear.
_NEGATIVE_LOWER_RE = re.compile(r"(do not|don't|never|not for|not activate)", re.IGNORECASE)
# Capitalised `Not` forms are matched case-SENSITIVELY, at a sentence start only. This catches the
# common short form ("Not editing an existing skill", "Not skill-audit"). Case-sensitivity and the
# sentence anchor are what keep an ordinary mid-sentence "not" (as in "features not in the web UI")
# from reading as a negative trigger; a plain \bnot\b passes such descriptions falsely.
_NEGATIVE_ANCHORED_RE = re.compile(r"(^Not\b|[.;]\s+Not\b|Does NOT\b)", re.MULTILINE)


def has_negative_trigger(description: str) -> bool:
    """True if the description states at least one case where the skill should not fire."""
    return bool(_NEGATIVE_LOWER_RE.search(description)
                or _NEGATIVE_ANCHORED_RE.search(description))


def check_skill_md(skill_dir: Path, r: Report):
    skill_md = skill_dir / "SKILL.md"
    if not skill_md.exists():
        r.hard(f"SKILL.md missing at {skill_md}")
        return
    text = read_text(skill_md)
    line_count = text.count("\n") + (0 if text.endswith("\n") else 1)

    if line_count > HARD_LINE_LIMIT:
        r.hard(f"SKILL.md is {line_count} lines; hard limit is {HARD_LINE_LIMIT}. Move material into references/.")
    elif line_count > WARN_LINE_LIMIT:
        r.warn(f"SKILL.md is {line_count} lines; aim for under {WARN_LINE_LIMIT} and keep it a routing layer.")
    else:
        r.ok(f"SKILL.md length {line_count} lines")

    # No em/en dash check. A dash in a skill file does not change how the skill loads or runs;
    # apply your own punctuation rules when you publish a skill outward, not here.

    fm, body = parse_frontmatter(text)
    if fm is None:
        r.hard("SKILL.md has no YAML frontmatter")
        return

    if "name" not in fm:
        r.hard("Frontmatter missing `name` field")
    else:
        name = fm["name"]["value"]
        if name != skill_dir.name:
            r.hard(f"Frontmatter `name` ({name}) does not match directory name ({skill_dir.name})")
        elif not re.match(r"^[a-z0-9-]{1,64}$", name):
            r.hard(f"Frontmatter `name` ({name}) must be lowercase letters, numbers, and hyphens, <= 64 chars")
        else:
            r.ok(f"name `{name}` valid")
        if REQUIRED_NAME_PREFIX and not name.startswith(REQUIRED_NAME_PREFIX):
            r.warn(f"`name` ({name}) has no `{REQUIRED_NAME_PREFIX}` prefix; confirm this is intentional (REQUIRED_NAME_PREFIX is set in preflight.py)")

    if "description" not in fm:
        r.hard("Frontmatter missing `description` field")
    else:
        desc = fm["description"]
        if desc["folded"]:
            r.hard("Description uses YAML folded scalar (`description: >`); use a flat single-line `description:` form so Claude reads the whole thing.")
        val = desc["value"]
        if len(val) > DESCRIPTION_MAX_CHARS:
            r.hard(
                f"Description is {len(val)} chars, over {DESCRIPTION_MAX_CHARS}, where the "
                f"skill listing truncates it silently. Everything past that point is never read. "
                f"Cut it toward {DESCRIPTION_TARGET_CHARS}."
            )
        elif len(val) > DESCRIPTION_WARN_CHARS:
            r.warn(
                f"Description is {len(val)} chars, over the {DESCRIPTION_WARN_CHARS}-char "
                f"ceiling (target about {DESCRIPTION_TARGET_CHARS}). Buy discrimination with "
                f"negative triggers, not length. Cut it, or record the reason for the length in "
                f"the Phase 2 design summary."
            )
        else:
            r.ok(f"description length {len(val)} chars")

        # No quoting check, and that is a deliberate decision rather than an omission. The hazard
        # a quoting rule would guard against is a colon-space inside an unquoted description making
        # the frontmatter unparseable. In testing, descriptions with an unquoted colon-space loaded
        # and reached the model with the full text intact. An always-quote rule would add the
        # doubled-apostrophe trap to every description containing an apostrophe in exchange for
        # preventing nothing. Do not add one without re-testing first.
        low = val.lower()
        if low.startswith("i ") or low.startswith("you "):
            r.warn("Description may not be third-person (starts with 'I' or 'You')")
        if not has_negative_trigger(val):
            r.warn("Description has no negative trigger (no 'Does NOT', 'Not for', 'Not <skill>', or similar); a description with no negative fires on its neighbors' requests")

    if "when_to_use" in fm:
        r.ok("when_to_use present")
    else:
        r.warn("No `when_to_use` field. Add one to three sentences of prose on when to pick this skill and how it differs from its nearest sibling.")

    for key in UNREAD_KEYS:
        if key in fm:
            r.warn(f"`{key}:` key present. Claude Code does not read it, so nothing routes from it; move any phrase that must route into `description`. Keep the key only if your own tooling reads it.")

    if re.search(r"^##\s+Gotchas\s*$", body, re.MULTILINE | re.IGNORECASE):
        r.ok("## Gotchas section present")
    else:
        r.warn("No `## Gotchas` section (recommended, not required)")

    if re.search(r"^##\s+Session Log\s*$", body, re.MULTILINE | re.IGNORECASE):
        r.ok("## Session Log section present")


def check_root_files(skill_dir: Path, r: Report):
    if (skill_dir / "CHANGELOG.md").exists():
        r.hard("Forbidden file CHANGELOG.md in skill root; remove it. It is not a skill component, and change history belongs outside the skill folder.")
    if (skill_dir / "README.md").exists():
        r.warn("README.md in skill root. Claude Code does not read it; that is fine for a published copy that documents the skill for people, but keep instructions the skill needs in SKILL.md or references/.")


def check_reference_nesting(skill_dir: Path, r: Report):
    refs_dir = skill_dir / "references"
    if not refs_dir.exists():
        return
    for p in refs_dir.rglob("*.md"):
        rel = p.relative_to(refs_dir)
        if len(rel.parts) > 1:
            r.hard(f"Nested reference file {rel}; references must be one level deep")


def main():
    if len(sys.argv) < 2:
        print("Error: missing skill directory argument.", file=sys.stderr)
        print("Usage: python3 preflight.py <path-to-skill-dir>", file=sys.stderr)
        sys.exit(2)

    skill_dir = Path(sys.argv[1]).expanduser().resolve()
    if not skill_dir.is_dir():
        print(f"Error: {skill_dir} is not a directory. Check the path and try again.", file=sys.stderr)
        sys.exit(2)

    r = Report()
    check_skill_md(skill_dir, r)
    check_root_files(skill_dir, r)
    check_reference_nesting(skill_dir, r)

    print(r.render(skill_dir))
    sys.exit(1 if r.hard_fails else 0)


if __name__ == "__main__":
    main()

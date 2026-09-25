#!/usr/bin/env python3
"""
search_and_rank.py: Query a search source, normalize results, rank with documented weights.

Derived from the script archetypes in skill-engineer-master by Antony Evans (edge-brain-lite,
https://github.com/antonyevans/edge-brain-lite), CC BY 4.0.

Archetype. Copy into [skill]/scripts/ and rename (e.g., search_catalog_products.py).
The skill author replaces the `SKILL_SPECIFIC:` blocks with real fetching + parsing.

Usage:
  python search_and_rank.py "query terms" [--limit 10] [--source web]

Output: a JSON array of ranked results to stdout. Each result:
  {"rank": int, "score": float, "title": str, "url": str, "meta": {...}}

Error taxonomy:
  exit 0: results returned (may be empty; that's a valid signal, not an error)
  exit 1: source fetch failed
  exit 2: bad arguments
"""

import argparse
import json
import sys

# --- Ranking weights (document the rationale; do not hardcode without comment) -----
# Each signal is normalized to [0, 1] then multiplied by its weight.
# Weights should sum to 1.0 to keep the composite score in [0, 1].
WEIGHT_RELEVANCE = 0.5   # Match strength between query and result title/snippet; highest weight because relevance is the primary reason to rank.
WEIGHT_RECENCY = 0.2     # Newer results preferred when dates are available; flat zero when not applicable.
WEIGHT_AUTHORITY = 0.2   # Source credibility (star count, install count, domain trust); domain-specific.
WEIGHT_FIT = 0.1         # Skill-specific fit signals (e.g., margin, compliance flag); small tiebreaker, not decisive.


def fetch_source(query: str, source: str, limit: int) -> list[dict]:
    """SKILL_SPECIFIC: replace this stub with a real source call.
    Must return a list of dicts, each with keys: title, url, snippet, published_at (optional), meta (dict)."""
    # Stub results so the archetype runs end-to-end without external dependencies.
    return [
        {
            "title": f"Example result {i} for '{query}'",
            "url": f"https://example.com/{i}",
            "snippet": f"Snippet about {query}; placeholder #{i}",
            "published_at": None,
            "meta": {"authority": 0.5, "fit": 0.5},
        }
        for i in range(min(limit, 5))
    ]


def score(query: str, result: dict) -> float:
    """Composite score in [0, 1]. Each signal must be normalized before weighting."""
    q_tokens = set(query.lower().split())
    title_tokens = set(result["title"].lower().split())
    snippet_tokens = set(result.get("snippet", "").lower().split())
    overlap = len(q_tokens & (title_tokens | snippet_tokens)) / max(1, len(q_tokens))
    relevance = min(1.0, overlap)

    recency = 0.0  # SKILL_SPECIFIC: parse published_at into a 0..1 recency signal if dates are available.

    authority = float(result.get("meta", {}).get("authority", 0.0))
    fit = float(result.get("meta", {}).get("fit", 0.0))

    return (
        WEIGHT_RELEVANCE * relevance
        + WEIGHT_RECENCY * recency
        + WEIGHT_AUTHORITY * authority
        + WEIGHT_FIT * fit
    )


def main():
    parser = argparse.ArgumentParser(description="Search and rank results from a source")
    parser.add_argument("query", help="Search query")
    parser.add_argument("--source", default="web", help="Source name (SKILL_SPECIFIC: wire real backends)")
    parser.add_argument("--limit", type=int, default=10, help="Max results to return")
    ns = parser.parse_args()

    try:
        raw = fetch_source(ns.query, ns.source, ns.limit)
    except Exception as e:
        # Specific exceptions should be caught by the SKILL_SPECIFIC fetch_source implementation
        # with self-correcting error messages. Fall through only for unexpected failures.
        print(
            f"Error: fetch from source '{ns.source}' failed: {type(e).__name__}: {e}. "
            f"Check credentials, network, and the source-specific adapter in fetch_source().",
            file=sys.stderr,
        )
        sys.exit(1)

    scored = [(score(ns.query, r), r) for r in raw]
    scored.sort(key=lambda x: x[0], reverse=True)

    ranked = [
        {
            "rank": i + 1,
            "score": round(s, 4),
            "title": r["title"],
            "url": r["url"],
            "meta": r.get("meta", {}),
        }
        for i, (s, r) in enumerate(scored[: ns.limit])
    ]

    print(json.dumps(ranked, indent=2))


if __name__ == "__main__":
    main()

#!/usr/bin/env python3
"""
fetch_and_cache.py: HTTP fetch with ETag/If-Modified-Since caching + retries.

Derived from the script archetypes in skill-engineer-master by Antony Evans (edge-brain-lite,
https://github.com/antonyevans/edge-brain-lite), CC BY 4.0.

Archetype. Copy into [skill]/scripts/ and rename to fetch_<domain>.py before editing.

Usage: python fetch_and_cache.py <url> [--cache-dir .cache] [--force]
Output: file contents to stdout (or from cache). Stderr: status/log.
Cache location: <cache-dir>/<sha1-of-url>.{body,meta}

Error taxonomy:
  exit 0: fetched (fresh or 304 not-modified from cache)
  exit 1: all retries exhausted (network error, DNS, timeout)
  exit 2: HTTP 4xx (client error; will not retry, user must fix URL or auth)
  exit 3: HTTP 5xx after retries (server error; try again later)
  exit 4: bad arguments or cache corruption

Required packages: requests (pip install requests, in whichever Python environment runs the skill)
"""

import argparse
import hashlib
import json
import sys
import time
from pathlib import Path

try:
    import requests
except ImportError:
    print(
        "Error: 'requests' package not installed. "
        "Install it with `python3 -m pip install requests` in the Python environment "
        "that runs this skill, then retry.",
        file=sys.stderr,
    )
    sys.exit(4)

# --- Configuration (document rationale for every value) -----------------------
MAX_RETRIES = 3          # Three attempts covers transient network blips without tying up the caller.
BACKOFF_BASE = 1.5       # Exponential backoff factor; 1s -> 1.5s -> 2.25s between retries.
REQUEST_TIMEOUT = 30     # Thirty seconds; tight enough to fail fast, generous enough for slow APIs.
USER_AGENT = "skill-fetcher/1.0 (+https://example.com)"  # Identify ourselves; some APIs block blank UAs.


def cache_paths(cache_dir: Path, url: str) -> tuple[Path, Path]:
    key = hashlib.sha1(url.encode("utf-8")).hexdigest()
    return cache_dir / f"{key}.body", cache_dir / f"{key}.meta"


def load_cache(body_path: Path, meta_path: Path) -> tuple[str | None, dict]:
    if not body_path.exists() or not meta_path.exists():
        return None, {}
    try:
        body = body_path.read_text(encoding="utf-8")
        meta = json.loads(meta_path.read_text(encoding="utf-8"))
        return body, meta
    except (OSError, json.JSONDecodeError) as e:
        # Corrupt cache; delete and start fresh rather than propagating a confusing error.
        print(f"Warning: cache corrupt ({e}); discarding.", file=sys.stderr)
        body_path.unlink(missing_ok=True)
        meta_path.unlink(missing_ok=True)
        return None, {}


def save_cache(body_path: Path, meta_path: Path, body: str, response: requests.Response) -> None:
    body_path.parent.mkdir(parents=True, exist_ok=True)
    body_path.write_text(body, encoding="utf-8")
    meta = {
        "etag": response.headers.get("ETag"),
        "last_modified": response.headers.get("Last-Modified"),
        "fetched_at": time.time(),
        "status": response.status_code,
    }
    meta_path.write_text(json.dumps(meta), encoding="utf-8")


def fetch(url: str, cache_dir: Path, force: bool) -> str:
    body_path, meta_path = cache_paths(cache_dir, url)
    cached_body, meta = (None, {}) if force else load_cache(body_path, meta_path)

    headers = {"User-Agent": USER_AGENT}
    if cached_body is not None:
        if meta.get("etag"):
            headers["If-None-Match"] = meta["etag"]
        if meta.get("last_modified"):
            headers["If-Modified-Since"] = meta["last_modified"]

    last_exc = None
    for attempt in range(1, MAX_RETRIES + 1):
        try:
            resp = requests.get(url, headers=headers, timeout=REQUEST_TIMEOUT)
        except requests.RequestException as e:
            last_exc = e
            if attempt < MAX_RETRIES:
                wait = BACKOFF_BASE ** attempt
                print(f"Attempt {attempt} failed ({e}); retrying in {wait:.1f}s", file=sys.stderr)
                time.sleep(wait)
                continue
            print(
                f"Error: network failure after {MAX_RETRIES} attempts: {e}. "
                f"Check connectivity, DNS, and whether the host is reachable.",
                file=sys.stderr,
            )
            sys.exit(1)

        if resp.status_code == 304 and cached_body is not None:
            print(f"Cache hit (304 Not Modified): {url}", file=sys.stderr)
            return cached_body

        if 400 <= resp.status_code < 500:
            print(
                f"Error: HTTP {resp.status_code} for {url}. "
                f"This is a client error; verify the URL, authentication, and request format. Will not retry.",
                file=sys.stderr,
            )
            sys.exit(2)

        if 500 <= resp.status_code < 600:
            if attempt < MAX_RETRIES:
                wait = BACKOFF_BASE ** attempt
                print(f"HTTP {resp.status_code} on attempt {attempt}; retrying in {wait:.1f}s", file=sys.stderr)
                time.sleep(wait)
                continue
            print(
                f"Error: HTTP {resp.status_code} after {MAX_RETRIES} attempts. "
                f"Server-side issue; try again later or use the cached copy at {body_path} if present.",
                file=sys.stderr,
            )
            sys.exit(3)

        save_cache(body_path, meta_path, resp.text, resp)
        print(f"Fetched fresh ({resp.status_code}): {url}", file=sys.stderr)
        return resp.text

    raise RuntimeError(f"Unreachable: exhausted retries without deciding. Last error: {last_exc}")


def main():
    parser = argparse.ArgumentParser(description="Fetch a URL with ETag caching")
    parser.add_argument("url", help="URL to fetch")
    parser.add_argument("--cache-dir", default=".cache", help="Cache directory (default: .cache)")
    parser.add_argument("--force", action="store_true", help="Ignore cache and re-fetch")
    ns = parser.parse_args()

    body = fetch(ns.url, Path(ns.cache_dir), ns.force)
    # SKILL_SPECIFIC: replace this line with whatever parsing/transformation the skill needs.
    sys.stdout.write(body)


if __name__ == "__main__":
    main()

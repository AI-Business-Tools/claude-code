# Script Archetypes

Derived from the script archetypes in `skill-engineer-master` by Antony Evans (edge-brain-lite, https://github.com/antonyevans/edge-brain-lite), CC BY 4.0.

Copy-and-adapt starting points for skill scripts. **Never design a script from a blank file**; pick the archetype closest to your use case, copy it into the target skill's `scripts/` folder, rename, and adapt.

| Archetype | Use when | Key patterns covered |
|-----------|----------|----------------------|
| `fetch_and_cache.py` | The step makes an HTTP call | ETag/If-Modified-Since caching, retries with backoff, descriptive error taxonomy |
| `validate_output.py` | Output must conform to a schema or template | JSON schema load + validate, self-correction messages |
| `log_run.py` | The step appends to a state file or run log | Append-only JSONL with O_APPEND (crash-safe), timestamped |
| `pick_from_options.py` | The step presents N options and captures a human choice | AskUserQuestion-compatible structured output |
| `search_and_rank.py` | The step searches + ranks results from an API | Query construction, result normalization, ranking with documented weights |

## Adapting an archetype

1. Copy the file into `[skill-name]/scripts/` with a descriptive verb-prefixed name (`fetch_catalog_product.py`, not `fetch.py`).
2. Update the module docstring: purpose, usage, stdout format, error taxonomy.
3. Replace placeholder logic with skill-specific operation.
4. Keep error messages self-correcting; tell the agent *what to try next*.
5. Keep magic constants out; every config value gets an inline comment explaining the rationale.
6. Test the happy path and at least one error path before declaring done.

## What archetypes are NOT

- Not libraries. Do not import from them; copy.
- Not runnable as-is. They have placeholders (`# SKILL_SPECIFIC: ...`) marking where you must edit.
- Not complete. They cover the hard parts (IO, retries, errors, concurrency) and leave the domain logic to you.

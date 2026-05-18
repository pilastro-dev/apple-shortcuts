---
name: refresh-cherri-docs
description: Refresh, partially refresh, or diagnose the local cherri-docs/ markdown mirror of cherrilang.org/language/. Use this skill whenever the user mentions refreshing, re-scraping, regenerating, or updating the cherri docs; regenerating the anchor index; normalizing internal links; pulling cherri-lang upstream changes; or troubleshooting a refresh that produced unexpected diffs. Also use it for partial-refresh tasks like rebuilding anchors.json or re-running link normalization without a full re-scrape.
---

# Refresh cherri-docs

This repo maintains a local markdown mirror of `https://cherrilang.org/language/` in `cherri-docs/`. The mirror has three moving parts kept consistent by three scripts that live in this skill's `scripts/` directory. This skill explains when to use each, what to expect, and how to diagnose problems.

All scripts are cwd-independent: they compute their own paths from script location, so the commands below work from any working directory.

## Pipeline

```
scrape (defuddle)  →  normalize internal links (convert_links.py)  →  build anchor index (gen_anchors.py)
```

End-to-end: `bash .claude/skills/refresh-cherri-docs/scripts/refresh.sh`. Idempotent. ~2-3 minutes for all 45 pages.

## When to run what

The right invocation depends on what just changed:

- **Upstream changed or periodic resync** → full pipeline:
  ```
  bash .claude/skills/refresh-cherri-docs/scripts/refresh.sh
  ```
- **You edited a doc file locally and want anchors current** → pure regeneration, no scrape, ~1 second:
  ```
  python3 .claude/skills/refresh-cherri-docs/scripts/gen_anchors.py
  ```
- **Suspect a URL slipped through, or you just modified convert_links.py** → re-run link normalization across the corpus, no scrape:
  ```
  python3 .claude/skills/refresh-cherri-docs/scripts/convert_links.py
  ```

Don't run `convert_links.py` after a fresh scrape and skip `gen_anchors.py` — they're paired. A scrape reintroduces absolute URLs *and* may change heading text, so both downstream stages need to run to keep the mirror coherent. `refresh.sh` enforces this.

## Known issues (defuddle scrape stage)

These failure modes have actually shown up. Surface them when a refresh produces unexpected output or when the user is asking why something doesn't work.

**Subcommand required.** `npx defuddle --markdown <url>` does not work. The `parse` subcommand is required: `npx defuddle parse --markdown <url>`. `refresh.sh` already uses the correct form.

**Stdin unsupported.** Piping HTML via `curl | npx defuddle -` fails with `error: unknown command '-'`. Pass the URL directly; defuddle fetches it internally.

**Non-fatal stderr noise.** On pages with relative internal links in `<head>` metadata, defuddle prints `Failed to parse URL: TypeError: Invalid URL ...` to stderr. The markdown body still writes correctly to stdout. `refresh.sh` suppresses this with `2>/dev/null`. If you're debugging and need to see the real errors, drop the redirect temporarily.

## Verifying a refresh ran cleanly

Each stage reports its own signal — read them in order:

- **Scrape**: one `fetched: <path>` line per page. Should be 45 total (19 top-level + 26 standard) unless the page list has been changed.
- **convert_links.py**: ends with `verification: no residual internal URLs outside code blocks`. If this line is missing or replaced by `FAIL:` output, the pipeline halted before anchor regeneration.
- **gen_anchors.py**: `wrote ...: N unique slugs, M headings, K slugs collide across files`. A sharp drop in N or M versus the last run is a flag — upstream may have restructured.

If anything looks off, `git diff cherri-docs/` is the fastest diagnostic — the corpus is small enough that a real-looking diff is fast to eyeball.

## Diagnostic checks

- `git diff cherri-docs/` — which markdown files and headings changed (anchors.json lives inside cherri-docs/, so this surfaces section drift too)
- `git diff cherri-docs/anchors.json` — isolated view of which headings appeared, disappeared, or moved
- `grep -rn 'cherrilang.org/language' cherri-docs/` — should return zero outside fenced code blocks; non-zero means convert_links.py didn't run or failed mid-corpus
- Re-run `python3 .claude/skills/refresh-cherri-docs/scripts/convert_links.py` — confirms link normalization is current; safe to invoke standalone, won't touch already-converted content

## What lives where

Inside this skill (`.claude/skills/refresh-cherri-docs/scripts/`):
- `refresh.sh` — orchestrator (scrape → convert → index)
- `convert_links.py` — URL → relative-path conversion + anchor validation (warns on missing anchors, drops them rather than shipping broken links)
- `gen_anchors.py` — heading index generator; reuses `convert_links.slugify_heading` so the validator and the index produce identical slugs

In the repo:
- `cherri-docs/` — the mirror (45 markdown files: 19 top-level + 26 in `standard/`)
- `cherri-docs/anchors.json` — generated index, `slug → [{file, line, heading}]`. Co-located with the corpus it describes. Slugs may have multiple entries when a heading name repeats across files (e.g., `list` appears in both `menus.md` and `standard/scripting.md`).

## Architectural notes worth knowing

**Scripts are cwd-independent.** Each script derives its working paths from its own file location, not from the cwd. So they run correctly whether invoked from the repo root, the skill directory, or anywhere else.

**Slug discovery is filesystem-derived.** `convert_links.py` does not maintain a hardcoded slug list. It walks `cherri-docs/` at startup and learns what pages exist. Newly scraped pages are automatically recognized as valid link targets on the next run.

**Dead-link policy: strip rather than ship broken affordances.** This corpus is for agentic consumption; misleading `[label](url)` constructs cost more than they save. If a URL points to a file that isn't in the mirror, the link becomes plain text (`label` only). If a URL points to a real file but a non-existent anchor, the anchor is dropped (file link preserved).

## Open improvements

GitHub issue #1 (`Proposed Improvements: Document processing pipeline`) tracks deferred gaps: dynamic page discovery (currently hardcoded in `refresh.sh`), end-to-end smoke test, and data-driven page list. If any land, they'll modify `refresh.sh`; this skill stays as an orchestration/knowledge layer.

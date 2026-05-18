# Link Conversion: Internal Cross-References to LLM-Native Format

## Problem

The scraped markdown files contain internal cross-references as full `https://cherrilang.org/language/` URLs. These are useless to an LLM reading local files — they point at a remote site the LLM won't fetch, and they carry no signal about where the information lives locally. The goal is to convert them into relative filesystem paths so a tool-using LLM can read the referenced file directly.

External links (GitHub, glyphs subdomain, the FAQ, the compiler docs) should be left as-is — they aren't mirrored locally and the URL is the only available reference.

---

## URL Taxonomy

Four internal URL patterns appear across the 45 files:

| Pattern | Example |
|---------|---------|
| Top-level with `.html` | `https://cherrilang.org/language/types.html` |
| Top-level without extension | `https://cherrilang.org/language/types` |
| Top-level with anchor (no `.html`) | `https://cherrilang.org/language/types#value-types` |
| Top-level with `.html` and anchor | `https://cherrilang.org/language/types.html#content-item-types` |
| Standard subpage with `.html` | `https://cherrilang.org/language/standard/documents.html` |
| Standard subpage with anchor | `https://cherrilang.org/language/standard/documents#match-text` |
| Dead link (page not in mirror) | `https://cherrilang.org/language/custom-actions#output-type` |

All variants reduce to the same three-field extraction: `standard/` prefix (bool), slug, optional anchor.

---

## Target Format

Convert internal links to relative markdown paths. Relative depth depends on the location of the file being processed:

| Source file location | Target URL resolves to | Converted form |
|----------------------|------------------------|----------------|
| `cherri-docs/*.md` | `/language/types.html` | `./types.md` |
| `cherri-docs/*.md` | `/language/standard/documents.html` | `./standard/documents.md` |
| `cherri-docs/standard/*.md` | `/language/types.html` | `../types.md` |
| `cherri-docs/standard/*.md` | `/language/standard/documents.html` | `./documents.md` |

Anchors are preserved verbatim:

```
# Before
[value types](https://cherrilang.org/language/types#value-types)

# After (from a top-level file)
[value types](./types.md#value-types)
```

---

## Edge Cases

**URLs inside code blocks must not be transformed.** The files contain template literals like `` `https://{host}/...` `` and package manager examples with real URLs as instructional content. A line-aware parser must skip fenced (` ``` `) and inline (`` ` ``) code spans.

**Dead link:** `https://cherrilang.org/language/custom-actions#output-type` appears once (in `action-definitions.md`) but `custom-actions.html` was never scraped — it doesn't exist on the site. Convert to `./custom-actions.md#output-type` with a comment noting the file is absent, or strip the link text to plain text. Plain text is safer: `output type` with no link.

**No-extension links resolve the same as `.html` links.** `https://cherrilang.org/language/types` and `https://cherrilang.org/language/types.html` both map to `./types.md`. Treat them identically.

**External cherrilang.org URLs are not internal links.** These are outside `/language/` and have no local mirror:
- `https://cherrilang.org/compiler/actions`
- `https://cherrilang.org/faq#how-do-i-use-non-standard-actions`
- `https://glyphs.cherrilang.org/`

Leave these unchanged.

---

## Implementation

A single Python script. No dependencies beyond the standard library.

```python
#!/usr/bin/env python3
"""
Convert cherrilang.org/language/ cross-reference URLs to relative markdown paths.
Run from the apple-shortcuts/ directory:

    python3 convert-links.py
"""

import re
import os
from pathlib import Path

DOCS_ROOT = Path("cherri-docs")
INTERNAL_BASE = "https://cherrilang.org/language/"

# Known pages in the local mirror (slugs only, no extension)
KNOWN_SLUGS = {
    "actions", "comments", "definitions", "variables-constants-globals",
    "references", "types", "control-flow", "menus", "vcards", "copy-paste",
    "import-questions", "import-actions", "includes", "functions",
    "action-definitions", "package-manager", "raw-actions", "best-practices",
}
KNOWN_STANDARD_SLUGS = {
    "a11y", "intelligence", "basic", "calendar", "contacts", "crypto",
    "device", "documents", "images", "location", "macos-only", "math",
    "media", "music", "network", "pdf", "photos", "scripting", "settings",
    "sharing", "shortcuts", "text", "translation", "web", "builtin", "stdlib",
}

# Match markdown links: [label](url) — only full URLs, not relative paths
LINK_RE = re.compile(r'\[([^\]]*)\]\((https://cherrilang\.org/language/[^)]*)\)')

# Match fenced code blocks to skip
FENCE_RE = re.compile(r'^```', re.MULTILINE)

def url_to_rel_path(url: str, in_standard: bool) -> str | None:
    """
    Convert an internal cherrilang.org/language/ URL to a relative path.
    Returns None if the URL is not an internal language link.
    """
    if not url.startswith(INTERNAL_BASE):
        return None

    path = url[len(INTERNAL_BASE):]          # e.g. "types.html#value-types"
    anchor = ""
    if "#" in path:
        path, anchor = path.split("#", 1)
        anchor = "#" + anchor

    path = path.rstrip("/").removesuffix(".html")   # e.g. "types" or "standard/documents"

    if path.startswith("standard/"):
        slug = path[len("standard/"):]
        known = slug in KNOWN_STANDARD_SLUGS
        rel = f"./standard/{slug}.md{anchor}" if not in_standard else f"./{slug}.md{anchor}"
    elif "/" not in path:
        slug = path or "index"
        known = slug in KNOWN_SLUGS
        rel = f"./{slug}.md{anchor}" if not in_standard else f"../{slug}.md{anchor}"
    else:
        return None  # unexpected sub-path — leave unchanged

    if not known and slug != "index":
        # Dead link: return plain slug text signal for the caller to handle
        return f"DEAD:{slug}{anchor}"

    return rel


def convert_file(md_path: Path) -> None:
    in_standard = md_path.parent.name == "standard"
    original = md_path.read_text(encoding="utf-8")

    # Split on fenced code blocks; process only even-indexed segments (outside fences)
    segments = FENCE_RE.split(original)
    result_segments = []

    for i, segment in enumerate(segments):
        if i % 2 == 1:
            # Inside a fenced block — pass through unchanged
            result_segments.append(segment)
            continue

        def replace_link(m: re.Match) -> str:
            label, url = m.group(1), m.group(2)
            rel = url_to_rel_path(url, in_standard)
            if rel is None:
                return m.group(0)                       # external — leave unchanged
            if rel.startswith("DEAD:"):
                return label                            # dead link — plain text
            return f"[{label}]({rel})"

        result_segments.append(LINK_RE.sub(replace_link, segment))

    converted = "```".join(result_segments)

    if converted != original:
        md_path.write_text(converted, encoding="utf-8")
        print(f"updated: {md_path}")


def main():
    for md_path in sorted(DOCS_ROOT.rglob("*.md")):
        convert_file(md_path)


if __name__ == "__main__":
    main()
```

### What it does

1. Walks every `.md` file under `cherri-docs/`
2. Splits on fenced code block delimiters (` ``` `) so URLs inside code examples are never touched
3. For each `[label](url)` outside a code block, extracts the slug and optional anchor from the URL
4. Computes the correct relative path based on whether the source file is in `standard/` or the top level
5. Degrades gracefully: external URLs are left as-is, dead links become plain text (label only)
6. Writes back only if the content changed

### Running it

```bash
cd /path/to/apple-shortcuts
python3 convert-links.py
```

No packages required. Python 3.9+ for `str.removesuffix`.

### Inline code spans

The regex matches `[label](url)` in markdown link syntax only. Bare URLs inside backtick inline code (`` `https://...` ``) won't match the `[label](url)` pattern and are safe. If bare URLs outside of code spans or links become an issue, add a second pass with a plain URL regex that checks for surrounding backticks before replacing.

---

## Before / After Examples

```markdown
# Before (in cherri-docs/action-definitions.md)
[standard Shortcut actions](https://cherrilang.org/language/actions)
[types](https://cherrilang.org/language/types#value-types)
[output type](https://cherrilang.org/language/custom-actions#output-type)

# After
[standard Shortcut actions](./actions.md)
[types](./types.md#value-types)
output type
```

```markdown
# Before (in cherri-docs/standard/builtin.md)
[Match Text](https://cherrilang.org/language/standard/documents#match-text)
[makeVCard()](https://cherrilang.org/language/vcards)

# After
[Match Text](./documents.md#match-text)
[makeVCard()](../vcards.md)
```

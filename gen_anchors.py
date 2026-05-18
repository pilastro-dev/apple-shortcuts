#!/usr/bin/env python3
"""
Generate anchors.json: an index of H2/H3 headings across cherri-docs/.

Run from the apple-shortcuts/ directory:

    python3 gen_anchors.py

Output: anchors.json mapping slug -> [{file, line, heading}, ...]. Slugs can
collide across files (e.g. 'list' appears in multiple), hence the list.

Reuses convert_links.slugify_heading so this index and the validator in
convert_links.py stay in lockstep.
"""

import json
import re
import sys
from pathlib import Path

from convert_links import slugify_heading  # type: ignore[import-not-found]

DOCS_ROOT = Path("cherri-docs")
OUTPUT = Path("anchors.json")

HEADING_RE = re.compile(r'^(#{2,3})\s+(.+?)\s*$')
FENCE_RE = re.compile(r'^\s*```')


def collect_anchors(root: Path) -> dict[str, list[dict]]:
    by_slug: dict[str, list[dict]] = {}
    for md in sorted(root.rglob("*.md")):
        rel = str(md.relative_to(root))
        in_fence = False
        for line_no, line in enumerate(md.read_text(encoding="utf-8").split("\n"), start=1):
            if FENCE_RE.match(line):
                in_fence = not in_fence
                continue
            if in_fence:
                continue
            m = HEADING_RE.match(line)
            if not m:
                continue
            heading = m.group(2)
            slug = slugify_heading(heading)
            if not slug:
                continue
            by_slug.setdefault(slug, []).append({
                "file": rel,
                "line": line_no,
                "heading": heading,
            })
    return by_slug


def main() -> int:
    if not DOCS_ROOT.is_dir():
        print(f"error: {DOCS_ROOT} not found (run from apple-shortcuts/)", file=sys.stderr)
        return 1

    anchors = collect_anchors(DOCS_ROOT)
    for entries in anchors.values():
        entries.sort(key=lambda e: (e["file"], e["line"]))
    sorted_anchors = dict(sorted(anchors.items()))

    OUTPUT.write_text(json.dumps(sorted_anchors, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")

    total = sum(len(v) for v in sorted_anchors.values())
    collisions = sum(1 for v in sorted_anchors.values() if len(v) > 1)
    print(f"wrote {OUTPUT}: {len(sorted_anchors)} unique slugs, {total} headings, {collisions} slugs collide across files")
    return 0


if __name__ == "__main__":
    sys.exit(main())

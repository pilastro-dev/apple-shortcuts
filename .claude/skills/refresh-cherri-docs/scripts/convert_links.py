#!/usr/bin/env python3
"""
Convert cherrilang.org/language/ cross-reference URLs in cherri-docs/ to
relative markdown paths so a tool-using LLM can resolve references locally.

Invoke from anywhere; the script resolves paths from its own location:

    python3 .claude/skills/refresh-cherri-docs/scripts/convert_links.py

Requires Python 3.10+.
"""

import re
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[4]
DOCS_ROOT = REPO_ROOT / "cherri-docs"
INTERNAL_BASE = "https://cherrilang.org/language/"

LINK_RE = re.compile(r'\[([^\]]*)\]\((https://cherrilang\.org/language/[^)]*)\)')
FENCE_RE = re.compile(r'^```', re.MULTILINE)
HEADING_RE = re.compile(r'^#{1,6}\s+(.+?)\s*$', re.MULTILINE)
RESIDUAL_RE = re.compile(r'https://cherrilang\.org/language/')


def discover_slugs(root: Path) -> tuple[set[str], set[str]]:
    """Walk the mirror and return (top-level slugs, standard/ slugs)."""
    top: set[str] = set()
    standard: set[str] = set()
    for md in root.rglob("*.md"):
        slug = md.stem
        if md.parent.name == "standard":
            standard.add(slug)
        elif md.parent == root:
            top.add(slug)
    return top, standard


def slugify_heading(text: str) -> str:
    text = re.sub(r'`([^`]+)`', r'\1', text)
    text = re.sub(r'\[([^\]]+)\]\([^)]+\)', r'\1', text)
    text = re.sub(r'[*_]', '', text)
    text = text.lower().strip()
    text = re.sub(r'[^a-z0-9]+', '-', text)
    return text.strip('-')


def discover_anchors(root: Path) -> dict[str, set[str]]:
    """Map 'types.md' or 'standard/documents.md' to the set of heading slugs in that file."""
    out: dict[str, set[str]] = {}
    for md in root.rglob("*.md"):
        key = str(md.relative_to(root))
        text = md.read_text(encoding="utf-8")
        # Strip fenced blocks before scanning so '# comment' inside code isn't read as a heading.
        segments = FENCE_RE.split(text)
        outside = "\n".join(seg for i, seg in enumerate(segments) if i % 2 == 0)
        out[key] = {slugify_heading(m.group(1)) for m in HEADING_RE.finditer(outside)}
    return out


def url_to_target(url: str) -> tuple[str | None, str]:
    """Parse an internal URL into (slug-path-without-extension, anchor-with-hash-or-empty)."""
    if not url.startswith(INTERNAL_BASE):
        return None, ""
    path = url[len(INTERNAL_BASE):]
    anchor = ""
    if "#" in path:
        path, _, frag = path.partition("#")
        anchor = "#" + frag
    path = path.rstrip("/").removesuffix(".html")
    return path, anchor


def resolve_link(
    slug_path: str,
    anchor: str,
    source_in_standard: bool,
    top_slugs: set[str],
    standard_slugs: set[str],
    anchors_by_file: dict[str, set[str]],
    source_label: str,
) -> str | None:
    """Return the relative markdown path, or None if the slug isn't in the mirror."""
    if slug_path.startswith("standard/"):
        slug = slug_path[len("standard/"):]
        if slug not in standard_slugs:
            return None
        target_key = f"standard/{slug}.md"
        rel = f"./{slug}.md{anchor}" if source_in_standard else f"./standard/{slug}.md{anchor}"
    else:
        if "/" in slug_path:
            return None
        slug = slug_path or "index"
        if slug not in top_slugs:
            return None
        target_key = f"{slug}.md"
        rel = f"../{slug}.md{anchor}" if source_in_standard else f"./{slug}.md{anchor}"

    if anchor:
        frag = anchor[1:]
        if frag not in anchors_by_file.get(target_key, set()):
            print(
                f"  warn: anchor #{frag} not found in {target_key} (from {source_label}) — dropping anchor",
                file=sys.stderr,
            )
            rel = rel.removesuffix(anchor)

    return rel


def convert_file(
    md_path: Path,
    top_slugs: set[str],
    standard_slugs: set[str],
    anchors_by_file: dict[str, set[str]],
) -> bool:
    source_in_standard = md_path.parent.name == "standard"
    original = md_path.read_text(encoding="utf-8")
    segments = FENCE_RE.split(original)
    result_segments = []

    for i, segment in enumerate(segments):
        if i % 2 == 1:
            result_segments.append(segment)
            continue

        def replace_link(m: re.Match) -> str:
            label, url = m.group(1), m.group(2)
            slug_path, anchor = url_to_target(url)
            if slug_path is None:
                return m.group(0)
            rel = resolve_link(
                slug_path,
                anchor,
                source_in_standard,
                top_slugs,
                standard_slugs,
                anchors_by_file,
                source_label=str(md_path),
            )
            if rel is None:
                return label
            return f"[{label}]({rel})"

        result_segments.append(LINK_RE.sub(replace_link, segment))

    converted = "```".join(result_segments)
    if converted != original:
        md_path.write_text(converted, encoding="utf-8")
        return True
    return False


def verify_no_residual(root: Path) -> list[tuple[Path, int, str]]:
    """Return (file, line_no, line) for every internal URL surviving outside a fenced block."""
    hits: list[tuple[Path, int, str]] = []
    for md in sorted(root.rglob("*.md")):
        in_fence = False
        for line_no, line in enumerate(md.read_text(encoding="utf-8").split("\n"), start=1):
            if line.lstrip().startswith("```"):
                in_fence = not in_fence
                continue
            if not in_fence and RESIDUAL_RE.search(line):
                hits.append((md, line_no, line.strip()))
    return hits


def main() -> int:
    top_slugs, standard_slugs = discover_slugs(DOCS_ROOT)
    print(f"discovered {len(top_slugs)} top-level slugs, {len(standard_slugs)} standard slugs")
    anchors_by_file = discover_anchors(DOCS_ROOT)

    changed = 0
    for md in sorted(DOCS_ROOT.rglob("*.md")):
        if convert_file(md, top_slugs, standard_slugs, anchors_by_file):
            print(f"updated: {md}")
            changed += 1
    print(f"\nupdated {changed} files")

    residuals = verify_no_residual(DOCS_ROOT)
    if residuals:
        print(f"\nFAIL: {len(residuals)} residual internal URLs outside code blocks:", file=sys.stderr)
        for path, line_no, line in residuals:
            print(f"  {path}:{line_no}: {line}", file=sys.stderr)
        return 1
    print("verification: no residual internal URLs outside code blocks")
    return 0


if __name__ == "__main__":
    sys.exit(main())

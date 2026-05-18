#!/bin/bash
# Refresh the cherri-docs/ mirror from https://cherrilang.org/language/.
#
# Scrapes each page via defuddle, normalizes internal cross-reference URLs to
# relative .md paths, and regenerates anchors.json. Safe to re-run; idempotent.
#
# Requires: Node.js (for `npx defuddle`), Python 3.10+.

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "${SCRIPT_DIR}/../../../.." && pwd)"
BASE="https://cherrilang.org/language"
OUT="${REPO_ROOT}/cherri-docs"

mkdir -p "$OUT/standard"

fetch() {
  local path="$1"
  local url="${BASE}${path}"
  local outfile

  if [ "$path" = "/" ]; then
    outfile="${OUT}/index.md"
  else
    outfile="${OUT}/${path#/}"
    outfile="${outfile%.html}.md"
  fi

  # defuddle prints a non-fatal URL parse error to stderr on some pages; suppress.
  npx defuddle parse --markdown "$url" > "$outfile" 2>/dev/null
  echo "  fetched: ${path}"
}

echo "Scraping cherrilang.org/language/ ..."

# Top-level pages
for page in / /actions.html /comments.html /definitions.html /variables-constants-globals.html \
  /references.html /types.html /control-flow.html /menus.html /vcards.html /copy-paste.html \
  /import-questions.html /import-actions.html /includes.html /functions.html \
  /action-definitions.html /package-manager.html /raw-actions.html /best-practices.html; do
  fetch "$page"
done

# Standard library pages
for page in /standard/a11y.html /standard/intelligence.html /standard/basic.html \
  /standard/calendar.html /standard/contacts.html /standard/crypto.html /standard/device.html \
  /standard/documents.html /standard/images.html /standard/location.html /standard/macos-only.html \
  /standard/math.html /standard/media.html /standard/music.html /standard/network.html \
  /standard/pdf.html /standard/photos.html /standard/scripting.html /standard/settings.html \
  /standard/sharing.html /standard/shortcuts.html /standard/text.html /standard/translation.html \
  /standard/web.html /standard/builtin.html /standard/stdlib.html; do
  fetch "$page"
done

echo ""
echo "Normalizing cross-reference links ..."
python3 "${SCRIPT_DIR}/convert_links.py"

echo ""
echo "Regenerating anchor index ..."
python3 "${SCRIPT_DIR}/gen_anchors.py"

echo ""
echo "Refresh complete."

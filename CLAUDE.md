# Apple Shortcuts / Cherri

## Cherri Language Documentation

Local mirror of https://cherrilang.org/language/ — scraped and converted to markdown for offline LLM use. Each file corresponds to one documentation page. To re-scrape, see [Refreshing the Docs](#refreshing-the-docs) below.

### Language Reference

| File | Contents |
|------|----------|
| `cherri-docs/index.md` | Overview and offline CLI usage (`cherri --action=`, `--docs=`) |
| `cherri-docs/actions.md` | How actions work; index of standard action categories |
| `cherri-docs/definitions.md` | `#define` directives: icon color/glyph, input/output types, noinput behavior, workflows, macOS flag, name, version |
| `cherri-docs/variables-constants-globals.md` | Variables (`@var`), constants (magic variables), globals (`ShortcutInput`, `CurrentDate`, etc.), `Ask`, inline interpolation, type coercion, array append |
| `cherri-docs/references.md` | `#ref` declarations for device-bound file/media values; `--refs=` extraction workflow |
| `cherri-docs/types.md` | All value types (text, number, bool, array, dict, etc.) and content item types used in action arguments |
| `cherri-docs/control-flow.md` | `if/else`, conditional operators, `repeat`, `repeat each`, `for`, `while` |
| `cherri-docs/menus.md` | `menu` / `item` switch-style prompt; `chooseFromList()` |
| `cherri-docs/vcards.md` | `makeVCard()` built-in; building vCard-based rich menus with images |
| `cherri-docs/copy-paste.md` | `copy`/`paste` pastables — inline code reuse without function overhead |
| `cherri-docs/import-questions.md` | `#question` — setup/import questions shown before a Shortcut runs |
| `cherri-docs/import-actions.md` | `#import` — load third-party app actions from the local Shortcuts DB |
| `cherri-docs/includes.md` | `#include 'path'` — file inclusion and include chains |
| `cherri-docs/functions.md` | `function` definitions, arguments, optional params, recursion, `output()` |
| `cherri-docs/action-definitions.md` | `action 'identifier' name()` — defining reusable custom action wrappers with typed arguments and attributes |
| `cherri-docs/raw-actions.md` | `rawAction("identifier", { params })` — one-off use of any Shortcuts action by raw `WFWorkflowActionIdentifier` |
| `cherri-docs/package-manager.md` | Package structure, `info.plist`, installing/using packages from remote Git repos |
| `cherri-docs/comments.md` | Single-line (`//`) and multi-line (`/* */`) comments; comments are stripped from output by default |
| `cherri-docs/best-practices.md` | Efficiency tips: clearing unused outputs, array cost, constant vs variable tradeoffs |

### Standard Library Actions

Actions in `standard/` require `#include 'actions/<category>'` unless noted.

| File | Contents |
|------|----------|
| `cherri-docs/standard/basic.md` | Core actions: `alert()`, `confirm()`, `wait()`, `output()`, `nothing()`, `list()`, `text()` |
| `cherri-docs/standard/scripting.md` | Script control: `chooseFromList()`, `runShortcut()`, `openApp()`, `setVariable()`, date/time, notification, clipboard |
| `cherri-docs/standard/text.md` | String manipulation: split, combine, match, replace, count, format date, change case |
| `cherri-docs/standard/math.md` | `calculate()`, `roundNumber()`, statistics actions |
| `cherri-docs/standard/web.md` | URL actions, `getContentsOfURL()` (HTTP requests), open URL, expand URL |
| `cherri-docs/standard/network.md` | Network info, IP address, reachability, Wi-Fi |
| `cherri-docs/standard/device.md` | `getBatteryLevel()`, volume, brightness, screen, torch, appearance, device details |
| `cherri-docs/standard/media.md` | Photos, video, audio playback and recording actions |
| `cherri-docs/standard/music.md` | Apple Music library actions: play, search, add to library |
| `cherri-docs/standard/photos.md` | Photo library actions: get photos, albums, save to camera roll |
| `cherri-docs/standard/images.md` | Image manipulation: resize, crop, convert format, combine, overlay |
| `cherri-docs/standard/documents.md` | Files, rich text, PDF, Quick Look, match text (regex), make HTML |
| `cherri-docs/standard/pdf.md` | PDF-specific actions: make PDF, append, extract pages |
| `cherri-docs/standard/calendar.md` | Calendar events and reminders: get, create, filter |
| `cherri-docs/standard/contacts.md` | Contacts: get, filter, edit properties, `makeVCard` |
| `cherri-docs/standard/location.md` | Maps, geocoding, get current location, street address |
| `cherri-docs/standard/sharing.md` | Share sheet, AirDrop, send message, send email |
| `cherri-docs/standard/settings.md` | Toggle system settings: Wi-Fi, Bluetooth, Do Not Disturb, airplane mode |
| `cherri-docs/standard/shortcuts.md` | Shortcut-to-Shortcut: run, open, get input, create, delete |
| `cherri-docs/standard/a11y.md` | Accessibility actions: speak text, set speech rate, VoiceOver control |
| `cherri-docs/standard/intelligence.md` | Apple Intelligence actions: summarize, rewrite, proofread, prioritize |
| `cherri-docs/standard/crypto.md` | Hash actions: MD5, SHA-1, SHA-256, SHA-512 |
| `cherri-docs/standard/translation.md` | Translate text, detect language |
| `cherri-docs/standard/macos-only.md` | macOS-exclusive actions: shell script, Finder items, system events |
| `cherri-docs/standard/builtin.md` | Compiler built-ins: `containsText()`, `embedFile()` (compile-time base64 encode), `makeVCard()` |
| `cherri-docs/standard/stdlib.md` | Standard library functions (`#include 'stdlib'`): `chooseFromVCard()` and others |

---

## Refreshing the Docs

### Process Summary

Scrape `https://cherrilang.org/language/` and convert each page to markdown using `npx defuddle`. This requires Node.js but no global installs.

### Steps

**1. Identify all pages**

Fetch the index page and extract all `/language/` links from the nav. The site has two tiers:
- Top-level pages: `https://cherrilang.org/language/<page>.html`
- Standard library pages: `https://cherrilang.org/language/standard/<page>.html`

**2. Run defuddle on each URL**

```bash
npx defuddle parse --markdown <URL> > <output>.md
```

Run with `npx` — do not install globally. Defuddle v0.x is fetched automatically on first run and cached by npx.

**3. Output file mapping**

| URL pattern | Local path |
|-------------|-----------|
| `/language/` | `cherri-docs/index.md` |
| `/language/<page>.html` | `cherri-docs/<page>.md` |
| `/language/standard/<page>.html` | `cherri-docs/standard/<page>.md` |

### Known Issues Encountered

**defuddle does not accept stdin (`-` argument is not supported)**

Attempting to pipe HTML via `curl | npx defuddle -` fails with `error: unknown command '-'`. Pass the URL directly as the argument instead — defuddle fetches it internally.

```bash
# Wrong
curl -s <url> | npx defuddle - --markdown

# Correct
npx defuddle parse --markdown <url> > output.md
```

**defuddle logs a non-fatal URL parse error to stderr**

When parsing pages with relative internal links (e.g. `/language/comments.html` in `<head>` metadata), defuddle prints:

```
Failed to parse URL: TypeError: Invalid URL
    at new URL ...
```

This is a metadata extraction failure, not a content failure. The markdown content is still written to stdout correctly. Suppress with `2>/dev/null` if scripting.

**The correct subcommand is `parse`, not the top-level command**

`npx defuddle --markdown <url>` does not work. The subcommand is required:

```bash
npx defuddle parse --markdown <url>
```

### Minimal Refresh Script

```bash
#!/bin/bash
BASE="https://cherrilang.org/language"
OUT="/path/to/apple-shortcuts/cherri-docs"

fetch() {
  local path="$1"
  local url="${BASE}${path}"
  local outfile

  [ "$path" = "/" ] && outfile="${OUT}/index.md" || outfile="${OUT}/${path#/}" && outfile="${outfile%.html}.md"

  npx defuddle parse --markdown "$url" > "$outfile" 2>/dev/null
}

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
```

Run from the `apple-shortcuts/` directory. Requires Node.js. Takes ~2-3 minutes for all 45 pages.

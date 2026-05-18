# Apple Shortcuts / Cherri

## Cherri Language Documentation

Local mirror of https://cherrilang.org/language/ — scraped and converted to markdown for offline LLM use. Each file corresponds to one documentation page. To re-scrape, see [Refreshing the Docs](#refreshing-the-docs) below.

**Navigating sections within a file:** consult `cherri-docs/anchors.json` (slug → `[{file, line, heading}]`) for direct section addressing, then `Read` with `offset`/`limit` to jump straight to the relevant lines instead of reading the whole file. Slugs may map to multiple `(file, line)` entries when a heading name repeats.

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

Invoke the `refresh-cherri-docs` skill, or run directly: `bash .claude/skills/refresh-cherri-docs/scripts/refresh.sh`. The skill captures the full workflow, known defuddle gotchas, partial-refresh paths (anchor-only, link-normalize-only), and post-run verification — load it on demand instead of keeping the prose always in context. Scripts compute their own paths from script location, so they run correctly from any cwd.

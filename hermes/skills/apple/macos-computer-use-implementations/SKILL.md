---
name: macos-computer-use-implementations
description: Reference catalog of production macOS computer-use / desktop-automation open-source implementations on GitHub, plus the proven patterns (AX-first routing, CGEvent fallback, postToPid targeting, layer cascades, permission onboarding) our own macOS automation already inherits via cua-driver and should adopt when extending. Use whenever designing, debugging, or extending macOS desktop automation — instead of re-deriving how click/type/snapshot/drag work, what `element_index`/`element_at_point` semantics are, how to stay background-safe, or how to onboard Accessibility/Screen Recording permissions properly. Local research cloned at `~/.hermes/research/computer-use-macos/`.
---

# macOS Computer-Use Implementations — Reference Catalog

Distilled from a June-2026 survey of 11 production open-source macOS computer-use projects. We use `trycua/cua` (specifically `cua-driver`) as our current backend; this skill catalogs the other implementations and the concrete patterns we should adopt when our needs outgrow cua-driver's surface.

## Our current setup

- **Backend:** `cua-driver` (trycua/cua) — already installed and working
- **Exposed via:** Hermes `computer_use` tool, driven by `cua-driver mcp`
- **Modes we get:** `som` screenshots + `ax` accessibility tree + `pixel` coordinates
- **We are NOT blocked from borrowing patterns** from the 10 other projects below

## Tier-1 implementations (full working desktop automation)

| Project | Stars | Stack | Key Contribution | Repo (cloned) |
|---|---|---|---|---|
| `trycua/cua` | 19.1k | Swift + Python + Rust | **Our backend.** cua-driver is the Swift daemon we already run. | `~/.hermes/research/computer-use-macos/cua/` |
| `simular-ai/Agent-S` | 11.9k | Python | Agentic framework (planning + memory + grounding). Not macOS-specific. | not cloned — reference only |
| `bytebot-ai/bytebot` | 11.1k | Container | Self-hosted Linux desktop agent. Not macOS. | not cloned |
| `microsoft/magentic-ui` | 9.9k | Python | Browser + filesystem agent. Not macOS. | not cloned |
| `iFurySt/open-codex-computer-use` | 1.2k | Swift | **The most important reference.** Reverse-engineered Codex Computer Use, has `OpenComputerUseKit` Swift source matching OpenAI's 9-tool surface. | `~/.hermes/research/computer-use-macos/open-codex-computer-use/` |
| `ghostwright/ghost-os` | 1.5k | Swift 6.2 | AX-first perception + 29 MCP tools + self-learning recipes + CGEvent tap recording. | `~/.hermes/research/computer-use-macos/ghost-os/` |
| `macOS26/Agent` | 511 | Swift | Full SwiftUI harness for macOS 26 with 18+ LLM providers. | `~/.hermes/research/computer-use-macos/macos26-agent/` |

## Tier-2 implementations (specialized, smaller, also worth mining)

| Project | Stars | Stack | Key Contribution |
|---|---|---|---|
| `VersoXBT/desktop-pilot-mcp` | 10 | Swift 6, 427KB binary, zero deps | **The 4-layer router pattern (AX + AppleScript + CGEvent + Screenshot)** with smart per-app routing. Cleanest Swift architecture. |
| `CursorTouch/MacOS-MCP` | 95 | Python | Lightweight Python+pyobjc MCP. |
| `macuse-app/macuse-mcp` | 34 | JS | Thin MCP wrapper for the macuse macOS app. |
| `sh3ll3x3c/native-devtools-mcp` | 116 | Rust | Mac+Win+Android MCP, CDP bridge for Electron apps, AX snapshot invalidation rules. |
| `kortix-ai/agent-computer-use` | 31 | Rust | Rust crates per platform (`-macos`, `-linux`, `-windows`, `-cdp`), selector DSL with `@ref`. |
| `wimi321/macos-computer-use-skill` | 16 | TS+Python | pyautogui+pyobjc bridge with auto-bootstrapped venv. |
| `tropeai/trope-cua` | 25 | Swift+C# | Background-safe with explicit `background_safe`/`cursor_moved`/`foreground_changed` safety contract. |
| `OpenGVLab/ScaleCUA` | 1.1k | Python | ICLR 2026 Oral. Cross-platform training data + agent. Reference for architecture. |
| `xlang-ai/OpenCUA` | 790 | Python | NeurIPS 2025 Spotlight. Open foundations. |

## The 9-tool reference surface (from `open-codex-computer-use` reverse-engineering)

This is the minimal viable tool surface that matches Codex Computer Use:

```json
{
  "list_apps":              { "params": {} },
  "get_app_state":          { "params": { "app": "string", "show_full_text": "bool?" } },
  "click":                  { "params": { "app", "element_index? OR x,y", "click_count?", "mouse_button?" } },
  "perform_secondary_action":{ "params": { "app", "element_index", "action" } },
  "scroll":                 { "params": { "app", "direction", "element_index", "pages?" } },
  "drag":                   { "params": { "app", "from_x", "from_y", "to_x", "to_y" } },
  "type_text":              { "params": { "app", "text" } },
  "press_key":              { "params": { "app", "key" } },  // xdotool syntax
  "set_value":              { "params": { "app", "element_index", "value" } }
}
```

`element_index` is first-class. Coordinates are fallback. `get_app_state` aggregates screenshot + AX tree in one call (saves round-trips). All tools take `app` to scope to a specific session.

## The proven implementation patterns

### Pattern 1: AX-first routing with cascade fallback (Desktop Pilot)

`Router.bestMethodForAction(action, appName, bundleID)`:
- `snapshot` / `read` / `find` → Accessibility (only path that reads UI state)
- `click` → Accessibility (AXPress more precise than coordinate click)
- `type` → CGEvent for most apps (more reliable), Accessibility for Electron (some Electron apps swallow raw keys)
- `menu` → Accessibility (menu bar traversal)
- `script` → AppleScript for scriptable apps (Finder, Mail, Safari), Accessibility otherwise

App categorization lookup order (Router.swift):
1. Hard-coded Electron bundle-ID set → never AppleScript
2. Hard-coded scriptable bundle-ID set (Finder, Mail, Safari, etc.)
3. Dynamic `sdef` detection via `/usr/bin/sdef`
4. `com.apple.*` prefix → nativeStandard
5. Otherwise → unknown → Accessibility

### Pattern 2: Background-safe input (no cursor hijack)

**Critical insight from `trope-cua`**: every mutating action returns a safety receipt:
```json
{
  "background_safe": true,
  "cursor_moved": false,
  "foreground_changed": false
}
```

**How to achieve background safety**:
1. **Use `CGEvent.postToPid(pid)` with `.combinedSessionState` source**, NOT `.cghidEventTap`
2. This delivers events directly to the target app's process without going through the global HID queue
3. Default path does NOT call `NSRunningApplication.activate(...)` — that steals foreground
4. For `type_text`: send `keyboardSetUnicodeString` chunks (max 64 UTF-16 units each) with `postToPid`
5. Optional escape hatch `OPEN_COMPUTER_USE_ALLOW_GLOBAL_POINTER_FALLBACKS=1` for diagnostics only

**Code from `open-codex-computer-use/InputSimulation.swift`**:
```swift
static func clickTargeted(at point: CGPoint, button: MouseButtonKind, clickCount: Int, pid: pid_t) throws {
    guard let source = CGEventSource(stateID: .combinedSessionState) else { ... }
    for _ in 0..<max(clickCount, 1) {
        try postMouseEventToPid(type: .mouseMoved, source: source, point: point, button: button.cgButton, clickState: clickCount, pid: pid)
        try postMouseEventToPid(type: button.downEvent, source: source, point: point, button: button.cgButton, clickState: clickCount, pid: pid)
        try postMouseEventToPid(type: button.upEvent, source: source, point: point, button: button.cgButton, clickState: clickCount, pid: pid)
    }
}
```

### Pattern 3: AX snapshot generation invalidation (native-devtools-mcp)

Every `take_ax_snapshot` call **bumps a monotonic generation** and **invalidates prior uids**. Uids look like `a42g3` (element 42, generation 3).

**Required behavior in any agent**:
1. Snapshot immediately before each `ax_click` / `ax_set_value` / `ax_select` call
2. Treat stale uids as `snapshot_expired` errors → re-snapshot and retry
3. Cache the latest snapshot handle map inside the MCP server (not in the agent)

This is the AX analog of ref-invalidation in Playwright.

### Pattern 4: Window screenshot → AX element coordinate conversion (native-devtools-mcp)

Window captures via `screencapture -o` exclude shadow and match `kCGWindowBounds × scale` exactly. Metadata to return with every screenshot:
```json
{
  "screenshot_origin_x": 0, "screenshot_origin_y": 0,
  "screenshot_scale": 2.0,  // Retina
  "screenshot_window_id": 1234,
  "screenshot_pixel_width": 1920, "screenshot_pixel_height": 1080
}
```

Conversion: `screen_x = origin_x + (pixel_x / scale)` — never assume 1:1.

### Pattern 5: Permission onboarding is a state machine, not a prompt

From `open-codex-computer-use/docs/.../permission-onboarding.md`:
- Don't just check `AXIsProcessTrusted()` and bail.
- Build a permission state machine that tracks: Accessibility, Screen Recording, Input Monitoring separately.
- Each permission has: current state, grant callback, open-Settings callback, return-from-Settings callback.
- Provide a System Settings **accessory window** with a draggable app view (so user doesn't have to navigate to it themselves).
- Bundle "permission onboarding app" with `LSUIElement=true` (no Dock icon).
- Provide an arrow overlay window pointing to where to drag.

Trope CUA goes further: permission gating is part of the **internal IPC request pipeline**, not a UI preflight.

### Pattern 6: Click-action fallback cascade (open-codex-computer-use)

For element-targeted click on macOS, the working cascade is:
1. Try `AXSelectedChildren` first (for native row selection in lists)
2. Try `AXPress` / `AXConfirm` / `AXOpen` (semantic activations)
3. If target itself unclickable, walk descendants looking for clickable children
4. Try AX hit-test at the click point (`AXUIElementCopyElementAtPosition`)
5. Last resort: `CGEvent.postToPid` with coordinate
6. For `click_count > 1`: repeat the AX action sequence

For element-frame target (renderer-synthesized text rows), don't click the **center** — click the **leading 30% anchor** to avoid hitting adjacent rows.

For Electron rows (Slack, Lark, Discord), prefer the parent row's `AXPress` over coordinate clicks. Skip generic browser handling for WebArea — Electron-specific only.

### Pattern 7: xdotool-style keypress parser (open-codex-computer-use)

`press_key` accepts strings like `"Return"`, `"Tab"`, `"super+c"`, `"Up"`, `"KP_0"`, `"BackSpace"`, `"Page_Up"`, `"F1..F12"`, `"KP_Enter"`. Parse → virtual key codes → CGEvent. Press modifiers down, key down, key up, modifiers up (in reverse).

### Pattern 8: Self-learning workflows (ghost-os)

When the agent figures out a workflow once, save it as a JSON "recipe" with steps, parameters, and wait conditions. Next time, replay directly. Recipes are auditable, shareable, and chainable. A frontier model figures it out; a small model runs it forever.

Recipe JSON schema (from `ghost-os/GHOST-MCP.md`):
```json
{
  "name": "gmail-send",
  "parameters": [{"name": "recipient", "type": "string"}, ...],
  "steps": [
    { "action": "click", "target": "Compose", "wait": {"elementExists": "..."} },
    { "action": "type_text", "target": "...", "value": "$recipient" },
    ...
  ]
}
```

This pairs with the `ghost_learn_*` tools (CGEvent tap + AX enrichment) to record user actions.

### Pattern 9: Unified coordinate space conversion (open-codex-computer-use)

Always convert between three spaces explicitly:
- **AppKit global points** (origin top-left, y-down)
- **Screen-state points** (origin top-left, y-down, used by CGEvent location)
- **Window-local points** (relative to window origin)
- **Screenshot pixel coordinates** (need `screenshot_scale`)

Helper from `open-codex-computer-use`:
```swift
func screenshotPixelToWindowPoint(_ point: CGPoint, screenshotPixelSize: CGSize?, windowBounds: CGRect?) -> CGPoint {
    let scale = CGSize(
        width: screenshotPixelSize.width / windowBounds.width,
        height: screenshotPixelSize.height / windowBounds.height
    )
    return CGPoint(x: point.x / scale.width, y: point.y / scale.height)
}
```

### Pattern 10: AX tree compression for LLMs (open-codex-computer-use)

Raw AX trees are huge and noisy. Before returning to the LLM:
1. Compress empty `AXGroup` / `AXUnknown` wrapper nodes (don't count toward depth budget)
2. Filter `AXScrollToVisible` noise actions
3. Skip empty-string attributes
4. Budget traversal depth (e.g. 25 levels default; 64 for GTK/Web)
5. For Electron WebArea, include visible file items from `AXContents` / `AXVisibleChildren`
6. Truncate text per-element to 500 chars by default (`show_full_text: true` opt-in)

## Permission troubleshooting

Always include a `doctor` CLI command that prints:
- `Accessibility: granted/not granted`
- `Screen Recording: granted/not granted`
- `Input Monitoring: granted/not granted (for learning mode)`
- `AX Tree: X/Y apps readable`
- `MCP Config: <status>`

`hermes computer-use doctor` already does this — the message in `computer_use` tool docs says so.

## What we should adopt from this research

Since we already use cua-driver (which inherits most of these patterns), the **highest-leverage** additional patterns to adopt when needed:

1. **Tool surface expansion**: If users ask for an action cua-driver doesn't expose (e.g. `perform_secondary_action`, `scroll`, `drag`), wrap cua-driver with a thin MCP layer using `open-codex-computer-use`'s 9-tool schema as the contract. Most action requests can be satisfied by composing existing cua-driver primitives.
2. **Background-safe receipt**: When our `computer_use` tool mutates state, return a safety receipt in the result so callers know we didn't hijack cursor/focus.
3. **xdotool key parser**: If we ever need to expose `press_key` with human-readable strings, the open-codex-computer-use `KeyMapping.swift` (6.2KB) is a complete reference.
4. **Self-learning recipes**: If we automate the same flow 3+ times, save it as a recipe. ghost-os proves this works.
5. **AX session-state invalidation**: When we cache AX handles across calls, generation-tag them so stale refs error clearly instead of clicking the wrong element.

## How to use this skill

- **Diagnosing "why didn't the click work?"** → load this skill, then jump to Pattern 6 (cascade).
- **Adding a new computer-use tool to Hermes** → load this skill, pick the matching pattern, copy the Swift code from `~/.hermes/research/computer-use-macos/open-codex-computer-use/packages/OpenComputerUseKit/Sources/OpenComputerUseKit/`.
- **Investigating permission failures** → load this skill, then jump to Pattern 5 (onboarding state machine) + check `hermes computer-use doctor`.
- **Building background-safe agent automation** → load this skill, then jump to Pattern 2 (postToPid, no global HID).
- **Comparing design choices** → load this skill, look at the Tier-1/Tier-2 table to find the closest peer.

## What's NOT in this skill (would re-derive if needed)

- Full Swift source for every project — only the most-used files are sampled (`ToolDefinitions.swift`, `InputSimulation.swift`, `ComputerUseService.swift`, `Router.swift`).
- Ghidra/radare2 reverse-engineering workflow — see `open-codex-computer-use/docs/.../background-click-free-tooling.md`.
- Cursor motion model math (heading-driven Bezier, spring physics) — see `open-codex-computer-use/packages/OpenComputerUseKit/Sources/OpenComputerUseKit/CursorMotionModel.swift` and `SoftwareCursorOverlay.swift`.
- Detailed Windows/Linux runtimes — see `open-codex-computer-use/docs/exec-plans/active/20260422-windows-...` and `...linux-...`.

## Reference reading order (if you want to learn it cold)

1. `open-codex-computer-use/docs/ARCHITECTURE.md` (28KB — the full architecture spec)
2. `open-codex-computer-use/docs/references/codex-computer-use-reverse-engineering/baseline-architecture.md` (10KB — what Codex actually does)
3. `desktop-pilot-mcp/README.md` (17KB — cleanest Swift architecture)
4. `native-devtools-mcp/README.md` (25KB — most operationally mature AX patterns)
5. `open-codex-computer-use/packages/OpenComputerUseKit/Sources/OpenComputerUseKit/InputSimulation.swift` (the production reference for keyboard/mouse)
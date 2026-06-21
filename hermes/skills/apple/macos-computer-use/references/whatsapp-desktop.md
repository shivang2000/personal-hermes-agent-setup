# WhatsApp Desktop Navigation (macOS)

## AX tree quality
WhatsApp Desktop for macOS has **extremely poor AX support**. Almost all elements report as `AXButton`, `AXGroup`, or `AXStaticText` with **empty labels and zero bounds** — making element-index navigation nearly impossible by itself.

## Working navigation patterns

### 1. Menu bar (most reliable)
Standard macOS menu items have proper AX labels. Use these instead of trying to click unlabeled toolbar buttons:

| Action | Menu path | AXMenuItem label |
|---|---|---|
| New Chat | File > New Chat | `New Chat` (Cmd+N) |
| Search chats | File > Search | `Search` |
| Search within chat | Chat > Search Chat | `Search Chat` |

Pattern:
```
computer_use(action="click", app="WhatsApp", element=<MenuBarItem index>)  # e.g., File = index 52
# Capture the menu dropdown
# Click the AXMenuItem by its labeled element (e.g., "New Chat" at index 54)
```

### 2. Keyboard shortcuts
WhatsApp Desktop keyboard shortcuts that work:

| Shortcut | Action |
|---|---|
| Cmd+N | New Chat (opens popover with search field) |
| Cmd+W | Close current chat |
| Escape | Dismiss popover/modal (sometimes doesn't work — see below) |

### 3. New Chat popover
When you open New Chat (Cmd+N or File > New Chat), a popover appears with:

- `AXPopover` — the popover container
- `AXGroup "WDSNavigationBar"` — navigation bar within the popover
- `AXTextField` — search input (element ~10-12, varies)
- `AXGroup "PopoverDismissRegion"` — click to dismiss
- Various `AXStaticText` items — contact names in search results
- `AXButton` items — contact buttons after search

### 4. Dismissing popovers
Sometimes `Escape` key doesn't dismiss popovers. Dismiss with:
```
computer_use(action="click", app="WhatsApp", element=<PopoverDismissRegion>)
```

## Search results
After typing in the New Chat search field, results appear as `AXStaticText` or `AXButton` elements below the search field. Labels are typically empty, so clicking the first result involves trial-and-error with indices.

If the requested contact is not found, use a user-provided fallback name if available rather than stopping. In one run, searching `Aku` returned “No results”; the user said to try `Akansha`, which was already visible in the New Chat frequent contacts list. Clicking the corresponding AXStaticText/result element (not just the visual row coordinates) opened the chat successfully.

The `ParticipantPicker_TableView` group (element ~15) sometimes appears — this is the group creation picker, not a simple contact selector.

## Limitations / Pitfalls

- **Cannot navigate blind**: Without vision (SOM screenshots), unlabeled elements make WhatsApp almost unusable via computer_use. The AX tree alone is insufficient. Always prefer a vision-capable model for WhatsApp tasks.
- **"Cua Driver" window**: Clicking certain AX elements opens a "Cua Driver" window. This is normal — it means the AXPress action was processed but the element may not have responded visibly.
- **Group vs. individual chat**: The "New group" menu option opens a `ParticipantPicker_TableView` with checkboxes. If you need a 1:1 chat, use "New Chat" instead.
- **Popover persistence**: WhatsApp popovers sometimes persist through Escape. Always try PopoverDismissRegion as fallback.
- **Element indices shift**: Each call to `capture` re-generates indices. Never cache indices across captures.
- **Video call trap**: The chat toolbar has unlabeled video call and voice call buttons adjacent to the contact name heading. Clicking the wrong element near the top of a chat opens a calling window instead. Symptoms: window title changes to `"Aku❤️❤️ - WhatsApp video call"`, a `AXGroup "Calling_Window"` appears in the tree. To cancel a call, click the end-call button (try elements ~16-19, whichever is an AXButton; look for a second AXGroup "Toolbar" with a heading — that's the chat below the call window).
- **Blind state detection**: Without vision, detect the current view by comparing element count and structure:
  | View | Element count range | Key signatures |
  |---|---|---|
  | Chat list (main) | ~65-66 | Element 16 `AXGroup "Toolbar"`, element 17 `AXHeading`, two filter buttons at 18-19, then 8-11 buttons (chat items 24-34) |
  | Chat open | ~83-93 | Element 38 `AXGroup "Toolbar"` (second toolbar = chat toolbar), element 39 `AXHeading`, **AXTextArea** at variable index (~67-69) |
  | Video call | ~44-67 | `AXGroup "Calling_Window"`, window title ends with "- WhatsApp video call" |
  | New Chat popover | ~60-66 | `AXPopover`, `AXTextField`, `AXGroup "WDSNavigationBar"`, `AXGroup "PopoverDismissRegion"` |

## Using the chat list (main view) — alternative to New Chat popover

If an existing chat with the contact is in your chat list, you can click it directly from the main view instead of using the New Chat popover:

1. Capture WhatsApp main view (65 elements) — you should see buttons 24-34 as potential chat items
2. Click element 24 to open the first chat in the list (sorted by recency)
3. If the wrong chat opens, close with Cmd+W and try element 25, 26, etc.
4. Verify the chat opened by checking for AXTextArea in the tree (the message input field)

The chat list buttons (24-34 in main view) are the most reliable way to open an existing chat when labels are empty.

## Recovery after closing the WhatsApp window

If you accidentally close WhatsApp (e.g., Cmd+W), the app stays running but its window disappears. Reopen with:

```bash
open -a "WhatsApp"
```

The app reopens to the main chat list view automatically — no need to quit and relaunch.

## Chat list tabs affect element indices

The main view has two filter tabs at elements 18-19 ("All" / "Unread"). The "All" tab shows:
- Element 21 as `AXButton` (first chat item — typically the most recent)
- Elements 22-23 as `AXGroup` (group containers within the first chat entry)
- Elements 24-34 as additional `AXButton` chat items

When the filter state changes (e.g., after interacting with the search overlay), element 21 may become a different role or no longer be a direct chat opener. Always re-capture the fresh main view before clicking chat items.

## File > Search is in-chat, not contact search

The **File > Search** menu item (`AXMenuItem "Search"`) opens a search within the *currently open chat* — it shows a search overlay with `AXTextField` and `AXButton` filter controls. It does NOT let you search for contacts. For contacting someone, use **File > New Chat** (or Cmd+N) instead.

## Sending a message (blind workflow)

1. Open the chat (via chat list or New Chat popover)
2. Capture the window — look for element structure with ~83-93 elements
3. Locate the AXTextArea (message input field) — it's typically at index ~67-69, but in large/duplicated AX trees it may appear twice (e.g. one early index around 45 and one later duplicate). Prefer clicking the visible text-entry bar by coordinates when AX indices are ambiguous.
4. Click the AXTextArea / visible message composer to focus it
5. Type the message: `computer_use(action="type", app="WhatsApp", text="Your message")`
6. Verify the draft is visibly present in the composer before sending. If `type` reports success but the composer still looks empty, do **not** press Return yet.
7. If direct typing is unreliable, use the clipboard replacement path:
   - Set clipboard to the intended message first (e.g. `printf 'hie' | pbcopy` via terminal if terminal is available)
   - Click the composer
   - Press `cmd+a` to select any accidental draft
   - Press `cmd+v`
   - Verify the intended text is visible in the composer
8. Press Return/Enter to send: `computer_use(action="key", app="WhatsApp", keys="return")`
9. **Verify**: Re-capture. Confirm the composer is empty and the new outgoing bubble/chat preview shows the intended message. If the text is still in the composer, the send didn't register — click the composer again and use key("return") once more.

### Clipboard/paste pitfall

Do not use Cmd+V in WhatsApp unless you have just set or inspected the clipboard. During one session, pasting without resetting the clipboard inserted an unrelated Linear URL into the message composer. Recovery was: set clipboard to the intended short message with `pbcopy`, click the composer, `cmd+a`, `cmd+v`, visually verify, then Return.

## Verifying messages without vision

- The text area being empty after typing + Enter is the primary delivery signal
- If the user reports not seeing the message, you may have opened the wrong chat. Re-open the chat list and try a different chat button
- Avoid clicking elements near the contact name heading in the toolbar — those are often video/voice call buttons (index ~40-42 in chat view)

## Recovering from accidental video calls

1. You'll see the window title contains " - WhatsApp video call" and a `AXGroup "Calling_Window"`
2. Click the end-call AXButton (try elements 16-19 sequentially — one of them ends the call)
3. After the call ends, re-capture. If the window title is back to just "WhatsApp" and there's an AXTextArea, you're back in the chat
4. To exit the chat back to the chat list, press Escape or Cmd+W

## Pitfall: popover vs chat state confusion

If you use New Chat and click a result, the popover may still be visible overlaying the chat. Before typing a message, check:
- Is there a `AXGroup "PopoverDismissRegion"` still present? If so, click it to dismiss, then re-capture
- The chat view should have ~83+ elements and an AXTextArea, NOT a `AXPopover`
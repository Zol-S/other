# News Portal Article Disabler – Chrome Extension

**Version 1.3.0**

Hides articles on selected Hungarian news portals whose title or body text contains any of the keywords you define. Keywords can be seeded from a YAML file and then managed interactively via **Learning mode**.

Supported sites:

| Site                         |
|-----------------------------:|
| [24.hu](https://24.hu)       |
| [444.hu](https://444.hu)     |
| [index.hu](https://index.hu) |
| [origo.hu](https://origo.hu) |
| [telex.hu](https://telex.hu) |

---

## Table of Contents

1. [Installation](#1-installation)
2. [How automatic hiding works](#2-how-automatic-hiding-works)
3. [Hidden-count toast](#3-hidden-count-toast)
4. [Learning mode (adding & removing keywords)](#4-learning-mode-adding--removing-keywords)
5. [Tips & troubleshooting](#8-tips--troubleshooting)
6. [Privacy & permissions](#9-privacy--permissions)

---

## 1. Installation

The extension is loaded in **Developer mode** (not published to the Chrome Web Store).

1. Open Chrome and go to `chrome://extensions`.
2. Enable **Developer mode** (toggle in the top-right corner).
3. Click **Load unpacked**.
4. Select the folder that contains this extension  
   (the folder that holds `manifest.json`, `content.js`, etc.).
5. The extension appears in the toolbar. You can pin it for easier access.

**After updating any files**, return to `chrome://extensions` and click the **Reload** (circular arrow) button on the extension card.

---

## 2. How automatic hiding works

1. When you visit any of the supported sites, the content script runs at `document_idle`.
2. It loads:
   - CSS selectors for article containers from `config.yaml` (site-specific).
   - The list of blocked keywords from Chrome storage (or seeds it from `blocked_keywords.yaml` on first run).
3. Every article element that matches a configured selector is examined.
4. If the **full text** of the article (title + body snippet) contains any keyword as a **case-insensitive substring**, the article is hidden with `display: none`.
5. A MutationObserver continues to watch the page for dynamically loaded content (infinite scroll, AJAX updates, etc.) and re-applies the hiding logic after a short debounce (~1.2 s).

Keywords persist across browser sessions in `chrome.storage.local`.

---

## 3. Hidden-count toast

After the initial hide pass (and whenever the page is refreshed), a small dark toast notification appears in the **top-right corner** of the page:

- `"No articles hidden"` – nothing matched.
- `"1 article hidden"` or `"N articles hidden"`.

The toast stays visible for **5 seconds**, then fades out.  
It is purely informational and does not block interaction with the page.

---

## 4. Learning mode (adding & removing keywords)

Learning mode lets you point-and-click articles to add new blocked keywords without editing YAML files.

### Activating Learning mode

1. Navigate to any of the supported news portal.
2. Click the extension icon in the Chrome toolbar.
3. A red **L** badge appears on the icon and the tooltip changes to  
   *“Learning mode ON – click again to exit”*.
4. Article containers that match the selectors for index.hu receive a red outline highlight when you hover them.

### Adding keywords

1. While Learning mode is active, **click** a highlighted article.
2. A modal dialog opens with:
   - The full text of the article pre-filled in the input field.
   - A short hint explaining that you can edit the text or enter multiple keywords separated by commas.
   - **Add** and **Cancel** buttons.
   - A list of all currently blocked keywords at the bottom.
3. Edit the input as needed (or leave it as-is).
4. Press **Enter** or click **Add**.
5. The new keyword(s) are saved immediately and matching articles on the page are hidden at once.
6. Click the extension icon again to exit Learning mode (the **L** badge disappears).

You can also close the modal with **Cancel**, the backdrop, or the **Escape** key.

### Removing keywords

Inside the same modal (opened by clicking an article in Learning mode):

1. Scroll to the section **“Currently blocked keywords”**.
2. Click any keyword in the list.
3. The keyword is removed from storage and the list refreshes.
4. **Note:** Already-hidden articles stay hidden until you refresh the page. After removal the storage change listener re-evaluates visibility on the next storage update, but a full page reload is the most reliable way to see previously hidden articles reappear.

---

## 5. Tips & troubleshooting

| Symptom                              | Likely cause / solution                                                                 |
|--------------------------------------|-----------------------------------------------------------------------------------------|
| Icon click does nothing              | You are not on a supported news portal. Learning mode is restricted to supported news portals only.                  |
| No articles are hidden               | Check the browser console (F12) for the log of loaded keywords. Add more keywords.      |
| Toast never appears                  | The page may have loaded before the content script finished; try a hard refresh.        |
| Learning mode highlight missing      | Selectors in `config.yaml` may no longer match the live HTML. Update them and reload.   |
| Keywords disappear after reinstall   | Chrome storage is wiped when the extension is removed. Re-seed via the YAML file.       |
| Dynamic content not hidden           | The MutationObserver has a 1.2 s debounce. Wait a moment or scroll to trigger it.       |
| Want to reset all keywords           | Open DevTools → Application → Storage → Local Storage (or use the chrome.storage API) and delete the `blockedKeywords` key, then reload. |

**Developer tip:** With `LOGGING_ENABLED = true` in `content.js`, the console shows:

- The list of keywords that will be used.
- A collapsible group of every article text that was hidden.
- The toast message.

---

## 6. Privacy & permissions

The extension requests:

- **`storage`** – to persist your keyword list and Learning-mode state.
- **`activeTab`** – to communicate with the current tab when you click the icon.
- **Host permissions** only for the five listed news domains.

No data is sent to any external server. All processing happens locally in your browser.

---

*Happy filtering!*
# News Portal Article Disabler – Chrome Extension

Hides articles on news portals (like [index.hu](https://index.hu)) whose title/text contains any of the keywords listed in `blocked_keywords.yaml` (or added via learning mode).

## Features

1. **Automatic hiding**  
   On page load the extension loads the keyword list and the CSS selectors from `config.yaml`, then hides every matching article (case-insensitive substring match).

2. **Hidden-count toast**  
   After hiding, a small notification appears in the **top-right corner** of the viewport for **3 seconds**, showing how many articles were hidden.

3. **Learning mode**  
   Click the extension icon while on index.hu. A red **L** badge appears.  
   - Hover any configured article element → red outline highlight.  
   - Click it → modal with the article title pre-filled.  
   - Edit the text (or type new keywords, comma-separated).  
   - Press **Enter** or click **Add** → keywords are saved and matching articles are hidden immediately.  
   - Click the icon again to exit learning mode.

## Configuration files

### `config.yaml` – article selectors per site

```yaml
index.hu:
  - div.cimlap-anyag
  - div#pp-box li.pp-post
```

### `blocked_keywords.yaml` – initial keyword list

One keyword or phrase per line (`#` comments ignored). Used only as a seed on first run; thereafter keywords live in `chrome.storage.local`.

## Installation (developer mode)

1. Open Chrome → `chrome://extensions`
2. Enable **Developer mode**
3. Click **Load unpacked**
4. Select the folder `news-portal-article-disabler`

If you already had the extension loaded, click the **Reload** button on the extension card after updating files.

## File structure

```
index-hu-article-hider/
├── manifest.json
├── background.js          # Icon click → toggle learning mode
├── content.js             # Hiding logic + learning mode + modal + toast
├── config.yaml            # CSS selectors per site
├── blocked_keywords.yaml  # Initial keyword list
├── styles/
│   └── content.css
├── icons/
│   ├── icon16.png
│   ├── icon48.png
│   └── icon128.png
└── README.md
```
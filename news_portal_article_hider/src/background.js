const LEARNING_MODE_KEY = 'learningMode';

// Cached list of domains read from config.yaml (e.g. ["24.hu", "444.hu", ...])
let supportedDomains = null;

/**
 * Parse top-level keys from config.yaml.
 * Keys are expected to be domain names (no leading whitespace, end with ':').
 */
function parseDomainsFromConfig(text) {
	const domains = [];
	const lines = text.split(/\r?\n/);

	for (const raw of lines) {
		const trimmed = raw.trim();
		if (!trimmed || trimmed.startsWith('#')) continue;

		// Top-level key: "domain.hu:" or "domain.hu: "
		if (/^[^\s].*:$/.test(trimmed) || /^[^\s].*:\s*$/.test(trimmed)) {
			const key = trimmed.replace(/:\s*$/, '').trim();
			if (key) domains.push(key);
		}
	}

	return domains;
}

/**
 * Load (and cache) the list of supported domains from config.yaml.
 */
async function getSupportedDomains() {
	if (supportedDomains !== null) return supportedDomains;

	try {
		const url = chrome.runtime.getURL('config.yaml');
		const resp = await fetch(url);
		if (!resp.ok) {
			console.warn('[IAH] Failed to fetch config.yaml:', resp.status);
			supportedDomains = [];
			return supportedDomains;
		}
		const text = await resp.text();
		supportedDomains = parseDomainsFromConfig(text);
		console.log('[IAH] Supported domains loaded from config.yaml:', supportedDomains);
	} catch (e) {
		console.warn('[IAH] Error loading config.yaml:', e);
		supportedDomains = [];
	}

	return supportedDomains;
}

/**
 * Return true if the given URL belongs to a supported site.
 */
function isSupportedUrl(url, domains) {
	if (!url || !domains || domains.length === 0) return false;

	let hostname;
	try {
		hostname = new URL(url).hostname;
	} catch {
		return false;
	}

	return domains.some(
		(domain) => hostname === domain || hostname.endsWith('.' + domain)
	);
}

// Toggle learning mode when extension icon is clicked
chrome.action.onClicked.addListener(async (tab) => {
	if (!tab.id || !tab.url) return;

	const domains = await getSupportedDomains();
	if (!isSupportedUrl(tab.url, domains)) {
		// Not on a supported site – ignore the click
		return;
	}

	const result = await chrome.storage.local.get(LEARNING_MODE_KEY);
	const current = !!result[LEARNING_MODE_KEY];
	const next = !current;

	await chrome.storage.local.set({ [LEARNING_MODE_KEY]: next });

	// Notify the content script
	try {
		await chrome.tabs.sendMessage(tab.id, {
			type: 'TOGGLE_LEARNING_MODE',
			enabled: next
		});
	} catch (e) {
		// Content script may not be ready; it will pick up from storage on load
		console.log('Could not send message to content script:', e);
	}

	// Update badge to indicate learning mode
	if (next) {
		chrome.action.setBadgeText({ text: 'L', tabId: tab.id });
		chrome.action.setBadgeBackgroundColor({ color: '#e74c3c', tabId: tab.id });
		chrome.action.setTitle({ title: 'Learning mode ON – click again to exit', tabId: tab.id });
	} else {
		chrome.action.setBadgeText({ text: '', tabId: tab.id });
		chrome.action.setTitle({ title: 'Toggle learning mode', tabId: tab.id });
	}
});

// Keep badge in sync if storage changes from elsewhere
chrome.storage.onChanged.addListener((changes, area) => {
	if (area === 'local' && changes[LEARNING_MODE_KEY]) {
		// Badge is per-tab, so we leave it; content script handles UI
	}
});
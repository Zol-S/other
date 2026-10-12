const LEARNING_MODE_KEY = 'learningMode';

// Toggle learning mode when extension icon is clicked
chrome.action.onClicked.addListener(async (tab) => {
	if (!tab.id || !tab.url || !tab.url.includes('index.hu')) { // change this
		// Optionally notify user, but for simplicity just ignore
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
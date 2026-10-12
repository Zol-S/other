(function () {
	'use strict';

	const KEYWORDS_STORAGE_KEY = 'blockedKeywords';
	const LEARNING_MODE_KEY = 'learningMode';
	const HIGHLIGHT_CLASS = 'iah-highlight';
	const HIDDEN_CLASS = 'iah-hidden';
	const MODAL_ID = 'iah-modal';
	const TOAST_ID = 'iah-toast';
	const LOGGING_ENABLED = true;

	let keywords = [];
	let articleSelectors = null;
	let learningMode = false;
	let modalEl = null;
	let lastHiddenCount = -1;

	// ---------- Config (selectors) ----------
	async function loadConfig() {
		try {
			const url = chrome.runtime.getURL('config.yaml');
			const resp = await fetch(url);
			const text = await resp.text();

			return parseConfigSelectors(text, window.location.hostname);
		} catch (e) {
			console.warn('Failed to load config.yaml', e);
		}
	}

	function parseConfigSelectors(text, currentDomain) {
		const lines = text.split(/\r?\n/);
		let inSection = false;
		const selectors = [];

		for (const raw of lines) {
			const line = raw.replace(/\t/g, '  ');
			const trimmed = line.trim();

			if (!trimmed || trimmed.startsWith('#')) continue;

			// Top-level key (no leading spaces, ends with :)
			if (/^[^\s].*:$/.test(trimmed) || /^[^\s].*:\s*$/.test(trimmed)) {
				const key = trimmed.replace(/:\s*$/, '').trim();
				inSection = key === currentDomain;
				continue;
			}

			if (inSection) {
				// List item: "  - selector"
				const m = trimmed.match(/^-\s+(.+)$/);
				if (m) {
					selectors.push(m[1].trim());
				} else if (/^[^\s]/.test(trimmed)) {
					// Another top-level key without the trailing colon form – leave section
					inSection = false;
				}
			}
		}

		return selectors;
	}

	// ---------- Keyword loading ----------
	async function loadKeywordsFromYaml() {
		try {
			const url = chrome.runtime.getURL('blocked_keywords.yaml');
			const resp = await fetch(url);
			if (!resp.ok) return [];
			const text = await resp.text();
			const kw = parseYamlKeywords(text);
			
			if (LOGGING_ENABLED) {
				console.log('Keywords to be hidden: ' + kw.join(", "));
			}

			return kw;
		} catch (e) {
			console.warn('[IAH] Failed to load blocked_keywords.yaml', e);
			return [];
		}
	}

	function parseYamlKeywords(text) {
		return text
			.split(/\r?\n/)
			.map((line) => line.replace(/^\s*-\s*/, '').trim())
			.filter((line) => line && !line.startsWith('#'));
	}

	async function getKeywords() {
		const stored = await chrome.storage.local.get(KEYWORDS_STORAGE_KEY);
		if (Array.isArray(stored[KEYWORDS_STORAGE_KEY]) && stored[KEYWORDS_STORAGE_KEY].length > 0) {
			return stored[KEYWORDS_STORAGE_KEY];
		}

		// First run: seed from yaml
		const fromFile = await loadKeywordsFromYaml();
		if (fromFile.length > 0) {
			await chrome.storage.local.set({ [KEYWORDS_STORAGE_KEY]: fromFile });
		}

		return fromFile;
	}

	async function addKeywords(newOnes) {
		const cleaned = newOnes
			.map((k) => k.trim())
			.filter((k) => k.length > 0);

		if (cleaned.length === 0) return;

		const current = await getKeywords();
		const set = new Set(current.map((k) => k.toLowerCase()));
		let changed = false;
		for (const k of cleaned) {
			if (!set.has(k.toLowerCase())) {
				current.push(k);
				set.add(k.toLowerCase());
				changed = true;
			}
		}

		if (changed) {
			await chrome.storage.local.set({ [KEYWORDS_STORAGE_KEY]: current });
			keywords = current;
			hideMatchingArticles();
		}
	}

	async function removeKeyword(kwToRemove) {
		const current = await getKeywords();
		const next = current.filter(
			(k) => k.toLowerCase() !== kwToRemove.toLowerCase()
		);

		if (next.length === current.length) return; // nothing removed

		await chrome.storage.local.set({ [KEYWORDS_STORAGE_KEY]: next });
		keywords = next;
	}

	// ---------- Article hiding ----------
	function articleText(el) {
		return (el.textContent || '').replace(/\s+/g,' ').trim();
	}

	function matchesKeyword(text, kw) {
		if (!kw) return false;
		return text.toLowerCase().includes(kw.toLowerCase());
	}

	function queryArticles(root) {
		const scope = root || document;
		const set = new Set();
		for (const sel of articleSelectors) {
			try {
				scope.querySelectorAll(sel).forEach((el) => set.add(el));
			} catch (_) {
				/* invalid selector – ignore */
			}
		}

		return Array.from(set);
	}

	function hideMatchingArticles() {
		let hidden_count = 0;
		let hidden_articles_array = [];
		const articles = queryArticles();
		articles.forEach((art) => {
			if (art.classList.contains(HIDDEN_CLASS)) {
				hidden_count++;
				return;
			}

			const text = articleText(art);
			const shouldHide = keywords.some((kw) => matchesKeyword(text, kw));
			if (shouldHide) {
				art.classList.add(HIDDEN_CLASS);
				hidden_articles_array.push(text);
			}
		});

		const count = hidden_articles_array.length;
		if (LOGGING_ENABLED && count !== lastHiddenCount) {
			lastHiddenCount = hidden_articles_array.length
			console.groupCollapsed('Articles hidden');
			hidden_articles_array.forEach((t) => console.log(t));
			console.groupEnd();
		}
		
		return count + hidden_count;
	}

	// ---------- Toast (hidden-count notification) ----------
	function showHiddenCountToast(count) {
		// Remove any existing toast
		const existing = document.getElementById(TOAST_ID);
		if (existing) existing.remove();

		const toast = document.createElement('div');
		toast.id = TOAST_ID;
		toast.className = 'iah-toast';
		toast.setAttribute('role', 'status');
		const toastMessage = count === 0
			? 'No articles hidden'
			: count === 1
			? '1 article hidden'
			: `${count} articles hidden`;
		toast.textContent = toastMessage;

		if (LOGGING_ENABLED) {
			console.log(toastMessage);
		}

		document.body.appendChild(toast);

		// Trigger enter animation
		requestAnimationFrame(() => {
			toast.classList.add('iah-toast-visible');
		});

		// Auto-hide after 5 seconds
		setTimeout(() => {
			toast.classList.remove('iah-toast-visible');
			toast.classList.add('iah-toast-hiding');
			setTimeout(() => {
				if (toast.parentNode) toast.parentNode.removeChild(toast);
			}, 300);
		}, 5000);
	}

	// ---------- Learning mode ----------
	function bindArticle(art) {
		if (art.dataset.iahBound) return;
		art.dataset.iahBound = '1';
		art.addEventListener('mouseenter', onArticleEnter);
		art.addEventListener('mouseleave', onArticleLeave);
		art.addEventListener('click', onArticleClick, true);
	}

	function unbindArticle(art) {
		art.removeEventListener('mouseenter', onArticleEnter);
		art.removeEventListener('mouseleave', onArticleLeave);
		art.removeEventListener('click', onArticleClick, true);
		art.classList.remove(HIGHLIGHT_CLASS);
		delete art.dataset.iahBound;
	}

	function setLearningMode(enabled) {
		learningMode = enabled;
		const articles = queryArticles();
		if (enabled) {
			articles.forEach(bindArticle);
			document.body.classList.add('iah-learning');
		} else {
			articles.forEach(unbindArticle);
			document.body.classList.remove('iah-learning');
			closeModal();
		}
	}

	function onArticleEnter(e) {
		e.currentTarget.classList.add(HIGHLIGHT_CLASS);
	}

	function onArticleLeave(e) {
		e.currentTarget.classList.remove(HIGHLIGHT_CLASS);
	}

	function onArticleClick(e) {
		if (!learningMode) return;
		e.preventDefault();
		e.stopPropagation();
		e.stopImmediatePropagation();

		const art = e.currentTarget;
		const title = articleText(art);
		showModal(title, art);
	}

	// ---------- Modal ----------
	function ensureModal() {
		if (modalEl) return modalEl;

		modalEl = document.createElement('div');
		modalEl.id = MODAL_ID;
		modalEl.innerHTML = `
			<div class="iah-modal-backdrop"></div>
			<div class="iah-modal-dialog">
				<h3>Add blocked keyword(s)</h3>
				<p class="iah-hint">Edit the text below. Multiple keywords can be separated by commas. Press Enter or click Add.</p>
				<input type="text" class="iah-input" autocomplete="off" />
				<div class="iah-actions">
					<button type="button" class="iah-btn iah-btn-add">Add</button>
					<button type="button" class="iah-btn iah-btn-cancel">Cancel</button>
				</div>

				<hr class="iah-divider" />

				<h4 class="iah-list-title">Currently blocked keywords</h4>
				<p class="iah-hint iah-remove-hint">
					Click any keyword to remove it. A page refresh is required after removal.
				</p>
				<ul class="iah-keyword-list"></ul>
			</div>`;
		document.body.appendChild(modalEl);

		const input = modalEl.querySelector('.iah-input');
		const addBtn = modalEl.querySelector('.iah-btn-add');
		const cancelBtn = modalEl.querySelector('.iah-btn-cancel');
		const backdrop = modalEl.querySelector('.iah-modal-backdrop');

		const doAdd = async () => {
			const raw = input.value || '';
			const parts = raw.split(',').map((s) => s.trim()).filter(Boolean);
			await addKeywords(parts.length ? parts : [raw.trim()]);
			closeModal();
		};

		addBtn.addEventListener('click', doAdd);
		cancelBtn.addEventListener('click', closeModal);
		backdrop.addEventListener('click', closeModal);

		input.addEventListener('keydown', (ev) => {
			if (ev.key === 'Enter') {
				ev.preventDefault();
				doAdd();
			} else if (ev.key === 'Escape') {
				closeModal();
			}
		});

		return modalEl;
	}

	function renderKeywordList() {
		if (!modalEl) return;
		const list = modalEl.querySelector('.iah-keyword-list');
		if (!list) return;

		list.innerHTML = '';
		if (keywords.length === 0) {
			list.innerHTML = '<li class="iah-keyword-empty">No keywords yet</li>';
			return;
		}

		keywords.forEach((kw) => {
			const li = document.createElement('li');
			li.className = 'iah-keyword-item';
			li.textContent = kw;
			li.title = 'Click to remove';
			li.addEventListener('click', async () => {
				await removeKeyword(kw);
				renderKeywordList(); // refresh the list in the modal
			});
			list.appendChild(li);
		});
	}

	function showModal(title, articleEl) {
		const modal = ensureModal();
		const input = modal.querySelector('.iah-input');
		input.value = title || '';
		modal.classList.add('iah-visible');
		input.focus();
		input.select();
		modal._targetArticle = articleEl;

		renderKeywordList();
	}

	function closeModal() {
		if (!modalEl) return;
		modalEl.classList.remove('iah-visible');
		modalEl._targetArticle = null;
	}

	// ---------- Init & observers ----------
	async function init() {
		articleSelectors = await loadConfig();
		keywords = await getKeywords();

		const hiddenCount = hideMatchingArticles();
		showHiddenCountToast(hiddenCount);

		// Check current learning mode from storage
		const res = await chrome.storage.local.get(LEARNING_MODE_KEY);
		if (res[LEARNING_MODE_KEY]) {
			setLearningMode(true);
		}

		// Listen for toggle messages from background
		chrome.runtime.onMessage.addListener((msg, _sender, sendResponse) => {
			if (msg && msg.type === 'TOGGLE_LEARNING_MODE') {
				setLearningMode(!!msg.enabled);
				sendResponse({ ok: true });
			}

			return true;
		});

		// React to storage changes (e.g. keywords updated in another tab)
		chrome.storage.onChanged.addListener((changes, area) => {
			if (area !== 'local') return;
			if (changes[KEYWORDS_STORAGE_KEY]) {
				keywords = changes[KEYWORDS_STORAGE_KEY].newValue || [];
				// Unhide everything first then re-hide
				queryArticles().forEach((el) => el.classList.remove(HIDDEN_CLASS));
				hideMatchingArticles();
			}

			if (changes[LEARNING_MODE_KEY]) {
				setLearningMode(!!changes[LEARNING_MODE_KEY].newValue);
			}
		});

		// Watch for dynamically loaded articles
		let hideTimer = null;
		const DEBOUNCE_MS = 1200;
	
		const observer = new MutationObserver(() => {
			clearTimeout(hideTimer);
			hideTimer = setTimeout(() => {
				hideMatchingArticles();
				if (learningMode) {
					queryArticles().forEach(bindArticle);
				}
			}, DEBOUNCE_MS);
		});
		observer.observe(document.body, { childList: true, subtree: true });
	}

	if (document.readyState === 'loading') {
		document.addEventListener('DOMContentLoaded', init);
	} else {
		init();
	}
})();
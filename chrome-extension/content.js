const UI_IDS = {
  style: "sanitise-ai-style",
  toolbar: "sanitise-ai-toolbar",
  button: "sanitise-ai-button",
  detailsToggle: "sanitise-ai-details-toggle",
  panel: "sanitise-ai-panel",
  panelList: "sanitise-ai-panel-list",
  toast: "sanitise-ai-toast"
};

const SETTINGS = {
  autoModeKey: "autoModeEnabled"
};

const GENERIC_SEND_BUTTON_SELECTORS = [
  "button[data-testid='send-button']",
  "button[data-testid*='send']",
  "button[aria-label*='Send']",
  "button[aria-label*='send']",
  "button[aria-label*='Submit']",
  "button[title*='Send']"
];

const GENERIC_STOP_BUTTON_SELECTORS = [
  "button[data-testid*='stop']",
  "button[aria-label*='Stop']",
  "button[aria-label*='stop']",
  "button[title*='Stop']"
];

const POSITION_WATCH_INTERVAL_MS = 220;
const SEND_CONTEXT_CACHE_MS = 180;
const STOP_BUTTON_CACHE_MS = 180;

const SITE_CONFIGS = [
  {
    key: "chatgpt",
    hosts: ["chat.openai.com", "chatgpt.com"],
    promptSelectors: ["#prompt-textarea", "textarea", "[contenteditable='true']"],
    sendButtonSelectors: [
      "button[data-testid='send-button']",
      "button[aria-label*='Send']",
      "button[aria-label*='send']"
    ]
  },
  {
    key: "claude",
    hosts: ["claude.ai"],
    promptSelectors: ["div[contenteditable='true']", "textarea"],
    sendButtonSelectors: ["button[aria-label*='Send']", "button[aria-label*='send']"]
  },
  {
    key: "gemini",
    hosts: ["gemini.google.com"],
    promptSelectors: ["textarea", "div[contenteditable='true']"],
    sendButtonSelectors: ["button[aria-label*='Send']", "button[aria-label*='send']"]
  },
  {
    key: "perplexity",
    hosts: ["perplexity.ai"],
    promptSelectors: ["textarea", "div[contenteditable='true']"],
    sendButtonSelectors: ["button[aria-label*='Send']", "button[aria-label*='send']", "button[aria-label*='Submit']"]
  }
];

const SUPPORTED_INPUT_TYPES = new Set(["text", "search", "url", "tel", "email", "password"]);

const ENTITY_LABELS = {
  PERSON: "Person",
  EMAIL: "Email",
  PHONE: "Phone",
  ADDRESS: "Location",
  LOCATION: "Location",
  ORG: "Organisation",
  ORGANISATION: "Organisation",
  ORGANIZATION: "Organisation",
  DATE: "Date",
  URL: "Web Address",
  WEB_ADDRESS: "Web Address",
  API_KEY: "API Key",
  PRIVATE_KEY: "Private Key",
  GOVERNMENT_ID: "Government ID",
  BANK_ACCOUNT: "Bank Account",
  CREDIT_CARD: "Credit Card",
  IP_ADDRESS: "IP Address",
  USERNAME: "Username",
  COORDINATE: "Coordinate",
  FILE_PATH: "File Path",
  COMPANY_REGISTRATION_NUMBER: "Company Registration Number",
  BOOKING_REFERENCE: "Booking Reference",
  TICKET_REFERENCE: "Ticket Reference",
  ORDER_ID: "Order ID",
  TRANSACTION_ID: "Transaction ID"
};

let activeSite = detectSite(window.location.hostname);
let activeEditable = null;
let autoModeEnabled = false;
let autoSanitiseInFlight = false;
let skipNextSendClick = false;
let placementRafId = 0;
let watcherIntervalId = 0;
let toastTimeoutId = null;
let detailsOpen = false;
let lastEntityRows = [];
let submitHoldUntil = 0;
let sendContextCache = null;
let sendContextCacheAt = 0;
let stopButtonCachedValue = false;
let stopButtonCacheAt = 0;

function detectSite(hostname) {
  for (const config of SITE_CONFIGS) {
    if (config.hosts.includes(hostname)) {
      return config;
    }
  }

  return {
    key: "generic",
    hosts: [],
    promptSelectors: ["textarea", "input[type='text']", "div[contenteditable='true']"],
    sendButtonSelectors: []
  };
}

function clamp(value, min, max) {
  return Math.max(min, Math.min(max, value));
}

function truncate(text, max = 48) {
  if (!text) {
    return "";
  }
  const compact = text.replace(/\s+/g, " ").trim();
  return compact.length <= max ? compact : `${compact.slice(0, max - 1)}…`;
}

function ensureStyles() {
  if (document.getElementById(UI_IDS.style)) {
    return;
  }

  const style = document.createElement("style");
  style.id = UI_IDS.style;

  // Stable layout: fixed-width slots prevent horizontal jumping when status/details change.
  style.textContent = `
    #${UI_IDS.toolbar} {
      position: fixed;
      z-index: 2147483646;
      display: none;
      grid-template-columns: 44px 120px;
      align-items: center;
      gap: 8px;
      min-height: 32px;
      font-family: ui-sans-serif, -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif;
      transform: translateX(-100%);
      pointer-events: auto;
    }

    #${UI_IDS.detailsToggle} {
      width: 44px;
      display: inline-flex;
      justify-content: center;
      align-items: center;
      border: 0;
      background: transparent;
      color: #93c5fd;
      font-size: 11px;
      line-height: 1;
      cursor: pointer;
      opacity: 0.95;
      padding: 0;
    }

    #${UI_IDS.detailsToggle}:hover { color: #bfdbfe; }

    #${UI_IDS.detailsToggle}[disabled] {
      opacity: 0.45;
      cursor: default;
    }

    #${UI_IDS.detailsToggle}:focus-visible {
      outline: 2px solid rgba(96, 165, 250, 0.4);
      outline-offset: 2px;
      border-radius: 4px;
    }

    #${UI_IDS.button} {
      width: 120px;
      height: 32px;
      display: inline-flex;
      align-items: center;
      justify-content: center;
      gap: 6px;
      border-radius: 999px;
      border: 1px solid rgba(34, 197, 94, 0.35);
      background: rgba(22, 163, 74, 0.18);
      color: #dcfce7;
      font-size: 13px;
      font-weight: 600;
      line-height: 1;
      cursor: pointer;
      transition: background 0.15s ease, border-color 0.15s ease;
      padding: 0;
    }

    #${UI_IDS.button}:hover {
      background: rgba(22, 163, 74, 0.24);
      border-color: rgba(34, 197, 94, 0.5);
    }

    #${UI_IDS.button}:focus-visible {
      outline: 2px solid rgba(74, 222, 128, 0.4);
      outline-offset: 2px;
    }

    #${UI_IDS.button}[disabled] {
      opacity: 0.65;
      cursor: not-allowed;
    }

    #${UI_IDS.button} .sai-spinner {
      width: 12px;
      height: 12px;
      border-radius: 50%;
      border: 2px solid rgba(220, 252, 231, 0.4);
      border-top-color: #dcfce7;
      display: none;
      animation: sai-spin 0.8s linear infinite;
    }

    #${UI_IDS.button}.is-loading .sai-spinner {
      display: inline-block;
    }

    #${UI_IDS.panel} {
      position: fixed;
      z-index: 2147483647;
      display: none;
      width: min(420px, calc(100vw - 24px));
      max-height: 220px;
      overflow: auto;
      border-radius: 12px;
      border: 1px solid rgba(148, 163, 184, 0.3);
      background: rgba(24, 24, 27, 0.96);
      box-shadow: 0 12px 32px rgba(0, 0, 0, 0.35);
      padding: 10px;
      color: #e5e7eb;
      font-family: ui-sans-serif, -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif;
    }

    #${UI_IDS.panel} .sai-panel-title {
      margin: 0 0 8px;
      font-size: 12px;
      font-weight: 600;
      color: #cbd5e1;
    }

    #${UI_IDS.panelList} {
      display: flex;
      flex-direction: column;
      gap: 6px;
    }

    #${UI_IDS.panelList} .sai-row {
      display: grid;
      grid-template-columns: minmax(0, 1fr) auto;
      align-items: center;
      gap: 8px;
      border: 1px solid rgba(148, 163, 184, 0.22);
      border-radius: 8px;
      background: rgba(15, 23, 42, 0.45);
      padding: 6px 8px;
      font-size: 12px;
      line-height: 1.3;
      color: #d1d5db;
    }

    #${UI_IDS.panelList} .sai-original {
      min-width: 0;
      white-space: nowrap;
      overflow: hidden;
      text-overflow: ellipsis;
      color: #cbd5e1;
    }

    #${UI_IDS.panelList} .sai-replacement {
      color: #86efac;
      white-space: nowrap;
      font-weight: 600;
    }

    #${UI_IDS.toast} {
      position: fixed;
      right: 16px;
      bottom: 16px;
      z-index: 2147483647;
      display: none;
      max-width: min(340px, calc(100vw - 24px));
      padding: 9px 11px;
      border-radius: 10px;
      border: 1px solid rgba(148, 163, 184, 0.3);
      background: rgba(24, 24, 27, 0.96);
      color: #e5e7eb;
      font-size: 12px;
      font-weight: 600;
      opacity: 0;
      transform: translateY(3px);
      transition: opacity 0.2s ease, transform 0.2s ease;
    }

    #${UI_IDS.toast}.show {
      opacity: 1;
      transform: translateY(0);
    }

    @keyframes sai-spin {
      from { transform: rotate(0deg); }
      to { transform: rotate(360deg); }
    }

    @media (max-width: 700px) {
      #${UI_IDS.toolbar} {
        grid-template-columns: 120px;
      }
      #${UI_IDS.detailsToggle} {
        display: none !important;
      }
    }
  `;

  document.documentElement.appendChild(style);
}

function ensureUI() {
  let toolbar = document.getElementById(UI_IDS.toolbar);
  let panel = document.getElementById(UI_IDS.panel);
  let toast = document.getElementById(UI_IDS.toast);

  if (!toolbar) {
    toolbar = document.createElement("div");
    toolbar.id = UI_IDS.toolbar;

    const detailsToggle = document.createElement("button");
    detailsToggle.id = UI_IDS.detailsToggle;
    detailsToggle.type = "button";
    detailsToggle.textContent = "Details";
    detailsToggle.setAttribute("aria-expanded", "false");
    detailsToggle.addEventListener("click", () => {
      if (detailsToggle.disabled) {
        return;
      }
      detailsOpen = !detailsOpen;
      renderDetailsVisibility();
    });

    const button = document.createElement("button");
    button.id = UI_IDS.button;
    button.type = "button";
    button.innerHTML = '<span class="sai-label">Sanitise AI</span><span class="sai-spinner" aria-hidden="true"></span>';
    button.addEventListener("mousedown", (event) => event.preventDefault());
    button.addEventListener("click", async () => {
      await sanitiseActivePrompt({ showToastOnSuccess: true });
    });

    toolbar.append(detailsToggle, button);
    document.body.appendChild(toolbar);
  }

  if (!panel) {
    panel = document.createElement("div");
    panel.id = UI_IDS.panel;
    panel.innerHTML = '<p class="sai-panel-title">Detected entities</p><div id="sanitise-ai-panel-list"></div>';
    document.body.appendChild(panel);
  }

  if (!toast) {
    toast = document.createElement("div");
    toast.id = UI_IDS.toast;
    document.body.appendChild(toast);
  }
}

function getToolbar() { return document.getElementById(UI_IDS.toolbar); }
function getButton() { return document.getElementById(UI_IDS.button); }
function getDetailsToggle() { return document.getElementById(UI_IDS.detailsToggle); }
function getPanel() { return document.getElementById(UI_IDS.panel); }
function getPanelList() { return document.getElementById(UI_IDS.panelList); }
function getToast() { return document.getElementById(UI_IDS.toast); }

function isEditableElement(element) {
  if (!element || !(element instanceof Element)) {
    return false;
  }

  if (element instanceof HTMLTextAreaElement) {
    return !element.disabled && !element.readOnly;
  }

  if (element instanceof HTMLInputElement) {
    const type = (element.type || "text").toLowerCase();
    return SUPPORTED_INPUT_TYPES.has(type) && !element.disabled && !element.readOnly;
  }

  return element.isContentEditable;
}

function findEditableTarget(node) {
  if (!(node instanceof Element)) {
    return null;
  }

  if (isEditableElement(node)) {
    return node;
  }

  for (const selector of activeSite.promptSelectors) {
    const match = node.closest(selector);
    if (match && isEditableElement(match)) {
      return match;
    }
  }

  return null;
}

function findFirstEditableOnPage() {
  for (const selector of activeSite.promptSelectors) {
    const node = document.querySelector(selector);
    if (node && isEditableElement(node)) {
      return node;
    }
  }
  return null;
}

function getElementText(element) {
  if (!element) {
    return "";
  }

  if (element instanceof HTMLTextAreaElement || element instanceof HTMLInputElement) {
    return element.value || "";
  }

  return element.innerText || element.textContent || "";
}

function setElementText(element, text) {
  if (!element) {
    return;
  }

  // Keep plain-text replacement so copy/paste and native editor behavior are preserved.
  if (element instanceof HTMLTextAreaElement || element instanceof HTMLInputElement) {
    element.value = text;
    element.dispatchEvent(new Event("input", { bubbles: true }));
    element.dispatchEvent(new Event("change", { bubbles: true }));
    return;
  }

  element.textContent = text;
  element.dispatchEvent(new Event("input", { bubbles: true }));
  element.dispatchEvent(new Event("change", { bubbles: true }));
}

function getActiveSendSelectors() {
  const site = Array.isArray(activeSite.sendButtonSelectors) ? activeSite.sendButtonSelectors : [];
  return [...site, ...GENERIC_SEND_BUTTON_SELECTORS];
}

function invalidateSendContextCache() {
  sendContextCache = null;
  sendContextCacheAt = 0;
}

function invalidateStopButtonCache() {
  stopButtonCachedValue = false;
  stopButtonCacheAt = 0;
}

function isLikelySendButton(button) {
  if (!(button instanceof HTMLButtonElement)) {
    return false;
  }

  const testId = String(button.getAttribute("data-testid") || "").toLowerCase();
  const aria = String(button.getAttribute("aria-label") || "").toLowerCase();
  const title = String(button.getAttribute("title") || "").toLowerCase();
  const text = String(button.textContent || "").toLowerCase();
  const joined = `${testId} ${aria} ${title} ${text}`;

  const hasSendSignal = joined.includes("send") || joined.includes("submit");
  const hasMicSignal = joined.includes("voice") || joined.includes("microphone") || joined.includes("dictat");

  return hasSendSignal && !hasMicSignal;
}

function findSendButtonFromTarget(target) {
  if (!(target instanceof Element)) {
    return null;
  }

  for (const selector of getActiveSendSelectors()) {
    const button = target.closest(selector);
    if (button instanceof HTMLButtonElement && isLikelySendButton(button)) {
      return button;
    }
  }

  return null;
}

function findAnySendButton() {
  const buttons = [];
  const seen = new Set();
  const selector = getActiveSendSelectors().join(", ");

  if (!selector) {
    return null;
  }

  const matches = document.querySelectorAll(selector);
  for (const node of matches) {
    if (!(node instanceof HTMLButtonElement)) {
      continue;
    }
    if (!isLikelySendButton(node)) {
      continue;
    }
    if (node.offsetParent === null) {
      continue;
    }
    if (seen.has(node)) {
      continue;
    }
    seen.add(node);
    buttons.push(node);
  }

  if (!buttons.length) {
    return null;
  }

  if (!activeEditable || !document.contains(activeEditable)) {
    return buttons[0];
  }

  const targetRect = activeEditable.getBoundingClientRect();
  const targetCx = targetRect.left + targetRect.width / 2;
  const targetCy = targetRect.top + targetRect.height / 2;

  let bestButton = buttons[0];
  let bestScore = Number.POSITIVE_INFINITY;

  for (const button of buttons) {
    const r = button.getBoundingClientRect();
    const cx = r.left + r.width / 2;
    const cy = r.top + r.height / 2;
    const dx = cx - targetCx;
    const dy = cy - targetCy;
    const score = (dx * dx) + (dy * dy);
    if (score < bestScore) {
      bestScore = score;
      bestButton = button;
    }
  }

  return bestButton;
}

function isLikelyStopButton(button) {
  if (!(button instanceof HTMLButtonElement)) {
    return false;
  }

  const testId = String(button.getAttribute("data-testid") || "").toLowerCase();
  const aria = String(button.getAttribute("aria-label") || "").toLowerCase();
  const title = String(button.getAttribute("title") || "").toLowerCase();
  const text = String(button.textContent || "").toLowerCase();
  const joined = `${testId} ${aria} ${title} ${text}`;

  const hasStopSignal = joined.includes("stop")
    || joined.includes("interrupt")
    || joined.includes("cancel");
  const hasMicSignal = joined.includes("voice") || joined.includes("microphone") || joined.includes("dictat");

  return hasStopSignal && !hasMicSignal;
}

function findAnyStopButton() {
  const selector = GENERIC_STOP_BUTTON_SELECTORS.join(", ");
  if (!selector) {
    return null;
  }

  const seen = new Set();
  const matches = document.querySelectorAll(selector);
  for (const node of matches) {
    if (!(node instanceof HTMLButtonElement) || node.offsetParent === null) {
      continue;
    }
    if (seen.has(node)) {
      continue;
    }
    seen.add(node);
    if (isLikelyStopButton(node)) {
      return node;
    }
  }

  return null;
}

function markSubmitInProgress(durationMs = 2400) {
  const until = Date.now() + durationMs;
  if (until > submitHoldUntil) {
    submitHoldUntil = until;
  }
  stopButtonCachedValue = true;
  stopButtonCacheAt = Date.now();
}

function isSubmitInProgress() {
  const now = Date.now();
  if (now < submitHoldUntil) {
    return true;
  }

  if ((now - stopButtonCacheAt) < STOP_BUTTON_CACHE_MS) {
    return stopButtonCachedValue;
  }

  stopButtonCachedValue = Boolean(findAnyStopButton());
  stopButtonCacheAt = now;
  return stopButtonCachedValue;
}

function findSendContext() {
  const now = Date.now();
  if (sendContextCache && (now - sendContextCacheAt) < SEND_CONTEXT_CACHE_MS) {
    const cachedButton = sendContextCache.sendButton;
    if (cachedButton?.isConnected && cachedButton.offsetParent !== null) {
      return sendContextCache;
    }
  }

  const sendButton = findAnySendButton();
  if (!sendButton) {
    invalidateSendContextCache();
    return null;
  }

  const container = sendButton.parentElement;
  sendContextCache = { sendButton, container };
  sendContextCacheAt = now;
  return sendContextCache;
}

function isVisible(el) {
  return !!el && el.offsetParent !== null;
}

function findNearestEditableForSend(sendButton, requireText = false) {
  if (!(sendButton instanceof HTMLButtonElement)) {
    return null;
  }

  const sendRect = sendButton.getBoundingClientRect();
  const sendCx = sendRect.left + sendRect.width / 2;
  const sendCy = sendRect.top + sendRect.height / 2;

  let best = null;
  let bestScore = Number.POSITIVE_INFINITY;

  for (const selector of activeSite.promptSelectors) {
    const matches = document.querySelectorAll(selector);
    for (const node of matches) {
      if (!(node instanceof Element)) {
        continue;
      }
      if (!isEditableElement(node) || !isVisible(node)) {
        continue;
      }

      const text = getElementText(node).trim();
      if (requireText && !text) {
        continue;
      }

      const r = node.getBoundingClientRect();
      const cx = r.left + r.width / 2;
      const cy = r.top + r.height / 2;
      const dx = cx - sendCx;
      const dy = cy - sendCy;
      const score = (dx * dx) + (dy * dy);

      if (score < bestScore) {
        bestScore = score;
        best = node;
      }
    }
  }

  return best;
}

function canonicalizeBackendTokens(rawText) {
  return String(rawText || "").replace(/\[([A-Z]+(?:_[A-Z]+)*)(?:_(\d+))?\]/g, (_, rawLabel, rawIndex) => {
    const label = ENTITY_LABELS[rawLabel] || rawLabel.replace(/_/g, " ");
    return rawIndex ? `[${label} ${rawIndex}]` : `[${label}]`;
  });
}

function normaliseEntityRows(sourceText, entities) {
  if (!Array.isArray(entities)) {
    return [];
  }

  return entities.slice(0, 40).map((entity) => {
    const start = Number(entity?.start ?? -1);
    const end = Number(entity?.end ?? -1);
    const raw = start >= 0 && end > start ? sourceText.slice(start, end) : "";
    const typeKey = String(entity?.type || "ENTITY").toUpperCase();
    const label = ENTITY_LABELS[typeKey] || typeKey.replace(/_/g, " ");
    const replacement = canonicalizeBackendTokens(String(entity?.replacement || `[${label}]`));

    return {
      original: truncate(raw || label),
      replacement
    };
  });
}

function requestBackendAnonymize(text) {
  return new Promise((resolve, reject) => {
    chrome.runtime.sendMessage(
      { type: "ANONYMIZE_TEXT", payload: { text } },
      (response) => {
        if (chrome.runtime.lastError) {
          reject(new Error(chrome.runtime.lastError.message));
          return;
        }
        if (!response || response.ok !== true) {
          reject(new Error(response?.error || "Anonymize request failed"));
          return;
        }

        resolve({
          text: canonicalizeBackendTokens(String(response.anonymizedText || "")),
          entityCount: Number(response.entityCount || 0),
          entities: Array.isArray(response.entities) ? response.entities : []
        });
      }
    );
  });
}

function setStatus(message, tone = "muted") {
  // Intentionally no-op: status text was removed to keep UI stable and minimal.
  void message;
  void tone;
}

function setLoading(isLoading) {
  const button = getButton();
  if (!button) {
    return;
  }

  if (isLoading) {
    button.disabled = true;
    button.classList.add("is-loading");
    return;
  }

  button.disabled = false;
  button.classList.remove("is-loading");
}

function showToast(message, tone = "neutral") {
  const toast = getToast();
  if (!toast) {
    return;
  }

  toast.textContent = message;
  if (tone === "error") {
    toast.style.color = "#fecaca";
    toast.style.borderColor = "rgba(248, 113, 113, 0.38)";
  } else {
    toast.style.color = "#e5e7eb";
    toast.style.borderColor = "rgba(148, 163, 184, 0.3)";
  }

  toast.style.display = "block";
  requestAnimationFrame(() => toast.classList.add("show"));

  if (toastTimeoutId) {
    clearTimeout(toastTimeoutId);
  }

  toastTimeoutId = setTimeout(() => {
    toast.classList.remove("show");
    setTimeout(() => {
      const node = getToast();
      if (node && !node.classList.contains("show")) {
        node.style.display = "none";
      }
    }, 200);
  }, 2600);
}

function renderEntityPanelRows(rows) {
  const panelList = getPanelList();
  if (!panelList) {
    return;
  }

  panelList.innerHTML = "";
  for (const row of rows) {
    const item = document.createElement("div");
    item.className = "sai-row";

    const original = document.createElement("span");
    original.className = "sai-original";
    original.textContent = row.original;

    const replacement = document.createElement("span");
    replacement.className = "sai-replacement";
    replacement.textContent = row.replacement;

    item.append(original, replacement);
    panelList.appendChild(item);
  }
}

function renderDetailsVisibility() {
  const panel = getPanel();
  const toggle = getDetailsToggle();
  const toolbar = getToolbar();
  if (!panel || !toggle || !toolbar) {
    return;
  }

  if (!detailsOpen || toolbar.style.display === "none") {
    panel.style.display = "none";
    toggle.textContent = "Details";
    toggle.setAttribute("aria-expanded", "false");
    return;
  }

  panel.style.display = "block";
  const panelList = getPanelList();
  if (panelList && lastEntityRows.length === 0) {
    panelList.innerHTML = '<div class="sai-row"><span class="sai-original">No entities detected yet</span><span class="sai-replacement">—</span></div>';
  }
  const toolbarRect = toolbar.getBoundingClientRect();

  const panelWidth = panel.offsetWidth;
  const panelHeight = panel.offsetHeight;

  const left = clamp(toolbarRect.right - panelWidth, 8, window.innerWidth - panelWidth - 8);
  const preferredTop = toolbarRect.top - panelHeight - 8;
  const top = preferredTop < 8 ? toolbarRect.bottom + 8 : preferredTop;

  panel.style.left = `${Math.round(left)}px`;
  panel.style.top = `${Math.round(clamp(top, 8, window.innerHeight - panelHeight - 8))}px`;

  toggle.textContent = "Hide";
  toggle.setAttribute("aria-expanded", "true");
}

function setEntityDetails(rows) {
  const toggle = getDetailsToggle();
  if (!toggle) {
    return;
  }

  lastEntityRows = rows;
  if (rows.length === 0) {
    detailsOpen = false;
    toggle.disabled = true;
    toggle.title = "No entity details yet";
    renderDetailsVisibility();
    return;
  }

  renderEntityPanelRows(rows);
  toggle.disabled = false;
  toggle.title = "Show detected entity details";
  renderDetailsVisibility();
}

function placeToolbar() {
  const toolbar = getToolbar();
  if (!toolbar) {
    return;
  }

  if (!activeEditable || !document.contains(activeEditable)) {
    activeEditable = findFirstEditableOnPage();
  }

  if (!activeEditable || !document.contains(activeEditable)) {
    if (toolbar.style.display !== "none") {
      toolbar.style.display = "none";
    }
    detailsOpen = false;
    renderDetailsVisibility();
    return;
  }

  const liveText = getElementText(activeEditable).trim();
  const hasText = liveText.length > 0;
  const submitting = isSubmitInProgress();

  if (!hasText || submitting) {
    if (toolbar.style.display !== "none") {
      toolbar.style.display = "none";
    }
    detailsOpen = false;
    renderDetailsVisibility();
    return;
  }

  const button = getButton();
  if (button) {
    button.disabled = autoSanitiseInFlight;
    if (!autoSanitiseInFlight) {
      button.classList.remove("is-loading");
    }
  }

  if (toolbar.style.display !== "grid") {
    toolbar.style.display = "grid";
  }
  if (toolbar.parentElement !== document.body) {
    document.body.appendChild(toolbar);
  }

  const context = findSendContext();
  const editableRect = activeEditable.getBoundingClientRect();

  let top = clamp(editableRect.top - 40, 8, window.innerHeight - 40);
  let anchorX = clamp(editableRect.right - 8, 120, window.innerWidth - 8);

  if (context?.sendButton) {
    const sendRect = context.sendButton.getBoundingClientRect();
    top = clamp(sendRect.top + (sendRect.height - 32) / 2, 8, window.innerHeight - 40);

    let clusterLeft = sendRect.left;
    if (context.container) {
      const buttons = Array.from(context.container.querySelectorAll("button"))
        .filter((btn) => btn instanceof HTMLButtonElement && btn.offsetParent !== null);
      for (const btn of buttons) {
        const r = btn.getBoundingClientRect();
        const sameRow = Math.abs(r.top - sendRect.top) < 24;
        if (sameRow) {
          clusterLeft = Math.min(clusterLeft, r.left);
        }
      }
    }

    anchorX = clusterLeft - 8;
  }

  const toggle = getDetailsToggle();
  if (toggle) {
    const canShowDetails = hasText && lastEntityRows.length > 0;
    toggle.style.visibility = canShowDetails ? "visible" : "hidden";
    toggle.style.pointerEvents = canShowDetails ? "auto" : "none";
    if (!canShowDetails) {
      detailsOpen = false;
    }
  }

  const toolbarWidth = toolbar.getBoundingClientRect().width || 300;
  anchorX = clamp(anchorX, toolbarWidth + 8, window.innerWidth - 8);

  const leftPx = Math.round(anchorX);
  const topPx = Math.round(top);
  const prevLeft = Number(toolbar.dataset.leftPx || NaN);
  const prevTop = Number(toolbar.dataset.topPx || NaN);

  if (!Number.isFinite(prevLeft) || Math.abs(prevLeft - leftPx) >= 1) {
    toolbar.style.left = `${leftPx}px`;
    toolbar.dataset.leftPx = String(leftPx);
  }
  if (!Number.isFinite(prevTop) || Math.abs(prevTop - topPx) >= 1) {
    toolbar.style.top = `${topPx}px`;
    toolbar.dataset.topPx = String(topPx);
  }

  renderDetailsVisibility();
}

function schedulePlacement() {
  if (placementRafId) {
    return;
  }
  placementRafId = requestAnimationFrame(() => {
    placementRafId = 0;
    placeToolbar();
  });
}

function startPositionWatcher() {
  if (watcherIntervalId) {
    return;
  }

  watcherIntervalId = window.setInterval(() => {
    if (document.visibilityState !== "visible") {
      return;
    }

    if (!activeEditable || !document.contains(activeEditable)) {
      return;
    }

    schedulePlacement();
  }, POSITION_WATCH_INTERVAL_MS);
}

async function sanitiseActivePrompt(options = { showToastOnSuccess: true }) {
  const focused = findEditableTarget(document.activeElement);
  if (focused) {
    activeEditable = focused;
  }

  if (!activeEditable) {
    setStatus("Focus the prompt first", "warn");
    return false;
  }

  const sourceText = getElementText(activeEditable).trim();
  if (!sourceText) {
    setStatus("Prompt is empty", "warn");
    return false;
  }

  if (autoSanitiseInFlight) {
    return false;
  }

  autoSanitiseInFlight = true;
  setLoading(true);
  setStatus("Sanitising…", "muted");

  try {
    const result = await requestBackendAnonymize(sourceText);
    setElementText(activeEditable, result.text || sourceText);

    const rows = normaliseEntityRows(sourceText, result.entities);
    setEntityDetails(rows);

    const count = Number(result.entityCount || rows.length || 0);
    if (count > 0) {
      setStatus(`${count} entities sanitised`, "ok");
      if (options.showToastOnSuccess) {
        showToast(`${count} entities anonymised`, "ok");
      }
    } else {
      setStatus("No sensitive entities found", "muted");
      if (options.showToastOnSuccess) {
        showToast("No sensitive entities found", "ok");
      }
    }

    schedulePlacement();
    return true;
  } catch (error) {
    const message = error?.message || "backend unavailable";
    setStatus("Sanitise failed", "error");
    showToast(`Sanitise failed: ${message}`, "error");
    return false;
  } finally {
    setLoading(false);
    autoSanitiseInFlight = false;
  }
}

async function autoSanitiseThenSend(sendButton) {
  const ok = await sanitiseActivePrompt({ showToastOnSuccess: false });
  if (!ok) {
    return;
  }

  setStatus("Sanitised. Sending…", "ok");
  const buttonToClick = sendButton?.isConnected ? sendButton : findAnySendButton();
  if (buttonToClick) {
    markSubmitInProgress();
    skipNextSendClick = true;
    setTimeout(() => {
      buttonToClick.click();
    }, 0);
  }
}

async function handleContextMenuSanitise(selectedText) {
  const focused = findEditableTarget(document.activeElement);
  if (focused) {
    activeEditable = focused;
  }

  const text = String(selectedText || "").trim();
  if (!text) {
    return;
  }

  try {
    const result = await requestBackendAnonymize(text);
    if (activeEditable) {
      const current = getElementText(activeEditable);
      if (current.includes(text)) {
        setElementText(activeEditable, current.replace(text, result.text));
      } else {
        setElementText(activeEditable, result.text);
      }
      setStatus(`${result.entityCount || 0} entities sanitised`, "ok");
      schedulePlacement();
    }
    showToast(`${result.entityCount || 0} entities anonymised`, "ok");
  } catch (error) {
    showToast(`Sanitise failed: ${error?.message || "backend unavailable"}`, "error");
  }
}

function setActiveEditableFromNode(node) {
  const target = findEditableTarget(node instanceof Element ? node : null);
  if (!target) {
    activeEditable = null;
    invalidateSendContextCache();
    schedulePlacement();
    return;
  }

  activeEditable = target;
  invalidateSendContextCache();
  schedulePlacement();
}

function bindEvents() {
  document.addEventListener("click", (event) => {
    if (autoModeEnabled || skipNextSendClick) {
      return;
    }

    const sendButton = findSendButtonFromTarget(event.target);
    if (!sendButton) {
      return;
    }

    const focused = findEditableTarget(document.activeElement);
    const candidate = focused || findNearestEditableForSend(sendButton, true);
    if (!candidate || !getElementText(candidate).trim()) {
      return;
    }

    markSubmitInProgress();
  }, true);

  document.addEventListener("click", (event) => {
    if (!autoModeEnabled) {
      return;
    }

    const sendButton = findSendButtonFromTarget(event.target);
    if (!sendButton) {
      return;
    }

    if (skipNextSendClick) {
      skipNextSendClick = false;
      return;
    }

    const focused = findEditableTarget(document.activeElement);
    const nearestWithText = findNearestEditableForSend(sendButton, true);
    const nearestAny = findNearestEditableForSend(sendButton, false);
    activeEditable = focused && getElementText(focused).trim()
      ? focused
      : (nearestWithText || nearestAny || focused || null);

    if (!activeEditable || !getElementText(activeEditable).trim()) {
      return;
    }

    event.preventDefault();
    event.stopImmediatePropagation();
    invalidateSendContextCache();
    autoSanitiseThenSend(sendButton);
  }, true);

  document.addEventListener("keydown", (event) => {
    if (autoModeEnabled || event.isComposing) {
      return;
    }

    if (event.key !== "Enter" || event.shiftKey || event.altKey || event.ctrlKey || event.metaKey) {
      return;
    }

    const sendButton = findAnySendButton();
    if (!sendButton) {
      return;
    }

    const focused = findEditableTarget(document.activeElement);
    const nearestWithText = findNearestEditableForSend(sendButton, true);
    const candidate = focused && getElementText(focused).trim() ? focused : nearestWithText;
    if (!candidate || !getElementText(candidate).trim()) {
      return;
    }

    markSubmitInProgress();
  }, true);

  document.addEventListener("keydown", (event) => {
    if (!autoModeEnabled || event.isComposing) {
      return;
    }

    if (event.key !== "Enter" || event.shiftKey || event.altKey || event.ctrlKey || event.metaKey) {
      return;
    }

    const sendButton = findAnySendButton();
    if (!sendButton) {
      return;
    }

    const focused = findEditableTarget(document.activeElement);
    const nearestWithText = findNearestEditableForSend(sendButton, true);
    const nearestAny = findNearestEditableForSend(sendButton, false);
    activeEditable = focused && getElementText(focused).trim()
      ? focused
      : (nearestWithText || nearestAny || focused || null);

    if (!activeEditable || !getElementText(activeEditable).trim()) {
      return;
    }

    event.preventDefault();
    event.stopImmediatePropagation();
    invalidateSendContextCache();
    autoSanitiseThenSend(sendButton);
  }, true);

  document.addEventListener("focusin", (event) => {
    setActiveEditableFromNode(event.target);
  });

  document.addEventListener("focusout", () => {
    setTimeout(() => {
      setActiveEditableFromNode(document.activeElement);
    }, 0);
  });

  document.addEventListener("input", (event) => {
    const target = findEditableTarget(event.target);
    if (!target) {
      return;
    }
    activeEditable = target;
    invalidateSendContextCache();
    invalidateStopButtonCache();
    schedulePlacement();
  }, true);

  document.addEventListener("click", (event) => {
    const toolbar = getToolbar();
    const panel = getPanel();

    if (toolbar && toolbar.contains(event.target)) {
      return;
    }
    if (panel && panel.contains(event.target)) {
      return;
    }

    if (detailsOpen) {
      detailsOpen = false;
      renderDetailsVisibility();
    }

    setActiveEditableFromNode(event.target);
  });

  window.addEventListener("resize", () => {
    invalidateSendContextCache();
    schedulePlacement();
  });
  window.addEventListener("scroll", () => {
    invalidateSendContextCache();
    schedulePlacement();
  }, true);

  chrome.runtime.onMessage.addListener((message) => {
    if (!message || message.type !== "SANITISE_SELECTED_TEXT") {
      return;
    }
    handleContextMenuSanitise(message.payload?.text || "");
  });
}

function loadSettings() {
  chrome.storage.local.get({ [SETTINGS.autoModeKey]: false }, (data) => {
    autoModeEnabled = Boolean(data?.[SETTINGS.autoModeKey]);
  });

  chrome.storage.onChanged.addListener((changes, areaName) => {
    if (areaName !== "local" || !changes[SETTINGS.autoModeKey]) {
      return;
    }
    autoModeEnabled = Boolean(changes[SETTINGS.autoModeKey].newValue);
  });
}

function init() {
  activeSite = detectSite(window.location.hostname);
  ensureStyles();
  ensureUI();
  loadSettings();
  bindEvents();
  schedulePlacement();
  startPositionWatcher();
}

init();

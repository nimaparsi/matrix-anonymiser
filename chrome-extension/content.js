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
  "#composer-submit-button",
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
      "#composer-submit-button",
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
    hosts: ["perplexity.ai", "www.perplexity.ai"],
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
  CRYPTO_WALLET: "Crypto Wallet",
  PRIVATE_KEY: "Private Key",
  GOVERNMENT_ID: "Government ID",
  BANK_ACCOUNT: "Bank Account",
  CREDIT_CARD: "Credit Card",
  IP_ADDRESS: "IP Address",
  USERNAME: "Username",
  COORDINATE: "Coordinate",
  FILE_PATH: "File Path",
  COMPANY_REGISTRATION_NUMBER: "Company Registration Number",
  EMPLOYEE_ID: "Employee ID",
  INVOICE_NUMBER: "Invoice Number",
  BOOKING_REFERENCE: "Booking Reference",
  TICKET_REFERENCE: "Ticket Reference",
  ORDER_ID: "Order ID",
  TRANSACTION_ID: "Transaction ID"
};

let activeSite = detectSite(window.location.hostname);
let activeEditable = null;
let autoModeEnabled = false;
let autoSanitiseInFlight = false;
let bypassNextFormSubmit = false;
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

  style.textContent = `
    #sanitise-ai-toolbar { position:fixed; z-index:2147483646; display:none; grid-template-columns:44px 152px; gap:8px; align-items:center; font-family:Manrope,system-ui,sans-serif; transform:translateX(-100%); }
    #sanitise-ai-toolbar button { box-sizing:border-box; margin:0; font-family:inherit; cursor:pointer; }
    #sanitise-ai-details-toggle { width:44px; height:44px; padding:0; display:grid; place-items:center; border:1px solid #dce1ff; border-radius:50%; background:#fff; color:#0049db; font:700 18px Georgia,serif; box-shadow:0 4px 16px #0049db12; }
    #sanitise-ai-button { width:152px; height:44px; padding:0 15px; display:flex; align-items:center; justify-content:center; gap:9px; border:0; border-radius:14px; background:linear-gradient(135deg,#0049db,#2962ff); color:#fff; font-size:14px; font-weight:700; box-shadow:0 8px 24px #0049db30; transition:filter .15s,transform .15s; }
    #sanitise-ai-button:hover:not(:disabled) { filter:brightness(1.08); transform:translateY(-1px); }
    #sanitise-ai-button:disabled { cursor:wait; opacity:.8; }
    #sanitise-ai-toolbar button:focus-visible { outline:3px solid #b6c4ff; outline-offset:3px; }
    #sanitise-ai-button .sai-spinner { display:none; width:14px; height:14px; border:2px solid #ffffff66; border-top-color:#fff; border-radius:50%; animation:sai-spin .8s linear infinite; }
    #sanitise-ai-button.is-loading .sai-spinner { display:block; }
    #sanitise-ai-panel { box-sizing:border-box; position:fixed; z-index:2147483647; display:none; width:min(310px,calc(100vw - 24px)); max-height:260px; overflow:auto; border:1px solid #dce1ff; border-radius:16px; padding:16px; background:#fffffff5; backdrop-filter:blur(20px); box-shadow:0 12px 36px #0049db18; color:#1b1c1c; font:13px/1.5 Manrope,system-ui,sans-serif; }
    #sanitise-ai-panel .sai-panel-title { margin:0 0 8px; font-weight:700; font-size:14px; }
    #sanitise-ai-panel-list { display:flex; flex-direction:column; gap:6px; }
    #sanitise-ai-panel-list .sai-row { display:flex; justify-content:space-between; gap:12px; padding:7px 9px; background:#f3f5ff; border-radius:8px; }
    #sanitise-ai-panel-list .sai-replacement { color:#0049db; font-weight:700; }
    #sanitise-ai-toast { position:fixed; right:20px; bottom:84px; z-index:2147483647; display:none; max-width:min(340px,calc(100vw - 40px)); padding:12px 16px; border-radius:12px; background:#101d3d; border:1px solid #344774; color:#fff; font:13px/1.5 system-ui,sans-serif; }
    @keyframes sai-spin { to { transform:rotate(360deg); } }
    @media(prefers-reduced-motion:reduce) { #sanitise-ai-button { transition:none; } }
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
    detailsToggle.textContent = "i";
    detailsToggle.setAttribute('aria-label', 'Sanitisation summary');
    detailsToggle.setAttribute('aria-describedby', UI_IDS.panel);
    detailsToggle.setAttribute('aria-controls', UI_IDS.panel);
    const showDetails = () => { detailsOpen = true; renderDetailsVisibility(); };
    const hideDetails = () => { detailsOpen = false; renderDetailsVisibility(); };
    detailsToggle.addEventListener('mouseenter', showDetails);
    detailsToggle.addEventListener('focus', showDetails);
    toolbar.addEventListener('mouseleave', event => { if (!getPanel()?.contains(event.relatedTarget)) hideDetails(); });
    detailsToggle.addEventListener('keydown', event => { if (event.key === 'Escape') { event.stopPropagation(); hideDetails(); } });
    detailsToggle.setAttribute("aria-expanded", "false");
    detailsToggle.addEventListener("click", () => {
      if (detailsToggle.disabled) {
        return;
      }
      detailsOpen = true;
      renderDetailsVisibility();
    });

    const button = document.createElement("button");
    button.id = UI_IDS.button;
    button.type = "button";
    button.innerHTML = '<span class="sai-label">Sanitise</span><span class="sai-spinner" aria-hidden="true"></span>';
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
    panel.setAttribute('role', 'tooltip');
    panel.addEventListener('mouseleave', () => { detailsOpen = false; renderDetailsVisibility(); });
    panel.innerHTML = '<p class="sai-panel-title">Sanitisation summary</p><div id="sanitise-ai-panel-list"></div>';
    document.body.appendChild(panel);
  }

  if (!toast) {
    toast = document.createElement("div");
    toast.id = UI_IDS.toast;
    toast.setAttribute('role', 'status');
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
    return false;
  }

  if (element instanceof HTMLTextAreaElement || element instanceof HTMLInputElement) {
    const prototype = element instanceof HTMLTextAreaElement
      ? HTMLTextAreaElement.prototype
      : HTMLInputElement.prototype;
    const setter = Object.getOwnPropertyDescriptor(prototype, "value")?.set;
    if (setter) {
      setter.call(element, text);
    } else {
      element.value = text;
    }
    element.dispatchEvent(new InputEvent("input", {
      bubbles: true,
      composed: true,
      data: text,
      inputType: "insertText"
    }));
    element.dispatchEvent(new Event("change", { bubbles: true }));
    return element.value === text;
  }

  if (!element.isContentEditable) {
    return false;
  }

  element.focus({ preventScroll: true });
  const selection = window.getSelection();
  const range = document.createRange();
  range.selectNodeContents(element);
  selection?.removeAllRanges();
  selection?.addRange(range);

  let updated = false;
  try {
    updated = document.execCommand("insertText", false, text);
  } catch (_error) {
    updated = false;
  }

  if (!updated) {
    element.textContent = text;
    element.dispatchEvent(new InputEvent("input", {
      bubbles: true,
      composed: true,
      data: text,
      inputType: "insertText"
    }));
  }

  element.dispatchEvent(new Event("change", { bubbles: true }));
  return getElementText(element).trim() === String(text).trim();
}

function nextFrame() {
  return new Promise((resolve) => requestAnimationFrame(resolve));
}

async function waitForEditorUpdate(element, expectedText) {
  for (let attempt = 0; attempt < 8; attempt += 1) {
    if (getElementText(element).trim() === String(expectedText).trim()) {
      return true;
    }
    await nextFrame();
  }
  return false;
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

function normaliseEntityRows(_sourceText, entities) {
  const counts = new Map();
  for (const entity of Array.isArray(entities) ? entities : []) {
    const type = String(entity?.type || 'ENTITY').toUpperCase();
    const label = ENTITY_LABELS[type] || type.replace(/_/g, ' ');
    counts.set(label, (counts.get(label) || 0) + 1);
  }
  return Array.from(counts, ([original, count]) => ({ original, replacement: String(count) }));
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

  button.setAttribute('aria-busy', String(isLoading));
  button.querySelector('.sai-label').textContent = isLoading ? 'Sanitising...' : 'Sanitise';
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
    toggle.textContent = "i";
    toggle.setAttribute("aria-expanded", "false");
    return;
  }

  panel.style.display = "block";
  const panelList = getPanelList();
  if (panelList && lastEntityRows.length === 0) {
    panelList.innerHTML = '<div class="sai-row"><span class="sai-original">Run Sanitise to see counts. Always review the result before sending.</span><span class="sai-replacement">—</span></div>';
  }
  const toolbarRect = toolbar.getBoundingClientRect();

  const panelWidth = panel.offsetWidth;
  const panelHeight = panel.offsetHeight;

  const left = clamp(toolbarRect.right - panelWidth, 8, window.innerWidth - panelWidth - 8);
  const preferredTop = toolbarRect.top - panelHeight - 8;
  const top = preferredTop < 8 ? toolbarRect.bottom + 8 : preferredTop;

  panel.style.left = `${Math.round(left)}px`;
  panel.style.top = `${Math.round(clamp(top, 8, window.innerHeight - panelHeight - 8))}px`;

  toggle.textContent = "i";
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
    toggle.disabled = false;
    toggle.title = "Run Sanitise to see a summary";
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

  const top = Math.max(8, window.innerHeight - 64);
  let anchorX = window.innerWidth - 20;
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

  const editor = activeEditable;
  const sourceSnapshot = getElementText(editor);
  const sourceText = sourceSnapshot.trim();
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
    if (!editor.isConnected || activeEditable !== editor || getElementText(editor) !== sourceSnapshot) {
      throw new Error('Your draft changed while sanitising. Run it again; your edits were preserved.');
    }
    const replacementText = result.text;
    const didSetText = setElementText(editor, replacementText);
    const didSyncEditor = didSetText && await waitForEditorUpdate(editor, replacementText);
    if (!didSyncEditor) {
      throw new Error("The AI editor did not accept the sanitised text");
    }

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

function findEditableForForm(form, submitter) {
  for (const selector of activeSite.promptSelectors) {
    const candidates = form.querySelectorAll(selector);
    for (const candidate of candidates) {
      if (isEditableElement(candidate) && isVisible(candidate)) {
        return candidate;
      }
    }
  }

  return findNearestEditableForSend(submitter, true)
    || findNearestEditableForSend(submitter, false)
    || null;
}

function resumeNativeSubmit(form, preferredSubmitter) {
  const currentSubmitter = preferredSubmitter?.isConnected && !preferredSubmitter.disabled
    ? preferredSubmitter
    : Array.from(form.querySelectorAll("button")).find((button) => (
      button instanceof HTMLButtonElement
      && isLikelySendButton(button)
      && !button.disabled
      && button.offsetParent !== null
    ));

  bypassNextFormSubmit = true;
  try {
    if (typeof form.requestSubmit === "function") {
      form.requestSubmit(currentSubmitter || undefined);
    } else if (currentSubmitter) {
      currentSubmitter.click();
    } else {
      showToast("Could not find the send control. Your prompt is still sanitised.", "error");
    }
  } catch (error) {
    showToast("Could not send automatically: " + (error?.message || "send unavailable"), "error");
  } finally {
    bypassNextFormSubmit = false;
  }
}

async function autoSanitiseThenSubmit(form, submitter, editable) {
  activeEditable = editable;
  const ok = await sanitiseActivePrompt({ showToastOnSuccess: false });
  if (!ok) {
    return;
  }

  await nextFrame();
  await nextFrame();
  const liveForm = editable.closest("form") || (form.isConnected ? form : null);
  if (!liveForm) {
    showToast("Your prompt was sanitised, but the send form changed. Press Send again.", "error");
    return;
  }
  markSubmitInProgress();
  resumeNativeSubmit(liveForm, submitter);
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

  const editor = activeEditable;
  const snapshot = editor ? getElementText(editor) : '';
  if (!editor || !snapshot.includes(text)) {
    showToast('Select text inside an editable prompt first.', 'error');
    return;
  }

  try {
    const result = await requestBackendAnonymize(text);
    if (!editor.isConnected || getElementText(editor) !== snapshot) {
      throw new Error('Your draft changed. Select the text and try again.');
    }
    if (editor) {
      const current = getElementText(editor);
      if (current.includes(text)) {
        const replacement = current.replace(text, result.text);
        if (!setElementText(editor, replacement) || !await waitForEditorUpdate(editor, replacement)) {
          throw new Error('The editor did not accept the replacement. Review your draft.');
        }
        setEntityDetails(normaliseEntityRows(text, result.entities));
      } else {
        throw new Error('Selected text is no longer in the editor. Select it again.');
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
    if (node instanceof Element && (getToolbar()?.contains(node) || getPanel()?.contains(node))) return;
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
  document.addEventListener("submit", (event) => {
    if (bypassNextFormSubmit) {
      bypassNextFormSubmit = false;
      return;
    }

    if (!autoModeEnabled) {
      return;
    }

    const form = event.target;
    if (!(form instanceof HTMLFormElement)) {
      return;
    }

    const submitter = event.submitter instanceof HTMLButtonElement
      ? event.submitter
      : Array.from(form.querySelectorAll("button")).find(isLikelySendButton);
    if (!(submitter instanceof HTMLButtonElement) || !isLikelySendButton(submitter)) {
      return;
    }

    if (autoSanitiseInFlight) {
      event.preventDefault();
      event.stopImmediatePropagation();
      return;
    }

    const editable = findEditableForForm(form, submitter);
    if (!editable || !getElementText(editable).trim()) {
      return;
    }

    event.preventDefault();
    event.stopImmediatePropagation();
    invalidateSendContextCache();
    void autoSanitiseThenSubmit(form, submitter, editable);
  }, true);

  document.addEventListener("click", (event) => {
    const sendButton = findSendButtonFromTarget(event.target);
    if (sendButton && !autoModeEnabled) {
      markSubmitInProgress();
    }
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
    setEntityDetails([]);
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

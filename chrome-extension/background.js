const CONTEXT_MENU_ID = "sanitise-ai-context-menu";
const ANONYMIZE_API_URL = "https://sanitiseai.com/api/anonymize";
const REQUEST_TIMEOUT_MS = 20000;
const SUPPORTED_PAGE_PATTERNS = [
  "https://chat.openai.com/*",
  "https://chatgpt.com/*",
  "https://claude.ai/*",
  "https://gemini.google.com/*",
  "https://perplexity.ai/*",
  "https://www.perplexity.ai/*"
];
const DEFAULT_TAG_STYLE = "standard";
const DEFAULT_REVERSE_PRONOUNS = false;
const DEFAULT_ENTITY_TYPES = [
  "PERSON",
  "EMAIL",
  "PHONE",
  "ADDRESS",
  "ORG",
  "DATE",
  "URL",
  "API_KEY",
  "CRYPTO_WALLET",
  "CREDIT_CARD",
  "GOVERNMENT_ID",
  "BANK_ACCOUNT",
  "PRIVATE_KEY",
  "COMPANY_REGISTRATION_NUMBER",
  "INVOICE_NUMBER",
  "EMPLOYEE_ID",
  "BOOKING_REFERENCE",
  "TICKET_REFERENCE",
  "ORDER_ID",
  "TRANSACTION_ID",
  "IP_ADDRESS",
  "USERNAME",
  "COORDINATE",
  "FILE_PATH"
];

chrome.runtime.onInstalled.addListener(() => {
  chrome.contextMenus.removeAll(() => {
    chrome.contextMenus.create({
      id: CONTEXT_MENU_ID,
      title: "Sanitise with Sanitise AI",
      contexts: ["selection"],
      documentUrlPatterns: SUPPORTED_PAGE_PATTERNS
    });
  });
});

chrome.contextMenus.onClicked.addListener(async (info, tab) => {
  if (info.menuItemId !== CONTEXT_MENU_ID) {
    return;
  }

  if (!tab || typeof tab.id !== "number") {
    return;
  }

  const selectedText = info.selectionText || "";

  try {
    await chrome.tabs.sendMessage(tab.id, {
      type: "SANITISE_SELECTED_TEXT",
      payload: {
        text: selectedText
      }
    });
  } catch (error) {
    console.error("Sanitise AI failed to send message to content script", error);
  }
});

chrome.runtime.onMessage.addListener((message, _sender, sendResponse) => {
  if (!message || message.type !== "ANONYMIZE_TEXT") {
    return false;
  }

  (async () => {
    try {
      const text = String(message.payload?.text || "");
      if (!text.trim()) {
        sendResponse({ ok: false, error: "Text is empty" });
        return;
      }

      const controller = new AbortController();
      const timeoutId = setTimeout(() => controller.abort(), REQUEST_TIMEOUT_MS);
      let response;

      try {
        response = await fetch(ANONYMIZE_API_URL, {
          method: "POST",
          headers: {
            "Content-Type": "application/json"
          },
          signal: controller.signal,
          body: JSON.stringify({
            text,
            entity_types: DEFAULT_ENTITY_TYPES,
            tag_style: DEFAULT_TAG_STYLE,
            reversePronouns: DEFAULT_REVERSE_PRONOUNS,
            reverse_pronouns: DEFAULT_REVERSE_PRONOUNS
          })
        });
      } finally {
        clearTimeout(timeoutId);
      }

      const data = await response.json().catch(() => ({}));
      if (!response.ok) {
        sendResponse({
          ok: false,
          error: data?.detail?.message || (typeof data?.detail === "string" ? data.detail : "") || `API error ${response.status}`
        });
        return;
      }

      if (typeof data?.anonymized_text !== 'string' || !data.anonymized_text.trim()) {
        sendResponse({ ok: false, error: 'The service returned no usable text. Your draft was not changed.' });
        return;
      }
      sendResponse({
        ok: true,
        anonymizedText: data?.anonymized_text || "",
        entityCount: Array.isArray(data?.entities) ? data.entities.length : 0,
        entities: Array.isArray(data?.entities) ? data.entities : []
      });
    } catch (error) {
      sendResponse({
        ok: false,
        error: error?.name === "AbortError"
          ? "Sanitising timed out. Please try again."
          : (error?.message || "Request failed")
      });
    }
  })();

  return true;
});

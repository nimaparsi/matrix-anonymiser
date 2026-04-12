const CONTEXT_MENU_ID = "sanitise-ai-context-menu";
const ANONYMIZE_API_URL = "https://matrix-anonymiser.netlify.app/api/anonymize";
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
  "CREDIT_CARD",
  "GOVERNMENT_ID",
  "BANK_ACCOUNT",
  "PRIVATE_KEY",
  "COMPANY_REGISTRATION_NUMBER",
  "INVOICE_NUMBER",
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
  chrome.contextMenus.create({
    id: CONTEXT_MENU_ID,
    title: "Sanitise with Sanitise AI",
    contexts: ["selection"]
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

      const response = await fetch(ANONYMIZE_API_URL, {
        method: "POST",
        headers: {
          "Content-Type": "application/json"
        },
        body: JSON.stringify({
          text,
          entity_types: DEFAULT_ENTITY_TYPES,
          tag_style: DEFAULT_TAG_STYLE,
          reversePronouns: DEFAULT_REVERSE_PRONOUNS,
          reverse_pronouns: DEFAULT_REVERSE_PRONOUNS
        })
      });

      const data = await response.json().catch(() => ({}));
      if (!response.ok) {
        sendResponse({
          ok: false,
          error: data?.detail?.message || data?.detail || `API error ${response.status}`
        });
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
        error: error?.message || "Request failed"
      });
    }
  })();

  return true;
});

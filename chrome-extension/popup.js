const openButton = document.getElementById("open-sanitise");
const quickButton = document.getElementById("quick-sanitise");
const quickInput = document.getElementById("quick-input");
const quickStatus = document.getElementById("quick-status");
const autoModeToggle = document.getElementById("auto-mode-toggle");
const AUTO_MODE_KEY = "autoModeEnabled";

function canonicalizeBackendTokens(rawText) {
  const labelMap = {
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

  return String(rawText || "").replace(/\[([A-Z]+(?:_[A-Z]+)*)(?:_(\d+))?\]/g, (_, rawLabel, rawIndex) => {
    const label = labelMap[rawLabel] || rawLabel.replace(/_/g, " ");
    return rawIndex ? `[${label} ${rawIndex}]` : `[${label}]`;
  });
}

if (openButton) {
  openButton.addEventListener("click", () => {
    chrome.tabs.create({ url: "https://sanitiseai.com" });
  });
}

if (autoModeToggle) {
  chrome.storage.local.get({ [AUTO_MODE_KEY]: false }, (data) => {
    autoModeToggle.checked = Boolean(data?.[AUTO_MODE_KEY]);
  });

  autoModeToggle.addEventListener("change", () => {
    chrome.storage.local.set({ [AUTO_MODE_KEY]: autoModeToggle.checked });
  });
}

function setQuickLoading(isLoading) {
  if (!quickButton) {
    return;
  }
  quickButton.disabled = isLoading;
  quickButton.classList.toggle("is-loading", isLoading);
  quickButton.setAttribute("aria-busy", String(isLoading));
}

if (quickButton && quickInput && quickStatus) {
  quickButton.addEventListener("click", () => {
    const text = quickInput.value.trim();
    if (!text) {
      quickStatus.textContent = "Add text to sanitise.";
      return;
    }

    quickStatus.textContent = "Sanitising sensitive data…";
    setQuickLoading(true);
    chrome.runtime.sendMessage(
      {
        type: "ANONYMIZE_TEXT",
        payload: { text }
      },
      (response) => {
        if (chrome.runtime.lastError) {
          quickStatus.textContent = "Sanitise unavailable right now.";
          setQuickLoading(false);
          return;
        }

        if (!response || response.ok !== true) {
          quickStatus.textContent = response?.error || "Could not sanitise this text.";
          setQuickLoading(false);
          return;
        }

        quickInput.value = canonicalizeBackendTokens(String(response.anonymizedText || ""));
        const count = Number(response.entityCount || 0);
        quickStatus.textContent = `Done. ${count} ${count === 1 ? "entity" : "entities"} anonymised.`;
        setQuickLoading(false);
      }
    );
  });
}

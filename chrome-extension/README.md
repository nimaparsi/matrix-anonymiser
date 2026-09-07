# SanitiseAI browser extension

Manual prompt sanitisation through the same HTTPS API as the website. Version 1.0.1 uses the website logo, a blue bottom-right action, loading state and an info summary containing category counts only. Automatic mode is off by default and applies only to recognised form submissions. Always review output before sending.

Supported host patterns: ChatGPT, Claude, Gemini, Perplexity (including www). Provider UIs change; verify current signed-in editors before store submission. The popup also works independently of those editors.

From the repository root run `node scripts/package-extension.mjs`. The package is `frontend/public/downloads/sanitiseai-chrome.zip`, also linked by the integrations page until a store URL is configured. Unzip, open chrome://extensions, enable Developer mode, choose Load unpacked and reload the AI page.

See CHROME_WEB_STORE_CHECKLIST.md for exact submission steps and STORE_LISTING_COPY.md for listing text. Set VITE_CHROME_EXTENSION_URL to the published store URL in the website build environment and redeploy after approval.

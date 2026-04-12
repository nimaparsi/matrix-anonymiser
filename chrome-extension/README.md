# Sanitise AI Chrome Extension (v1)

Sanitise AI helps protect private information before prompts are sent to AI tools.

## What it does
- Adds an in-page **Sanitise** action near supported prompt fields.
- Shows compact status feedback (detected/sanitised count) in the composer action area.
- Supports an optional collapsible entity details panel after sanitisation.
- Optional **Automatic mode** sanitises prompt text before send when enabled from popup.
- Calls the same anonymisation backend used by the web app for stronger coverage.
- Supports right-click context menu: **Sanitise with Sanitise AI**.

Privacy positioning in this prototype:
- No prompt data is stored.
- Text is sent only when you click Sanitise or trigger send in Automatic mode, then anonymised before sharing to external AI tools.

## Supported AI sites (current)
- `chat.openai.com`
- `chatgpt.com`
- `claude.ai`
- `gemini.google.com`
- `perplexity.ai`

## Load locally
1. Open Chrome and go to `chrome://extensions`.
2. Enable **Developer mode**.
3. Click **Load unpacked**.
4. Select this folder: `chrome-extension/`.
5. Reload the target AI tab(s) after extension updates.

## Permissions used
- `activeTab`: interact with the active page when needed.
- `contextMenus`: add right-click sanitise action.
- Host permissions for supported AI domains plus the anonymisation API endpoint.

## Notes for Chrome Web Store readiness
- Backend endpoint currently configured in `background.js` as `https://matrix-anonymiser.netlify.app/api/anonymize`.
- Consider moving API base URL to extension settings/env for production builds.
- Keep host list narrow and explicit unless multi-domain support expands.

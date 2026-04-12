# Chrome Web Store Submission Checklist

Use this list before submitting Sanitise AI to the Chrome Web Store.

## 1) Package and version
- Verify extension loads from `chrome://extensions` with no errors.
- Confirm `manifest_version` is `3`.
- Bump `version` in `manifest.json` for each new submission.
- Ensure icons exist and render correctly at 16, 48, and 128.

## 2) Permissions and hosts
- Keep only required permissions:
  - `contextMenus`
  - `storage`
- Keep host permissions scoped to supported sites and API host only.
- Re-check no broad wildcard hosts are present.

## 3) Privacy and policy
- Set Privacy Policy URL to: `https://sanitiseai.com/privacy`.
- In Web Store data disclosures, state:
  - Text is sent to Sanitise AI only when user clicks Sanitise or uses Automatic mode.
  - Prompt text is processed for anonymisation and not stored as content records.
  - Service-health telemetry may be retained in aggregate.
- Ensure this matches the live privacy page exactly.

## 4) Listing assets
- Extension name: `Sanitise AI`.
- Short summary and full description prepared (see `STORE_LISTING_COPY.md`).
- Upload screenshots that show:
  - ChatGPT composer integration.
  - Sanitise action near send controls.
  - Before/after anonymisation example.
  - Popup with privacy messaging and automatic mode toggle.
- Add support contact email and website URL.

## 5) Functional verification
- Manual sanitise works on all supported sites:
  - `chat.openai.com`
  - `chatgpt.com`
  - `claude.ai`
  - `gemini.google.com`
  - `perplexity.ai`
- Automatic mode sanitises before send when enabled.
- Context menu action sanitises selected text.
- Toolbar hides when no text and during submit/send.
- No console errors in background service worker or content script.

## 6) Final review notes
- Describe single purpose clearly: anonymise sensitive text before AI prompts are sent.
- Avoid marketing claims that imply guaranteed legal/compliance outcomes.
- Keep listing copy aligned with actual behavior in code.

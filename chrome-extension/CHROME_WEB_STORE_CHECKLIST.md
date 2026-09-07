# Publish SanitiseAI 1.0.1

## Exact upload steps

1. Run `node scripts/package-extension.mjs` from the repository root. Upload `frontend/public/downloads/sanitiseai-chrome.zip`. This ZIP has manifest.json at its root and includes only runtime files and website-derived icons. Do not upload the older root-level 1.0.0 ZIP.
2. Open https://chrome.google.com/webstore/devconsole and sign in to the Google account that should own the extension. Complete developer registration, any requested registration payment, account/contact verification and account security requirements shown by Google. Do not share credentials or keys in the extension.
3. Before submission, unzip the archive, open chrome://extensions, enable Developer mode, choose Load unpacked and select the extracted folder. Reload each supported AI site. Test manual sanitisation, loading, errors, summary, editing while processing, and keyboard focus. Automatic mode only intercepts supported form submissions; do not advertise universal send interception.
4. In the dashboard choose Add new item, select the ZIP and Upload. If updating an existing listing, open that item and upload the new package there instead. Do not create a duplicate listing. Later uploads must increment manifest.version beyond the last submitted version.
5. Fill Store Listing: name SanitiseAI; summary and description from STORE_LISTING_COPY.md; appropriate category and English language. Website https://sanitiseai.com/ and support https://sanitiseai.com/contact. Use your real publisher/support contact when the dashboard requires it.
6. Supply the 128px icon, a small promotional image (440x280) and at least one genuine screenshot (1280x800 or 640x400), following the current dashboard requirements. Capture the actual extension with synthetic example text in a supported editor. Do not present our local test fixture as a screenshot of ChatGPT. Use the same website logo; no fabricated ratings or certifications.
7. Privacy tab: single purpose is sanitising user-selected prompt text before sharing with AI services. Declare that text leaves the device for https://sanitiseai.com/api/anonymize; it may contain personal information and credentials. No remote executable code is loaded. Data-disclosure categories must describe the content actually handled, not claim no collection merely because processing is transient. Policy URL: https://sanitiseai.com/privacy.
8. Permission justifications: contextMenus adds the selected-text action; storage stores the automatic-mode preference; AI-site host access injects the prompt button; sanitiseai.com host access calls the sanitisation API. There is no all-sites permission, prompt history or extension analytics. The website's own analytics are separate and should be disclosed by the website.
9. Test instructions: no SanitiseAI login required. For reviewers without a signed-in AI account, open the popup, paste `Email: jane@example.com`, click Sanitise and confirm the email is replaced. For the in-page button, use a supported signed-in AI editor, paste the same synthetic text, click Sanitise and inspect the info summary. Explain that AI-provider accounts belong to those providers; do not supply personal account credentials.
10. Distribution: select the intended audience/countries, complete any outstanding dashboard fields and Submit for Review. Choose automatic publication after approval or deferred publication. Uploading is not approval; address reviewer feedback before saying it is published.
11. Once published, copy the exact public listing URL. In Netlify set `VITE_CHROME_EXTENSION_URL` to that URL for the production build and redeploy. The integrations page switches from Download extension to Add to browser. Do not use the developer dashboard URL. Chrome store publication does not automatically publish an Edge Add-ons listing; Edge users may install compatible Chrome extensions or you may submit separately to Microsoft.

## What is ready and what remains

Version 1.0.1 is packaged for manual installation and upload. Automated local checks cover the extension UI using a mock API/editor; they do not establish compatibility with every current signed-in provider UI. Complete step 3 on the actual supported websites and supply genuine store images before submission. Google's review is external and has no guaranteed completion time.

The button is manual by default. Enabling Automatic mode is optional and only affects recognised form submissions. Always review output before sharing; detection can miss sensitive details.

## Official references

- https://developer.chrome.com/docs/webstore/publish
- https://developer.chrome.com/docs/webstore/images
- https://developer.chrome.com/docs/webstore/register

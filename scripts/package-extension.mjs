import { execFileSync } from 'node:child_process';
import { mkdirSync, rmSync } from 'node:fs';
import { fileURLToPath } from 'node:url';
const root = fileURLToPath(new URL('../', import.meta.url));
const destination = `${root}frontend/public/downloads/sanitiseai-chrome.zip`;
mkdirSync(`${root}frontend/public/downloads`, { recursive: true });
rmSync(destination, { force: true });
execFileSync('zip', ['-q', '-X', destination, 'manifest.json', 'background.js', 'content.js', 'popup.html', 'popup.js', 'styles.css', 'icons/icon16.png', 'icons/icon48.png', 'icons/icon128.png'], { cwd: `${root}chrome-extension` });
console.log(destination);

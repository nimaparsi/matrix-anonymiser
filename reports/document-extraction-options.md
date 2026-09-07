# Extraction adapters for SanitiseAI

Extraction produces text for the existing sanitisation API. No library guarantees perfect recognition or reading order for every PDF.

| Option | Best fit | Tradeoff |
| --- | --- | --- |
| PDF.js (installed) | PDFs with text layers | Browser; geometry and line endings. No OCR. This release repairs spacing on this stack. |
| Tesseract.js | Scanned pages/images | Browser OCR; render PDFs to images with PDF.js first. Does not accept PDFs directly. Self-host workers/models; add progress and cancellation. |
| Docling | Complex layouts, tables and mixed/scanned documents | Dedicated Python service with layout/OCR dependencies. Benchmark before deployment; not a drop-in Netlify function. Define retention, memory limits and hosting first. |
| Mammoth.js | Word DOCX contracts | Browser/Node extractRawText. Do not inject generated HTML. Does not fix PDFs. |

Recommendation: PDF.js spacing repair now; evaluate Tesseract.js for explicit OCR and Mammoth for DOCX next. Pilot Docling on complex layouts before adding infrastructure. No third-party extraction service is enabled in this release.

The updated importer preserves fragment order, infers spaces from geometry, respects lines and pages, warns about pages with no text and pauses for review. It does not perform OCR, reconstruct original styling or export redacted PDFs.

Evaluate split names/emails/keys, invoice IDs, letter spacing, columns, tables, scanned and mixed documents, protected PDFs, rotated and non-Latin text. Measure sensitive-string recovery and reading order, not just visual appearance.

Primary sources:
- https://mozilla.github.io/pdf.js/
- https://github.com/naptha/tesseract.js
- https://github.com/docling-project/docling
- https://github.com/mwilliamson/mammoth.js

---
name: sanitise-ai-api
description: "Call the SanitiseAI backend /api/anonymize endpoint for every sanitisation request (no caching). Use when anonymising text or files via the SanitiseAI API, needing consistent tokens, counts, reverse pronouns, or language warnings."
---

# Sanitise Ai Api

## Overview

Route all sanitisation through the SanitiseAI backend API. Always send the full input for each request and return the API response without caching or storing text locally.

## Quick Start

- Endpoint: `POST /api/anonymize`
- Base URL: `SANITISE_API_URL` (default `http://localhost:8000`)
- Optional header: `x-bot-challenge` (value: `SANITISE_BOT_CHALLENGE`)

Example (curl):

```bash
curl -sS "$SANITISE_API_URL/api/anonymize" \
  -H "content-type: application/json" \
  ${SANITISE_BOT_CHALLENGE:+-H "x-bot-challenge: $SANITISE_BOT_CHALLENGE"} \
  -d '{
    "text": "Contact: alice@example.com",
    "entity_types": ["EMAIL", "PERSON", "PHONE", "ADDRESS"],
    "reverse_pronouns": false
  }'
```

## Workflow

1. Gather the raw text (or extracted text from files).
2. Select entity types (defaults match backend supported toggles if omitted).
3. Call `POST /api/anonymize` for every sanitisation request.
4. Return `anonymized_text`, `counts`, `entities`, and `warning` to the caller.
5. Do not cache results or store raw input.

## Request Shape

- `text` (string, required)
- `entity_types` (array of strings, optional)
- `reverse_pronouns` or `reversePronouns` (bool, optional)

Backend defaults to a comprehensive list when `entity_types` is omitted.

## Response Shape

- `anonymized_text` (string)
- `entities` (array)
- `counts` (object)
- `warning` (string or empty)
- `meta` (processing details)

## Script

Use `scripts/sanitise_api.py` for a thin CLI wrapper around the API. It reads from stdin or `--input` and always sends requests directly to the backend (no caching).

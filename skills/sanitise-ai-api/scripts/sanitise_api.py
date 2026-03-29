#!/usr/bin/env python3
import argparse
import json
import os
import sys
import urllib.error
import urllib.request
from typing import Optional


def _read_input(path: Optional[str]) -> str:
    if path:
        with open(path, "r", encoding="utf-8") as handle:
            return handle.read()
    data = sys.stdin.read()
    return data


def _build_payload(text: str, types: Optional[str], reverse_pronouns: bool) -> dict:
    payload = {"text": text, "reverse_pronouns": reverse_pronouns}
    if types:
        payload["entity_types"] = [t.strip() for t in types.split(",") if t.strip()]
    return payload


def _post_json(url: str, payload: dict, bot_challenge: Optional[str]) -> dict:
    body = json.dumps(payload).encode("utf-8")
    headers = {"content-type": "application/json"}
    if bot_challenge:
        headers["x-bot-challenge"] = bot_challenge
    req = urllib.request.Request(url, data=body, headers=headers, method="POST")
    try:
        with urllib.request.urlopen(req, timeout=30) as resp:
            return json.loads(resp.read().decode("utf-8"))
    except urllib.error.HTTPError as exc:
        detail = exc.read().decode("utf-8")
        raise RuntimeError(f"API error {exc.code}: {detail}") from exc


def main() -> int:
    parser = argparse.ArgumentParser(description="Call SanitiseAI /api/anonymize")
    parser.add_argument("--input", help="Path to a text file. Reads stdin if omitted.")
    parser.add_argument("--types", help="Comma-separated entity types (optional)")
    parser.add_argument("--reverse-pronouns", action="store_true", help="Enable pronoun reversal")
    parser.add_argument("--api-url", default=os.getenv("SANITISE_API_URL", "http://localhost:8000"))
    parser.add_argument("--bot-challenge", default=os.getenv("SANITISE_BOT_CHALLENGE"))
    parser.add_argument("--json", action="store_true", help="Print full JSON response")
    args = parser.parse_args()

    text = _read_input(args.input)
    if not text.strip():
        raise SystemExit("No input text provided.")

    payload = _build_payload(text, args.types, args.reverse_pronouns)
    url = args.api_url.rstrip("/") + "/api/anonymize"
    result = _post_json(url, payload, args.bot_challenge)

    if args.json:
        print(json.dumps(result, indent=2))
        return 0

    print(result.get("anonymized_text", ""))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

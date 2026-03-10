from __future__ import annotations

import os
import time
from typing import Dict, List

import stripe
from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException, Request, Response
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field

from anonymizer import SUPPORTED_TOGGLES, OptionalNlp, anonymize_text, get_language_warning
from auth import create_pro_token, is_pro_from_cookie
from usage import UsageLimiter


load_dotenv()

APP_VERSION = "v1"
MAX_INPUT_CHARS = int(os.getenv("MAX_INPUT_CHARS", "50000"))
BOT_CHALLENGE_THRESHOLD = int(os.getenv("BOT_CHALLENGE_THRESHOLD", "20"))
BOT_CHALLENGE_SECRET = os.getenv("BOT_CHALLENGE_SECRET", "")

nlp = OptionalNlp()
limiter = UsageLimiter()

stripe.api_key = os.getenv("STRIPE_SECRET_KEY", "")

app = FastAPI(title="Matrix Anonymiser API", version=APP_VERSION)

origins = [o.strip() for o in os.getenv("FRONTEND_ORIGIN", "http://localhost:5173").split(",") if o.strip()]
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["GET", "POST", "OPTIONS"],
    allow_headers=["*"],
)


class AnonymizeRequest(BaseModel):
    text: str = Field(min_length=1)
    entity_types: List[str] = Field(default_factory=lambda: ["PERSON", "EMAIL", "PHONE", "ADDRESS", "ORG", "DATE", "URL", "API_KEY", "CREDIT_CARD", "GOVERNMENT_ID", "BANK_ACCOUNT", "PRIVATE_KEY", "BOOKING_REFERENCE", "TICKET_REFERENCE", "ORDER_ID", "TRANSACTION_ID", "IP_ADDRESS", "USERNAME", "COORDINATE", "FILE_PATH"])
    reverse_pronouns: bool = False
    reversePronouns: bool | None = None


class BillingRequest(BaseModel):
    success_url: str
    cancel_url: str


def _client_ip(request: Request) -> str:
    forwarded = request.headers.get("x-forwarded-for")
    if forwarded:
        return forwarded.split(",")[0].strip()
    return request.client.host if request.client else "0.0.0.0"


@app.get("/api/health")
def health() -> Dict[str, object]:
    return {
        "ok": True,
        "version": APP_VERSION,
        "nlp_available": nlp.available,
    }


@app.post("/api/anonymize")
def anonymize(payload: AnonymizeRequest, request: Request):
    started = time.perf_counter()

    if len(payload.text) > MAX_INPUT_CHARS:
        raise HTTPException(status_code=413, detail="Input exceeds character limit")

    is_pro = is_pro_from_cookie(request)
    key = limiter.make_usage_key(_client_ip(request), request.headers.get("user-agent", "unknown"), is_pro)
    usage = limiter.check_and_increment(key, is_pro=is_pro)

    if not usage.allowed:
        raise HTTPException(
            status_code=429,
            detail={
                "code": "USAGE_LIMIT_EXCEEDED",
                "message": "Daily limit reached",
                "used": usage.used,
                "limit": usage.limit,
            },
        )

    if usage.used > BOT_CHALLENGE_THRESHOLD and BOT_CHALLENGE_SECRET:
        challenge = request.headers.get("x-bot-challenge", "")
        if challenge != BOT_CHALLENGE_SECRET:
            raise HTTPException(
                status_code=403,
                detail={
                    "code": "BOT_CHALLENGE_REQUIRED",
                    "message": "Bot challenge failed",
                },
            )

    selected = [e for e in payload.entity_types if e in SUPPORTED_TOGGLES]
    if not selected:
        raise HTTPException(status_code=400, detail="No valid entity types selected")

    reverse_pronouns = payload.reversePronouns if payload.reversePronouns is not None else payload.reverse_pronouns
    language = get_language_warning(payload.text)
    result = anonymize_text(payload.text, selected, nlp, reverse_pronouns=reverse_pronouns)
    duration_ms = int((time.perf_counter() - started) * 1000)

    return {
        "anonymized_text": result["anonymized_text"],
        "entities": result["entities"],
        "counts": result["counts"],
        "warning": language["warning"],
        "meta": {
            "processing_ms": duration_ms,
            "version": APP_VERSION,
            "nlp_used": nlp.available,
            "usage_used": usage.used,
            "usage_limit": usage.limit,
            "tier": "pro" if is_pro else "free",
            "supported_language": language["supported_language"],
            "detected_language": language["detected_language"],
            "reverse_pronouns": reverse_pronouns,
            "reversePronouns": reverse_pronouns,
        },
        "cta_visaprep": result["cta_visaprep"],
    }


@app.post("/api/billing/create-checkout")
def create_checkout(payload: BillingRequest):
    price_id = os.getenv("STRIPE_PRICE_ID")
    if not stripe.api_key or not price_id:
        raise HTTPException(status_code=503, detail="Billing not configured")

    session = stripe.checkout.Session.create(
        mode="subscription",
        line_items=[{"price": price_id, "quantity": 1}],
        success_url=payload.success_url + "?session_id={CHECKOUT_SESSION_ID}",
        cancel_url=payload.cancel_url,
        allow_promotion_codes=True,
    )

    return {"url": session.url}


@app.get("/api/billing/activate")
def activate_pro(session_id: str, response: Response):
    if stripe.api_key:
        try:
            session = stripe.checkout.Session.retrieve(session_id)
            if session.payment_status not in {"paid", "no_payment_required"}:
                raise HTTPException(status_code=402, detail="Payment not completed")
        except stripe.error.StripeError as exc:
            raise HTTPException(status_code=400, detail=f"Stripe validation failed: {exc.user_message or 'unknown error'}")

    token = create_pro_token()
    response.set_cookie(
        key="pro_token",
        value=token,
        httponly=True,
        secure=os.getenv("COOKIE_SECURE", "false").lower() == "true",
        samesite="lax",
        max_age=60 * 60 * 24 * int(os.getenv("PRO_TOKEN_DAYS", "30")),
    )
    return {"ok": True, "tier": "pro"}


@app.post("/api/billing/dev-upgrade")
def dev_upgrade(response: Response):
    if os.getenv("ENV", "dev") == "production":
        raise HTTPException(status_code=403, detail="Disabled in production")
    token = create_pro_token()
    response.set_cookie(
        key="pro_token",
        value=token,
        httponly=True,
        secure=False,
        samesite="lax",
        max_age=60 * 60 * 24 * int(os.getenv("PRO_TOKEN_DAYS", "30")),
    )
    return {"ok": True, "tier": "pro"}

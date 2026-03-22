from __future__ import annotations

import os
import smtplib
import ssl
import time
from email.message import EmailMessage
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
    entity_types: List[str] = Field(default_factory=lambda: ["PERSON", "EMAIL", "PHONE", "ADDRESS", "ORG", "DATE", "URL", "API_KEY", "CRYPTO_WALLET", "CREDIT_CARD", "GOVERNMENT_ID", "BANK_ACCOUNT", "PRIVATE_KEY", "COMPANY_REGISTRATION_NUMBER", "INVOICE_NUMBER", "EMPLOYEE_ID", "BOOKING_REFERENCE", "TICKET_REFERENCE", "ORDER_ID", "TRANSACTION_ID", "IP_ADDRESS", "USERNAME", "COORDINATE", "FILE_PATH"])
    reverse_pronouns: bool = False
    reversePronouns: bool | None = None


class BillingRequest(BaseModel):
    success_url: str
    cancel_url: str


class ContactRequest(BaseModel):
    name: str = Field(min_length=1, max_length=120)
    email: str = Field(min_length=3, max_length=200)
    company: str = Field(default="", max_length=200)
    topic: str = Field(min_length=1, max_length=80)
    message: str = Field(min_length=1, max_length=5000)


def _client_ip(request: Request) -> str:
    forwarded = request.headers.get("x-forwarded-for")
    if forwarded:
        return forwarded.split(",")[0].strip()
    return request.client.host if request.client else "0.0.0.0"


def _send_contact_email(payload: ContactRequest, request: Request) -> None:
    smtp_host = os.getenv("SMTP_HOST", "").strip()
    smtp_port = int(os.getenv("SMTP_PORT", "587"))
    smtp_username = os.getenv("SMTP_USERNAME", "").strip()
    smtp_password = os.getenv("SMTP_PASSWORD", "")
    smtp_from = os.getenv("SMTP_FROM_EMAIL", "").strip()
    contact_to = os.getenv("CONTACT_TO_EMAIL", "nimaparsi@icloud.com").strip()
    smtp_use_tls = os.getenv("SMTP_USE_TLS", "true").lower() == "true"
    smtp_use_ssl = os.getenv("SMTP_USE_SSL", "false").lower() == "true"
    smtp_timeout = float(os.getenv("SMTP_TIMEOUT_SECONDS", "15"))

    if not smtp_host or not smtp_from or not contact_to:
        raise HTTPException(status_code=503, detail="Contact service not configured")

    safe_topic = payload.topic.replace("\r", " ").replace("\n", " ").strip()
    safe_name = payload.name.strip()
    safe_email = payload.email.strip()
    safe_company = payload.company.strip()
    safe_message = payload.message.strip()

    msg = EmailMessage()
    msg["Subject"] = f"[SanitiseAI] {safe_topic}"
    msg["From"] = smtp_from
    msg["To"] = contact_to
    msg["Reply-To"] = safe_email
    msg.set_content(
        "\n".join(
            [
                "New contact request from sanitiseai.com",
                "",
                f"Topic: {safe_topic}",
                f"Name: {safe_name}",
                f"Email: {safe_email}",
                f"Company: {safe_company or '-'}",
                "",
                "Message:",
                safe_message,
                "",
                f"Source IP: {_client_ip(request)}",
                f"User-Agent: {request.headers.get('user-agent', 'unknown')}",
            ]
        )
    )

    ssl_context = ssl.create_default_context()

    try:
        if smtp_use_ssl:
            with smtplib.SMTP_SSL(smtp_host, smtp_port, timeout=smtp_timeout, context=ssl_context) as server:
                if smtp_username:
                    server.login(smtp_username, smtp_password)
                server.send_message(msg)
            return

        with smtplib.SMTP(smtp_host, smtp_port, timeout=smtp_timeout) as server:
            server.ehlo()
            if smtp_use_tls:
                server.starttls(context=ssl_context)
                server.ehlo()
            if smtp_username:
                server.login(smtp_username, smtp_password)
            server.send_message(msg)
    except (smtplib.SMTPException, OSError):
        raise HTTPException(status_code=502, detail="Unable to deliver contact message")


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


@app.post("/api/contact")
def contact(payload: ContactRequest, request: Request):
    normalized_email = payload.email.strip()
    if "@" not in normalized_email or "." not in normalized_email.split("@")[-1]:
        raise HTTPException(status_code=400, detail="Please provide a valid email address")

    _send_contact_email(payload, request)
    return {"ok": True, "message": "Contact request sent"}


@app.get("/api/billing/status")
def billing_status(request: Request):
    is_pro = is_pro_from_cookie(request)
    return {"ok": True, "tier": "pro" if is_pro else "free"}


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


@app.post("/api/dev/reset-usage")
def dev_reset_usage(request: Request, response: Response):
    if os.getenv("ENV", "dev") == "production":
        raise HTTPException(status_code=403, detail="Disabled in production")

    user_agent = request.headers.get("user-agent", "unknown")
    ip = _client_ip(request)

    limiter.reset_key(limiter.make_usage_key(ip, user_agent, is_pro=False))
    limiter.reset_key(limiter.make_usage_key(ip, user_agent, is_pro=True))

    response.delete_cookie(key="pro_token", path="/")
    return {"ok": True, "message": "Usage and pro token reset"}

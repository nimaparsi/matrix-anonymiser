from __future__ import annotations

import os
from datetime import datetime, timedelta, timezone
from typing import Optional

import jwt
from fastapi import Request


def create_pro_token() -> str:
    secret = os.getenv("JWT_SECRET", "dev-secret-change-me")
    exp_days = int(os.getenv("PRO_TOKEN_DAYS", "30"))
    payload = {
        "tier": "pro",
        "exp": datetime.now(timezone.utc) + timedelta(days=exp_days),
        "iat": datetime.now(timezone.utc),
    }
    return jwt.encode(payload, secret, algorithm="HS256")


def is_pro_from_cookie(request: Request) -> bool:
    token = request.cookies.get("pro_token")
    if not token:
        return False
    secret = os.getenv("JWT_SECRET", "dev-secret-change-me")
    try:
        payload = jwt.decode(token, secret, algorithms=["HS256"])
        return payload.get("tier") == "pro"
    except jwt.PyJWTError:
        return False



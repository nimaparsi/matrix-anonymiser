from __future__ import annotations

import hashlib
import os
from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Optional

from redis import Redis
from redis.exceptions import RedisError


@dataclass
class UsageResult:
    allowed: bool
    used: int
    limit: int


class UsageLimiter:
    def __init__(self) -> None:
        self.limit_free = int(os.getenv("FREE_DAILY_LIMIT", "100"))
        self.limit_pro = int(os.getenv("PRO_DAILY_LIMIT", "500"))
        self.salt = os.getenv("USAGE_SALT", "change-me")
        self.redis: Optional[Redis] = None
        self.mem = {}

        redis_url = os.getenv("REDIS_URL")
        if redis_url:
            self.redis = Redis.from_url(redis_url, decode_responses=True)

    def make_usage_key(self, ip: str, user_agent: str, is_pro: bool) -> str:
        day = datetime.now(timezone.utc).strftime("%Y%m%d")
        raw = f"{ip}|{user_agent}|{day}|{self.salt}"
        digest = hashlib.sha256(raw.encode("utf-8")).hexdigest()
        tier = "pro" if is_pro else "free"
        return f"usage:{tier}:{digest}"

    def check_and_increment(self, key: str, is_pro: bool) -> UsageResult:
        limit = self.limit_pro if is_pro else self.limit_free
        ttl = 60 * 60 * 48

        if self.redis:
            try:
                val = self.redis.incr(key)
                if val == 1:
                    self.redis.expire(key, ttl)
                return UsageResult(allowed=val <= limit, used=int(val), limit=limit)
            except RedisError:
                pass

        current = self.mem.get(key, 0) + 1
        self.mem[key] = current
        return UsageResult(allowed=current <= limit, used=current, limit=limit)

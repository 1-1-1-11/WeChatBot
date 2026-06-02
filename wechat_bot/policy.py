from __future__ import annotations

import datetime as dt
import random
from dataclasses import dataclass
from enum import Enum
from typing import Protocol, Sequence


class RiskLevel(str, Enum):
    LOW = "low"
    MEDIUM = "medium"


@dataclass(frozen=True)
class MessageCandidate:
    contact: str
    text: str
    received_at: dt.datetime
    is_personal: bool = True


@dataclass(frozen=True)
class ReplyDecision:
    allow_send: bool
    risk_level: RiskLevel
    reason: str
    reply_text: str | None = None
    delay_seconds: int | None = None


@dataclass(frozen=True)
class SendGuardResult:
    cancel: bool
    reason: str


class RandomLike(Protocol):
    def randint(self, minimum: int, maximum: int) -> int:
        ...

    def choice(self, values: Sequence[str]) -> str:
        ...


DEFAULT_TEMPLATES = (
    "收到，我稍后看完回复你。",
    "好的，我晚点回复你。",
    "我现在不太方便，稍后回你。",
)

MEDIUM_RISK_KEYWORDS = (
    "多少钱",
    "报价",
    "价格",
    "付款",
    "转账",
    "发票",
    "合同",
    "承诺",
    "保证",
    "投诉",
    "不满意",
    "退款",
    "密码",
    "验证码",
    "账号",
    "身份证",
    "隐私",
)


class ReplyPolicy:
    def __init__(
        self,
        templates: Sequence[str] = DEFAULT_TEMPLATES,
        delay_range_seconds: tuple[int, int] = (20, 60),
        contact_cooldown_seconds: int = 600,
        rng: RandomLike | None = None,
    ) -> None:
        self.templates = tuple(templates)
        self.delay_range_seconds = delay_range_seconds
        self.contact_cooldown_seconds = contact_cooldown_seconds
        self.rng = rng or random

    def evaluate(
        self,
        message: MessageCandidate,
        *,
        user_offline: bool,
        paused: bool,
        now: dt.datetime,
        last_auto_reply_at: dt.datetime | None = None,
    ) -> ReplyDecision:
        risk_level = self.classify_risk(message.text)
        if not message.is_personal:
            return ReplyDecision(False, risk_level, "not_personal")
        if paused:
            return ReplyDecision(False, risk_level, "paused")
        if not user_offline:
            return ReplyDecision(False, risk_level, "user_online")
        if risk_level != RiskLevel.LOW:
            return ReplyDecision(False, risk_level, "risk_excluded")
        if last_auto_reply_at is not None:
            elapsed = (now - last_auto_reply_at).total_seconds()
            if elapsed < self.contact_cooldown_seconds:
                return ReplyDecision(False, risk_level, "cooldown")

        minimum, maximum = self.delay_range_seconds
        return ReplyDecision(
            True,
            risk_level,
            "allowed",
            reply_text=self.rng.choice(self.templates),
            delay_seconds=self.rng.randint(minimum, maximum),
        )

    def classify_risk(self, text: str) -> RiskLevel:
        normalized = text.strip().lower()
        if any(keyword.lower() in normalized for keyword in MEDIUM_RISK_KEYWORDS):
            return RiskLevel.MEDIUM
        return RiskLevel.LOW


class SendGuard:
    def check_before_send(
        self,
        *,
        user_offline: bool,
        paused: bool,
        cooldown_ok: bool,
        human_replied_after_received: bool,
    ) -> SendGuardResult:
        if not user_offline:
            return SendGuardResult(True, "user_returned")
        if paused:
            return SendGuardResult(True, "paused")
        if not cooldown_ok:
            return SendGuardResult(True, "cooldown")
        if human_replied_after_received:
            return SendGuardResult(True, "human_replied")
        return SendGuardResult(False, "allowed")


from __future__ import annotations

import datetime as dt
import random
import re
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
    # 金融相关
    "多少钱",
    "报价",
    "价格",
    "付款",
    "转账",
    "发票",
    "合同",
    "微信支付",
    "支付宝",
    "银行卡",
    "红包",
    "借钱",
    "贷款",
    "欠款",
    "汇款",
    # 承诺保证
    "承诺",
    "保证",
    "确认",
    "批准",
    # 投诉风险
    "投诉",
    "不满意",
    "退款",
    "赔偿",
    "法律",
    "起诉",
    "维权",
    # 敏感信息
    "密码",
    "验证码",
    "账号",
    "身份证",
    "隐私",
    "手机号",
    "地址",
    # 敏感操作
    "删除",
    "修改",
    "授权",
    "权限",
    "登录",
    "注销",
    "取消",
    # 紧急情况
    "紧急",
    "立即",
    "马上",
    "加急",
    "投诉升级",
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
        # 移除所有非字母数字字符，防止"多 少 钱"、"多-少-钱"等绕过
        normalized = re.sub(r'[^\w]', '', text.strip().lower())
        for keyword in MEDIUM_RISK_KEYWORDS:
            keyword_normalized = re.sub(r'[^\w]', '', keyword.lower())
            if keyword_normalized in normalized:
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


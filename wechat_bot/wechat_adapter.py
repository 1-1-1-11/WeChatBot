from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class SendResult:
    sent: bool
    mode: str
    detail: str = ""


class DryRunWechatAdapter:
    def __init__(self) -> None:
        self.sent_messages: list[dict] = []

    def send_text(self, *, contact: str, text: str) -> SendResult:
        self.sent_messages.append({"contact": contact, "text": text})
        return SendResult(sent=True, mode="dry_run")


class PyWeixinAdapter:
    def send_text(self, *, contact: str, text: str) -> SendResult:
        from pyweixin import Messages

        Messages.send_messages_to_friend(friend=contact, messages=[text])
        return SendResult(sent=True, mode="pyweixin")

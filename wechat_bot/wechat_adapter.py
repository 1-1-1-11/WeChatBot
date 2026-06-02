from __future__ import annotations

import datetime as dt
from dataclasses import dataclass


@dataclass(frozen=True)
class SendResult:
    sent: bool
    mode: str
    detail: str = ""


@dataclass(frozen=True)
class IncomingMessage:
    contact: str
    text: str
    received_at: dt.datetime
    is_personal: bool = True

    @property
    def fingerprint(self) -> tuple[str, str, str]:
        return (self.contact, self.text, self.received_at.isoformat())


class DryRunWechatAdapter:
    def __init__(self, incoming_messages: list[IncomingMessage] | None = None) -> None:
        self.sent_messages: list[dict] = []
        self._incoming_messages = list(incoming_messages or [])

    def set_incoming_messages(self, messages: list[IncomingMessage]) -> None:
        self._incoming_messages = list(messages)

    def read_new_personal_messages(self) -> list[IncomingMessage]:
        return [message for message in self._incoming_messages if message.is_personal]

    def send_text(self, *, contact: str, text: str) -> SendResult:
        self.sent_messages.append({"contact": contact, "text": text})
        return SendResult(sent=True, mode="dry_run")


class PyWeixinAdapter:
    def read_new_personal_messages(self) -> list[IncomingMessage]:
        # The concrete unread-message extraction depends on 微信 UI state.
        # The runtime keeps this adapter isolated so live testing can refine it
        # without touching policy, storage, or dashboard code.
        return []

    def send_text(self, *, contact: str, text: str) -> SendResult:
        from pyweixin import Messages

        Messages.send_messages_to_friend(friend=contact, messages=[text])
        return SendResult(sent=True, mode="pyweixin")

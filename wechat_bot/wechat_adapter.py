from __future__ import annotations

import datetime as dt
from dataclasses import dataclass


class WeixinAdapterError(RuntimeError):
    pass


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


def normalize_pyweixin_messages(raw_result: dict, *, received_at: dt.datetime) -> list[IncomingMessage]:
    messages: list[IncomingMessage] = []
    for contact, raw_messages in raw_result.items():
        if not _is_probably_personal_contact(contact):
            continue
        for raw_message in raw_messages or []:
            message_type = str(raw_message.get("消息类型", "文本"))
            if "文本" not in message_type:
                continue
            text = str(raw_message.get("消息内容", "")).strip()
            if not text:
                continue
            sender = str(raw_message.get("消息发送人", ""))
            if sender and sender != contact:
                continue
            messages.append(IncomingMessage(contact=contact, text=text, received_at=received_at, is_personal=True))
    return messages


def _is_probably_personal_contact(contact: str) -> bool:
    group_markers = ("群", "群聊", "@chatroom", "微信群")
    return not any(marker in contact for marker in group_markers)


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
    def __init__(self, messages_api=None) -> None:
        self._messages_api = messages_api

    def read_new_personal_messages(self) -> list[IncomingMessage]:
        try:
            if self._messages_api is None:
                from pyweixin import Messages

                messages_api = Messages
            else:
                messages_api = self._messages_api

            raw_result = messages_api.check_new_messages(close_weixin=False)
            return normalize_pyweixin_messages(raw_result, received_at=dt.datetime.now())
        except Exception as exc:
            raise WeixinAdapterError(
                "微信 UI Automation 不可用。请确认 PC 微信/Weixin.exe 已登录，必要时按上游 Weixin4.0.md 做 UI 可见性设置。"
            ) from exc

    def send_text(self, *, contact: str, text: str) -> SendResult:
        try:
            from pyweixin import Messages

            Messages.send_messages_to_friend(friend=contact, messages=[text])
            return SendResult(sent=True, mode="pyweixin")
        except Exception as exc:
            raise WeixinAdapterError("微信发送失败，请确认 PC 微信窗口可用且联系人存在。") from exc

from __future__ import annotations

import datetime as dt
import threading
import time
from collections import deque
from typing import Callable

from wechat_bot.db import BotDatabase
from wechat_bot.policy import MessageCandidate, ReplyPolicy, SendGuard
from wechat_bot.wechat_adapter import IncomingMessage, WeixinAdapterError


class BotRuntime:
    def __init__(
        self,
        *,
        db: BotDatabase,
        adapter,
        presence,
        policy: ReplyPolicy,
        now_provider: Callable[[], dt.datetime] = dt.datetime.now,
        sleep: Callable[[float], None] = time.sleep,
        paused_provider: Callable[[], bool] = lambda: False,
    ) -> None:
        self.db = db
        self.adapter = adapter
        self.presence = presence
        self.policy = policy
        self.now_provider = now_provider
        self.sleep = sleep
        self.paused_provider = paused_provider
        self.send_guard = SendGuard()

        # 线程安全的消息去重（有界队列，防止内存泄露）
        self._baseline: set[tuple[str, str, str]] = set()
        self._seen_deque: deque[tuple[str, str, str]] = deque(maxlen=10000)
        self._seen_set: set[tuple[str, str, str]] = set()
        self._seen_lock = threading.RLock()

        # 线程安全的冷却时间管理
        self._last_auto_reply_by_contact: dict[str, dt.datetime] = {}
        self._cooldown_lock = threading.RLock()

        self.last_error: str | None = None

    def establish_baseline(self) -> None:
        try:
            messages = self.adapter.read_new_personal_messages()
            with self._seen_lock:
                self._baseline = {message.fingerprint for message in messages}
            self.last_error = None
        except WeixinAdapterError as exc:
            self.last_error = str(exc)
            with self._seen_lock:
                self._baseline = set()

    def process_once(self) -> None:
        try:
            messages = self.adapter.read_new_personal_messages()
            self.last_error = None
        except WeixinAdapterError as exc:
            self.last_error = str(exc)
            return

        for message in messages:
            fingerprint = message.fingerprint
            with self._seen_lock:
                if fingerprint in self._baseline or fingerprint in self._seen_set:
                    continue
                self._seen_deque.append(fingerprint)
                self._seen_set.add(fingerprint)
                # 清理旧指纹（当队列满时）
                if len(self._seen_deque) == self._seen_deque.maxlen:
                    oldest = self._seen_deque[0]
                    self._seen_set.discard(oldest)

            self._handle_message(message)

    def _handle_message(self, message: IncomingMessage) -> None:
        now = self.now_provider()
        self.db.record_message(
            contact=message.contact,
            text=message.text,
            received_at=message.received_at,
            direction="incoming",
        )
        state = self.presence.current_state()
        paused = self.paused_provider()

        with self._cooldown_lock:
            last_auto_reply_at = self._last_auto_reply_by_contact.get(message.contact)

        decision = self.policy.evaluate(
            MessageCandidate(
                contact=message.contact,
                text=message.text,
                received_at=message.received_at,
                is_personal=message.is_personal,
            ),
            user_offline=state.is_offline,
            paused=paused,
            now=now,
            last_auto_reply_at=last_auto_reply_at,
        )
        if not decision.allow_send:
            if decision.reason not in {"user_online", "paused", "cooldown", "not_personal"}:
                self.db.record_pending_item(
                    contact=message.contact,
                    text=message.text,
                    reason=decision.reason,
                    created_at=now,
                )
            return

        self.sleep(decision.delay_seconds or 0)
        after_delay = self.presence.current_state()
        cooldown_ok = self._cooldown_ok(message.contact, self.now_provider())
        guard = self.send_guard.check_before_send(
            user_offline=after_delay.is_offline,
            paused=self.paused_provider(),
            cooldown_ok=cooldown_ok,
            human_replied_after_received=False,
        )
        if guard.cancel:
            return

        try:
            assert decision.reply_text is not None
            self.adapter.send_text(contact=message.contact, text=decision.reply_text)
            sent_at = self.now_provider()

            with self._cooldown_lock:
                self._last_auto_reply_by_contact[message.contact] = sent_at

            self.db.record_auto_reply(contact=message.contact, text=decision.reply_text, sent_at=sent_at)
        except WeixinAdapterError as exc:
            self.last_error = f"发送失败: {exc}"

    def _cooldown_ok(self, contact: str, now: dt.datetime) -> bool:
        with self._cooldown_lock:
            last_sent = self._last_auto_reply_by_contact.get(contact)
        if last_sent is None:
            return True
        return (now - last_sent).total_seconds() >= self.policy.contact_cooldown_seconds

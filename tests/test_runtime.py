import datetime as dt
import tempfile
import unittest
from pathlib import Path

from wechat_bot.db import BotDatabase
from wechat_bot.policy import ReplyPolicy
from wechat_bot.presence import PresenceMode, PresenceState
from wechat_bot.runtime import BotRuntime
from wechat_bot.wechat_adapter import DryRunWechatAdapter, IncomingMessage


class StaticPresence:
    def __init__(self, states):
        self._states = list(states)
        self._index = 0

    def current_state(self):
        state = self._states[min(self._index, len(self._states) - 1)]
        self._index += 1
        return state


class FixedRandom:
    def randint(self, minimum, maximum):
        return minimum

    def choice(self, values):
        return values[0]


class RuntimeTests(unittest.TestCase):
    def setUp(self):
        self.now = dt.datetime(2026, 6, 2, 12, 0, 0)

    def test_startup_baseline_ignores_existing_messages(self):
        with tempfile.TemporaryDirectory() as tmp:
            db = self._db(tmp)
            old_message = IncomingMessage(contact="张三", text="旧消息", received_at=self.now)
            new_message = IncomingMessage(contact="张三", text="新消息", received_at=self.now)
            adapter = DryRunWechatAdapter(incoming_messages=[old_message])
            runtime = self._runtime(db, adapter, offline=True)

            runtime.establish_baseline()
            adapter.set_incoming_messages([old_message, new_message])
            runtime.process_once()

            messages = db.messages_for_day(self.now.date())
            self.assertEqual([message["text"] for message in messages], ["新消息"])

    def test_online_user_records_message_without_sending(self):
        with tempfile.TemporaryDirectory() as tmp:
            db = self._db(tmp)
            adapter = DryRunWechatAdapter(
                incoming_messages=[IncomingMessage(contact="张三", text="在吗", received_at=self.now)]
            )
            runtime = self._runtime(db, adapter, offline=False)

            runtime.process_once()

            self.assertEqual(len(db.messages_for_day(self.now.date())), 1)
            self.assertEqual(adapter.sent_messages, [])

    def test_offline_low_risk_message_sends_template_and_logs_it(self):
        with tempfile.TemporaryDirectory() as tmp:
            db = self._db(tmp)
            adapter = DryRunWechatAdapter(
                incoming_messages=[IncomingMessage(contact="张三", text="在吗", received_at=self.now)]
            )
            runtime = self._runtime(db, adapter, offline=True)

            runtime.process_once()

            self.assertEqual(adapter.sent_messages[0]["text"], "收到，我稍后看完回复你。")
            logs = db.auto_replies_for_day(self.now.date())
            self.assertEqual(logs[0]["contact"], "张三")

    def test_medium_risk_message_becomes_pending_item_without_send(self):
        with tempfile.TemporaryDirectory() as tmp:
            db = self._db(tmp)
            adapter = DryRunWechatAdapter(
                incoming_messages=[IncomingMessage(contact="张三", text="报价多少钱？", received_at=self.now)]
            )
            runtime = self._runtime(db, adapter, offline=True)

            runtime.process_once()

            self.assertEqual(adapter.sent_messages, [])
            pending = db.pending_items_for_day(self.now.date())
            self.assertEqual(pending[0]["contact"], "张三")
            self.assertEqual(pending[0]["reason"], "risk_excluded")

    def test_pending_send_is_cancelled_when_user_returns_after_delay(self):
        with tempfile.TemporaryDirectory() as tmp:
            db = self._db(tmp)
            adapter = DryRunWechatAdapter(
                incoming_messages=[IncomingMessage(contact="张三", text="在吗", received_at=self.now)]
            )
            presence = StaticPresence(
                [
                    PresenceState(PresenceMode.AUTO, idle_seconds=601, is_offline=True),
                    PresenceState(PresenceMode.AUTO, idle_seconds=0, is_offline=False),
                ]
            )
            runtime = self._runtime(db, adapter, presence=presence)

            runtime.process_once()

            self.assertEqual(adapter.sent_messages, [])
            self.assertEqual(db.auto_replies_for_day(self.now.date()), [])

    def _db(self, tmp):
        db = BotDatabase(Path(tmp) / "bot.sqlite3")
        db.initialize()
        return db

    def _runtime(self, db, adapter, offline=None, presence=None):
        if presence is None:
            presence = StaticPresence(
                [PresenceState(PresenceMode.AUTO, idle_seconds=601 if offline else 0, is_offline=bool(offline))]
            )
        return BotRuntime(
            db=db,
            adapter=adapter,
            presence=presence,
            policy=ReplyPolicy(delay_range_seconds=(0, 0), rng=FixedRandom()),
            now_provider=lambda: self.now,
            sleep=lambda seconds: None,
        )


if __name__ == "__main__":
    unittest.main()

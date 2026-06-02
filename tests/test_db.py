import datetime as dt
import tempfile
import unittest
from pathlib import Path

from wechat_bot.db import BotDatabase


class BotDatabaseTests(unittest.TestCase):
    def test_records_messages_and_returns_same_day_context(self):
        with tempfile.TemporaryDirectory() as tmp:
            db = BotDatabase(Path(tmp) / "bot.sqlite3")
            db.initialize()
            received_at = dt.datetime(2026, 6, 2, 9, 30, 0)

            db.record_message(contact="张三", text="在吗", received_at=received_at, direction="incoming")
            messages = db.messages_for_day(dt.date(2026, 6, 2))

            self.assertEqual(len(messages), 1)
            self.assertEqual(messages[0]["contact"], "张三")
            self.assertEqual(messages[0]["text"], "在吗")

    def test_purges_records_older_than_retention_days(self):
        with tempfile.TemporaryDirectory() as tmp:
            db = BotDatabase(Path(tmp) / "bot.sqlite3")
            db.initialize()
            db.record_message(
                contact="旧联系人",
                text="旧消息",
                received_at=dt.datetime(2026, 5, 20, 12, 0, 0),
                direction="incoming",
            )
            db.record_message(
                contact="新联系人",
                text="新消息",
                received_at=dt.datetime(2026, 6, 2, 12, 0, 0),
                direction="incoming",
            )

            deleted = db.purge_older_than(now=dt.datetime(2026, 6, 2, 12, 0, 0), days=7)

            self.assertEqual(deleted, 1)
            remaining = db.messages_for_day(dt.date(2026, 6, 2))
            self.assertEqual([message["contact"] for message in remaining], ["新联系人"])

    def test_records_auto_reply_log(self):
        with tempfile.TemporaryDirectory() as tmp:
            db = BotDatabase(Path(tmp) / "bot.sqlite3")
            db.initialize()
            sent_at = dt.datetime(2026, 6, 2, 12, 1, 0)

            db.record_auto_reply(contact="张三", text="收到，我稍后看完回复你。", sent_at=sent_at)
            logs = db.auto_replies_for_day(dt.date(2026, 6, 2))

            self.assertEqual(len(logs), 1)
            self.assertEqual(logs[0]["contact"], "张三")
            self.assertEqual(logs[0]["text"], "收到，我稍后看完回复你。")

    def test_records_daily_summary_once_per_date(self):
        with tempfile.TemporaryDirectory() as tmp:
            db = BotDatabase(Path(tmp) / "bot.sqlite3")
            db.initialize()

            db.record_daily_summary(
                summary_date=dt.date(2026, 6, 2),
                content="重点：有新消息\n待办：回复张三\n风险：无",
                created_at=dt.datetime(2026, 6, 2, 22, 0, 0),
            )
            db.record_daily_summary(
                summary_date=dt.date(2026, 6, 2),
                content="重点：已更新",
                created_at=dt.datetime(2026, 6, 2, 22, 5, 0),
            )

            summary = db.daily_summary_for_date(dt.date(2026, 6, 2))

            self.assertEqual(summary["content"], "重点：已更新")


if __name__ == "__main__":
    unittest.main()

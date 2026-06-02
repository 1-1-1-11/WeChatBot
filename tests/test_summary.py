import datetime as dt
import tempfile
import unittest
from pathlib import Path

from wechat_bot.db import BotDatabase
from wechat_bot.summary import DailySummaryService


class FakeModelClient:
    def __init__(self):
        self.calls = []

    def create_chat_completion(self, messages, *, temperature=0.2):
        self.calls.append((messages, temperature))
        return "重点：张三问候\n待办：稍后回复\n风险：无"


class DailySummaryServiceTests(unittest.TestCase):
    def test_does_not_generate_before_22_00(self):
        with tempfile.TemporaryDirectory() as tmp:
            db = self._db(tmp)
            client = FakeModelClient()
            service = DailySummaryService(db=db, model_client=client)

            generated = service.maybe_generate(now=dt.datetime(2026, 6, 2, 21, 59, 0))

            self.assertFalse(generated)
            self.assertEqual(client.calls, [])

    def test_generates_and_stores_summary_at_22_00_once(self):
        with tempfile.TemporaryDirectory() as tmp:
            db = self._db(tmp)
            db.record_message(
                contact="张三",
                text="在吗",
                received_at=dt.datetime(2026, 6, 2, 12, 0, 0),
                direction="incoming",
            )
            client = FakeModelClient()
            service = DailySummaryService(db=db, model_client=client)

            first = service.maybe_generate(now=dt.datetime(2026, 6, 2, 22, 0, 0))
            second = service.maybe_generate(now=dt.datetime(2026, 6, 2, 22, 1, 0))
            summary = db.daily_summary_for_date(dt.date(2026, 6, 2))

            self.assertTrue(first)
            self.assertFalse(second)
            self.assertEqual(len(client.calls), 1)
            self.assertEqual(summary["content"], "重点：张三问候\n待办：稍后回复\n风险：无")

    def _db(self, tmp):
        db = BotDatabase(Path(tmp) / "bot.sqlite3")
        db.initialize()
        return db


if __name__ == "__main__":
    unittest.main()

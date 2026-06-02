import tempfile
import unittest
from io import StringIO
from pathlib import Path

from wechat_bot.app import build_runtime, run_live_check
from wechat_bot.config import AppConfig
from wechat_bot.runtime import BotRuntime
from wechat_bot.wechat_adapter import IncomingMessage, WeixinAdapterError


class AppTests(unittest.TestCase):
    def test_build_runtime_creates_database_and_runtime(self):
        with tempfile.TemporaryDirectory() as tmp:
            config = AppConfig(
                openai_base_url="https://api.example.test",
                openai_api_key="secret",
                model_name="test-model",
                data_dir=Path(tmp),
                dry_run=True,
            )

            runtime, db = build_runtime(config)

            self.assertIsInstance(runtime, BotRuntime)
            self.assertTrue((Path(tmp) / "wechat_bot.sqlite3").exists())
            self.assertEqual(db.messages_for_day.__name__, "messages_for_day")

    def test_live_check_reads_messages_without_sending(self):
        class FakeAdapter:
            def __init__(self):
                self.sent = False

            def read_new_personal_messages(self):
                return [
                    IncomingMessage(
                        contact="张三",
                        text="在吗",
                        received_at=__import__("datetime").datetime(2026, 6, 2, 12, 0, 0),
                    )
                ]

            def send_text(self, *, contact, text):
                self.sent = True

        adapter = FakeAdapter()
        output = StringIO()

        count = run_live_check(adapter=adapter, output=output)

        self.assertEqual(count, 1)
        self.assertFalse(adapter.sent)
        self.assertIn("张三", output.getvalue())
        self.assertIn("1", output.getvalue())

    def test_live_check_reports_adapter_error_without_traceback(self):
        class FailingAdapter:
            def read_new_personal_messages(self):
                raise WeixinAdapterError("微信 UI Automation 不可用")

        output = StringIO()

        count = run_live_check(adapter=FailingAdapter(), output=output)

        self.assertEqual(count, -1)
        self.assertIn("live-check failed", output.getvalue())
        self.assertIn("微信 UI Automation 不可用", output.getvalue())


if __name__ == "__main__":
    unittest.main()

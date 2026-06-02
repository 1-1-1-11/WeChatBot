import tempfile
import unittest
from pathlib import Path

from wechat_bot.app import build_runtime
from wechat_bot.config import AppConfig
from wechat_bot.runtime import BotRuntime


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


if __name__ == "__main__":
    unittest.main()

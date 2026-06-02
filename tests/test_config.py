import tempfile
import unittest
from pathlib import Path

from wechat_bot.config import AppConfig


class AppConfigTests(unittest.TestCase):
    def test_loads_env_file_with_defaults(self):
        with tempfile.TemporaryDirectory() as tmp:
            env_path = Path(tmp) / ".env"
            env_path.write_text(
                "\n".join(
                    [
                        "OPENAI_BASE_URL=https://api.example.test",
                        "OPENAI_API_KEY=secret",
                        "MODEL_NAME=test-model",
                    ]
                ),
                encoding="utf-8",
            )

            config = AppConfig.from_env_file(env_path)

            self.assertEqual(config.openai_base_url, "https://api.example.test")
            self.assertEqual(config.model_name, "test-model")
            self.assertEqual(config.idle_minutes, 10)
            self.assertEqual(config.auto_reply_delay_min_seconds, 20)
            self.assertEqual(config.auto_reply_delay_max_seconds, 60)
            self.assertEqual(config.contact_cooldown_minutes, 10)


if __name__ == "__main__":
    unittest.main()

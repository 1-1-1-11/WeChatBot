import datetime as dt
import unittest

from wechat_bot.model_client import build_daily_summary_messages


class ModelClientTests(unittest.TestCase):
    def test_daily_summary_prompt_contains_same_day_text_context_without_images(self):
        messages = [
            {
                "contact": "张三",
                "text": "明天可以聊一下吗？",
                "direction": "incoming",
                "received_at": dt.datetime(2026, 6, 2, 9, 0, 0).isoformat(),
            },
            {
                "contact": "李四",
                "text": "报价多少钱？",
                "direction": "incoming",
                "received_at": dt.datetime(2026, 6, 2, 10, 0, 0).isoformat(),
            },
        ]

        prompt_messages = build_daily_summary_messages(messages, summary_date=dt.date(2026, 6, 2))
        joined = "\n".join(message["content"] for message in prompt_messages)

        self.assertIn("张三", joined)
        self.assertIn("明天可以聊一下吗？", joined)
        self.assertIn("李四", joined)
        self.assertIn("报价多少钱？", joined)
        self.assertIn("重点", joined)
        self.assertIn("待办", joined)
        self.assertIn("风险", joined)
        self.assertNotIn("screenshot", joined.lower())
        self.assertNotIn("image", joined.lower())


if __name__ == "__main__":
    unittest.main()

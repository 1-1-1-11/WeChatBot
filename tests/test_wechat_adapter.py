import unittest

from wechat_bot.wechat_adapter import DryRunWechatAdapter


class DryRunWechatAdapterTests(unittest.TestCase):
    def test_send_text_records_intended_send_without_weixin_side_effects(self):
        adapter = DryRunWechatAdapter()

        result = adapter.send_text(contact="张三", text="收到，我稍后看完回复你。")

        self.assertTrue(result.sent)
        self.assertEqual(result.mode, "dry_run")
        self.assertEqual(adapter.sent_messages[0]["contact"], "张三")
        self.assertEqual(adapter.sent_messages[0]["text"], "收到，我稍后看完回复你。")


if __name__ == "__main__":
    unittest.main()

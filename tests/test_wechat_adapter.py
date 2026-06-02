import datetime as dt
import unittest

from wechat_bot.wechat_adapter import (
    DryRunWechatAdapter,
    PyWeixinAdapter,
    WeixinAdapterError,
    normalize_pyweixin_messages,
)


class FailingMessagesApi:
    @staticmethod
    def check_new_messages(close_weixin=False):
        raise RuntimeError("not logged in")


class DryRunWechatAdapterTests(unittest.TestCase):
    def test_send_text_records_intended_send_without_weixin_side_effects(self):
        adapter = DryRunWechatAdapter()

        result = adapter.send_text(contact="张三", text="收到，我稍后看完回复你。")

        self.assertTrue(result.sent)
        self.assertEqual(result.mode, "dry_run")
        self.assertEqual(adapter.sent_messages[0]["contact"], "张三")
        self.assertEqual(adapter.sent_messages[0]["text"], "收到，我稍后看完回复你。")

    def test_normalizes_only_personal_text_messages_from_pyweixin_result(self):
        now = dt.datetime(2026, 6, 2, 12, 0, 0)
        raw = {
            "张三": [
                {"消息发送人": "张三", "消息内容": "在吗", "消息类型": "文本"},
                {"消息发送人": "张三", "消息内容": "[图片]", "消息类型": "图片"},
            ],
            "项目群": [
                {"消息发送人": "李四", "消息内容": "群消息", "消息类型": "文本"},
            ],
        }

        messages = normalize_pyweixin_messages(raw, received_at=now)

        self.assertEqual(len(messages), 1)
        self.assertEqual(messages[0].contact, "张三")
        self.assertEqual(messages[0].text, "在吗")
        self.assertTrue(messages[0].is_personal)

    def test_pyweixin_adapter_wraps_ui_errors_with_setup_message(self):
        adapter = PyWeixinAdapter(messages_api=FailingMessagesApi)

        with self.assertRaises(WeixinAdapterError) as error:
            adapter.read_new_personal_messages()

        self.assertIn("微信 UI Automation 不可用", str(error.exception))


if __name__ == "__main__":
    unittest.main()

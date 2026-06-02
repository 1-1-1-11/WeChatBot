import unittest

from wechat_bot.dashboard import format_presence_status
from wechat_bot.presence import PresenceMode, PresenceState


class DashboardTests(unittest.TestCase):
    def test_formats_auto_offline_status_in_weixin_terms(self):
        status = format_presence_status(
            PresenceState(PresenceMode.AUTO, idle_seconds=601, is_offline=True)
        )

        self.assertIn("微信值班", status)
        self.assertIn("离线", status)
        self.assertIn("601", status)
        self.assertNotIn("foreign", status.lower())


if __name__ == "__main__":
    unittest.main()

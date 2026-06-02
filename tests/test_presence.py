import unittest

from wechat_bot.presence import PresenceController, PresenceMode


class PresenceControllerTests(unittest.TestCase):
    def test_auto_mode_marks_user_offline_after_idle_threshold(self):
        controller = PresenceController(
            idle_seconds_provider=lambda: 601,
            idle_threshold_seconds=600,
        )

        state = controller.current_state()

        self.assertTrue(state.is_offline)
        self.assertEqual(state.mode, PresenceMode.AUTO)
        self.assertEqual(state.idle_seconds, 601)

    def test_forced_online_never_allows_auto_reply(self):
        controller = PresenceController(
            idle_seconds_provider=lambda: 3600,
            idle_threshold_seconds=600,
            mode=PresenceMode.FORCED_ONLINE,
        )

        self.assertFalse(controller.current_state().is_offline)

    def test_forced_offline_allows_auto_reply_even_without_idle(self):
        controller = PresenceController(
            idle_seconds_provider=lambda: 0,
            idle_threshold_seconds=600,
            mode=PresenceMode.FORCED_OFFLINE,
        )

        self.assertTrue(controller.current_state().is_offline)


if __name__ == "__main__":
    unittest.main()

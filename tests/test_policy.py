import datetime as dt
import unittest

from wechat_bot.policy import (
    MessageCandidate,
    ReplyPolicy,
    RiskLevel,
    SendGuard,
)


class FixedRandom:
    def randint(self, minimum, maximum):
        self.last_bounds = (minimum, maximum)
        return maximum

    def choice(self, values):
        self.last_choices = list(values)
        return values[0]


class ReplyPolicyTests(unittest.TestCase):
    def setUp(self):
        self.now = dt.datetime(2026, 6, 2, 12, 0, 0)

    def test_online_user_never_auto_replies(self):
        policy = ReplyPolicy()
        message = MessageCandidate(contact="张三", text="在吗", received_at=self.now)

        decision = policy.evaluate(message, user_offline=False, paused=False, now=self.now)

        self.assertFalse(decision.allow_send)
        self.assertEqual(decision.risk_level, RiskLevel.LOW)
        self.assertEqual(decision.reason, "user_online")

    def test_medium_risk_money_message_is_blocked(self):
        policy = ReplyPolicy()
        message = MessageCandidate(contact="张三", text="这个报价多少钱？", received_at=self.now)

        decision = policy.evaluate(message, user_offline=True, paused=False, now=self.now)

        self.assertFalse(decision.allow_send)
        self.assertEqual(decision.risk_level, RiskLevel.MEDIUM)
        self.assertEqual(decision.reason, "risk_excluded")

    def test_low_risk_message_gets_template_and_delay_under_one_minute(self):
        rng = FixedRandom()
        policy = ReplyPolicy(rng=rng, delay_range_seconds=(20, 60))
        message = MessageCandidate(contact="张三", text="在吗", received_at=self.now)

        decision = policy.evaluate(message, user_offline=True, paused=False, now=self.now)

        self.assertTrue(decision.allow_send)
        self.assertEqual(decision.risk_level, RiskLevel.LOW)
        self.assertEqual(decision.reply_text, "收到，我稍后看完回复你。")
        self.assertEqual(decision.delay_seconds, 60)
        self.assertEqual(rng.last_bounds, (20, 60))

    def test_contact_cooldown_blocks_repeat_auto_reply(self):
        policy = ReplyPolicy(contact_cooldown_seconds=600)
        message = MessageCandidate(contact="张三", text="在吗", received_at=self.now)

        decision = policy.evaluate(
            message,
            user_offline=True,
            paused=False,
            now=self.now,
            last_auto_reply_at=self.now - dt.timedelta(seconds=120),
        )

        self.assertFalse(decision.allow_send)
        self.assertEqual(decision.reason, "cooldown")


class SendGuardTests(unittest.TestCase):
    def test_pending_send_is_cancelled_when_user_returns(self):
        guard = SendGuard()

        result = guard.check_before_send(
            user_offline=False,
            paused=False,
            cooldown_ok=True,
            human_replied_after_received=False,
        )

        self.assertTrue(result.cancel)
        self.assertEqual(result.reason, "user_returned")

    def test_pending_send_is_cancelled_when_human_replied(self):
        guard = SendGuard()

        result = guard.check_before_send(
            user_offline=True,
            paused=False,
            cooldown_ok=True,
            human_replied_after_received=True,
        )

        self.assertTrue(result.cancel)
        self.assertEqual(result.reason, "human_replied")


if __name__ == "__main__":
    unittest.main()

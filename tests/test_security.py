import datetime as dt
import tempfile
import unittest
from pathlib import Path

from wechat_bot.config import AppConfig, _read_env_file
from wechat_bot.policy import MessageCandidate, ReplyPolicy, RiskLevel


class SecurityTests(unittest.TestCase):
    def test_risk_keywords_bypass_with_spaces(self):
        """测试关键词绕过：插入空格"""
        policy = ReplyPolicy()
        message = MessageCandidate(
            contact="攻击者",
            text="这个多 少 钱？",  # 插入空格
            received_at=dt.datetime.now(),
        )
        risk = policy.classify_risk(message.text)
        self.assertEqual(risk, RiskLevel.MEDIUM, "应检测到风险关键词")

    def test_risk_keywords_bypass_with_punctuation(self):
        """测试关键词绕过：插入标点符号"""
        policy = ReplyPolicy()
        test_cases = [
            "多-少-钱",
            "多.少.钱",
            "多/少/钱",
            "报。价",
            "转—账",
        ]
        for text in test_cases:
            with self.subTest(text=text):
                risk = policy.classify_risk(text)
                self.assertEqual(risk, RiskLevel.MEDIUM, f"应检测到风险关键词: {text}")

    def test_risk_keywords_new_keywords(self):
        """测试新增的风险关键词"""
        policy = ReplyPolicy()
        test_cases = [
            "微信支付",
            "支付宝",
            "银行卡",
            "借钱",
            "贷款",
            "维权",
            "手机号",
            "删除",
            "授权",
            "紧急",
            "立即处理",
        ]
        for text in test_cases:
            with self.subTest(text=text):
                risk = policy.classify_risk(text)
                self.assertEqual(risk, RiskLevel.MEDIUM, f"应检测到风险关键词: {text}")

    def test_path_traversal_in_data_dir(self):
        """测试路径遍历攻击"""
        with tempfile.NamedTemporaryFile(mode="w", suffix=".env", delete=False, encoding="utf-8") as f:
            f.write("DATA_DIR=../../etc\n")
            f.flush()
            env_path = Path(f.name)

        try:
            AppConfig.from_env_file(env_path)
            self.fail("应拒绝目录遍历路径")
        except ValueError as e:
            self.assertIn("must be under project root", str(e))
        finally:
            env_path.unlink(missing_ok=True)

    def test_env_value_too_long(self):
        """测试超长环境变量值"""
        with tempfile.NamedTemporaryFile(mode="w", suffix=".env", delete=False, encoding="utf-8") as f:
            f.write(f'OPENAI_API_KEY={"x" * 20000}\n')
            f.flush()
            env_path = Path(f.name)

        try:
            _read_env_file(env_path)
            self.fail("应拒绝超长值")
        except ValueError as e:
            self.assertIn("too long", str(e))
        finally:
            env_path.unlink(missing_ok=True)

    def test_env_file_too_large(self):
        """测试超大环境文件"""
        with tempfile.NamedTemporaryFile(mode="w", suffix=".env", delete=False, encoding="utf-8") as f:
            # 写入超过 100KB 的内容
            for i in range(20000):
                f.write(f"VAR_{i}=value_{i}\n")
            f.flush()
            env_path = Path(f.name)

        try:
            _read_env_file(env_path)
            self.fail("应拒绝超大文件")
        except ValueError as e:
            self.assertIn("too large", str(e))
        finally:
            env_path.unlink(missing_ok=True)

    def test_env_invalid_key_names(self):
        """测试非法环境变量键名"""
        with tempfile.NamedTemporaryFile(mode="w", suffix=".env", delete=False, encoding="utf-8") as f:
            f.write("VALID_KEY=value1\n")
            f.write("invalid-key=value2\n")  # 包含非法字符
            f.write("123INVALID=value3\n")  # 数字开头
            f.write("ANOTHER_VALID=value4\n")
            f.flush()
            env_path = Path(f.name)

        try:
            values = _read_env_file(env_path)
            # 应该只包含合法的键
            self.assertIn("VALID_KEY", values)
            self.assertIn("ANOTHER_VALID", values)
            self.assertNotIn("invalid-key", values)
            self.assertNotIn("123INVALID", values)
        finally:
            env_path.unlink(missing_ok=True)

    def test_config_api_key_not_in_repr(self):
        """测试配置对象的 repr 不包含 API key"""
        with tempfile.NamedTemporaryFile(mode="w", suffix=".env", delete=False, encoding="utf-8") as f:
            f.write("OPENAI_BASE_URL=https://api.example.com\n")
            f.write("OPENAI_API_KEY=sk-secret123456\n")
            f.write("MODEL_NAME=test-model\n")
            f.write("DATA_DIR=data\n")
            f.flush()
            env_path = Path(f.name)

        try:
            config = AppConfig.from_env_file(env_path)
            repr_str = repr(config)
            str_str = str(config)

            # API key 不应出现在 repr 和 str 中
            self.assertNotIn("sk-secret", repr_str)
            self.assertNotIn("sk-secret", str_str)

            # 但其他字段应该可见
            self.assertIn("test-model", str_str)
        finally:
            env_path.unlink(missing_ok=True)


if __name__ == "__main__":
    unittest.main()

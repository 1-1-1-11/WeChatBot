# WeChatBot - PC 微信值班助手

这个项目面向国内 PC 微信 / `Weixin.exe`，不是面向国外 WeChat 场景。

首版目标：

- 程序启动后只处理新的个人微信消息。
- 使用者在线时只记录和汇总，不自动回复。
- 电脑空闲超过 10 分钟后，才允许低风险消息自动回复。
- 自动回复只使用固定短模板，并在 20-60 秒随机延迟后再次检查是否还能发送。
- 金额、报价、承诺、投诉、隐私等消息进入待办风险，不自动回复。
- 每天 22:00 生成一次每日总览。
- 不做截图、不保存截图、不上传图片。

## 当前状态

已实现：

- `wechat_bot/` 业务包。
- SQLite 本地记录，默认数据目录 `data/`。
- `.env` 配置读取。
- Tkinter 控制台。
- dry-run 模式。
- `pyweixin` 消息读取/发送适配层。
- 单元测试和 smoke test。

仍需现场验证：

- 使用测试联系人发送新消息，验证 `pyweixin` 能读取 PC 微信 4.1.9.55 的实际新消息。
- 在测试联系人上关闭 `DRY_RUN` 后验证真实文本发送。
- 使用真实中转 API key 验证 22:00 每日汇总。

## 安装

使用 Codex bundled Python 或本机 Python 3.12：

```powershell
$py='C:\Users\32299\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe'
& $py -m pip install -r requirements.txt
```

## 配置

复制 `.env.example` 为 `.env`，填入你的 OpenAI 兼容中转 API：

```env
OPENAI_BASE_URL=https://api.example.com
OPENAI_API_KEY=replace-me
MODEL_NAME=replace-me
IDLE_MINUTES=10
AUTO_REPLY_DELAY_MIN_SECONDS=20
AUTO_REPLY_DELAY_MAX_SECONDS=60
CONTACT_COOLDOWN_MINUTES=10
DATA_DIR=data
DRY_RUN=true
```

首轮测试建议保持：

```env
DRY_RUN=true
```

## 运行

Smoke test：

```powershell
& $py -m wechat_bot.app --env .env.example --smoke-test
```

启动控制台：

```powershell
& $py -m wechat_bot --env .env
```

控制台包含：

- 暂停自动回复。
- 自动检测 / 强制在线 / 强制离线。
- 待办风险。
- 自动回复日志。
- 每日总览。

## 安全边界

- 默认 `DRY_RUN=true`，不会真实发送微信消息。
- 只有 `DRY_RUN=false` 才会通过 `pyweixin` 操作 PC 微信发送文本。
- 自动回复只发固定模板，不让模型自由生成自动发送内容。
- 自动发送前会延迟并再次检查使用者是否回来、是否暂停、是否触发限频。
- 只处理个人文本消息；群聊和非文本消息会被保守忽略或进入待办。

## 上游来源

本项目基于 GitHub 资源 `Hello-Mr-Crab/pywechat`，固定导入 commit：

```text
27961984f59e506604c5c0e9f0c62c8844a047dd
```

4.1+ PC 微信自动化主要使用上游 `pyweixin` 模块。上游说明保留在 `Weixin4.0.md` 和源码目录中。

许可证沿用上游 `LICENSE`。

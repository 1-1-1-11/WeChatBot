# WeChatBot 快速入门指南

> 🤖 PC 微信智能值班助手 - 从零开始的完整使用教程

本指南将带你从零开始配置和使用 WeChatBot，包括环境准备、配置、测试和正式运行。

---

## 📋 目录

1. [前置要求](#前置要求)
2. [第一步：安装依赖](#第一步安装依赖)
3. [第二步：配置微信 UI Automation](#第二步配置微信-ui-automation)
4. [第三步：创建配置文件](#第三步创建配置文件)
5. [第四步：运行测试](#第四步运行测试)
6. [第五步：现场验证](#第五步现场验证)
7. [第六步：启动控制台](#第六步启动控制台)
8. [常见问题](#常见问题)
9. [安全提示](#安全提示)

---

## 前置要求

在开始之前，请确保你有：

- ✅ **Windows 10/11** 操作系统
- ✅ **PC 微信客户端** (版本 4.1.9.55 或更高)
- ✅ **Python 3.9+** (推荐 Python 3.12)
- ✅ **已登录的微信账号**
- ✅ **OpenAI 兼容 API** (用于每日汇总功能)
- ✅ **测试联系人** (用于验证自动回复)

---

## 第一步：安装依赖

### 1.1 确认 Python 环境

打开 PowerShell，检查 Python 版本：

```powershell
python --version
```

应显示 `Python 3.9.x` 或更高版本。

### 1.2 定位 Python 路径

如果你使用 Codex bundled Python：

```powershell
$py = 'C:\Users\32299\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe'
& $py --version
```

如果使用系统 Python，直接使用 `python` 命令即可。

### 1.3 安装依赖包

```powershell
# 使用 bundled Python
& $py -m pip install -r requirements.txt

# 或使用系统 Python
python -m pip install -r requirements.txt
```

**依赖包列表**：
- `psutil` - 系统监控
- `pyautogui` - 自动化
- `pycaw` - 音频控制
- `pywin32` - Windows API
- `pywinauto` - UI Automation
- `pillow` - 图像处理
- `emoji` - Emoji 支持

安装完成后，验证导入：

```powershell
python -c "import pyweixin; print('pyweixin 导入成功')"
```

---

## 第二步：配置微信 UI Automation

> ⚠️ **关键步骤**：微信 4.1+ 默认隐藏 UI Automation 元素，必须通过讲述人模式激活。

### 2.1 开启 Windows 讲述人

**在微信登录之前**，执行以下操作：

1. 按 `Win + Ctrl + Enter` 启动 Windows 讲述人
2. 或：`设置 > 轻松使用 > 讲述人 > 启用讲述人`

### 2.2 登录微信

启动讲述人后：

1. 打开微信客户端
2. 扫码登录
3. **保持讲述人运行至少 5 分钟**

### 2.3 关闭讲述人

5 分钟后，按 `Win + Ctrl + Enter` 关闭讲述人。

### 2.4 验证 UI 可见性

```powershell
python -m wechat_bot.app --env .env.example --live-check
```

**期望输出**：
```
live-check: read 0 personal text message(s)
```

**如果显示 `微信 UI Automation 不可用`**：
- 重新登录微信前再次开启讲述人
- 确保微信窗口可见（不要最小化）
- 检查微信版本是否为 4.1+

> 💡 **提示**：讲述人激活一次后，后续使用通常无需再次激活。

---

## 第三步：创建配置文件

### 3.1 复制示例配置

```powershell
Copy-Item .env.example .env
```

### 3.2 编辑配置文件

用文本编辑器打开 `.env` 文件：

```env
# OpenAI 兼容 API 配置（用于每日汇总）
OPENAI_BASE_URL=https://api.example.com
OPENAI_API_KEY=sk-your-api-key-here
MODEL_NAME=gpt-3.5-turbo

# 用户在线检测配置
IDLE_MINUTES=10                      # 空闲多少分钟判断为离线

# 自动回复延迟配置
AUTO_REPLY_DELAY_MIN_SECONDS=20      # 最小延迟（秒）
AUTO_REPLY_DELAY_MAX_SECONDS=60      # 最大延迟（秒）

# 联系人冷却时间
CONTACT_COOLDOWN_MINUTES=10          # 同一联系人的回复间隔（分钟）

# 数据存储目录
DATA_DIR=data                        # 数据库存储目录

# 安全开关
DRY_RUN=true                         # 测试模式，不真实发送消息
```

### 3.3 配置说明

#### API 配置
- `OPENAI_BASE_URL`: OpenAI 兼容 API 的基础 URL
- `OPENAI_API_KEY`: 你的 API 密钥
- `MODEL_NAME`: 使用的模型名称（如 `gpt-3.5-turbo`, `gpt-4`）

#### 行为配置
- `IDLE_MINUTES`: 电脑空闲多久后触发"离线值班"模式
- `AUTO_REPLY_DELAY_MIN/MAX_SECONDS`: 自动回复的随机延迟范围
- `CONTACT_COOLDOWN_MINUTES`: 防止对同一联系人频繁回复

#### 安全配置
- `DRY_RUN=true`: **首次使用必须保持为 true**，只记录不发送
- `DRY_RUN=false`: 正式运行，会真实发送微信消息

---

## 第四步：运行测试

### 4.1 Smoke Test（构建测试）

验证运行时可以正常构建：

```powershell
python -m wechat_bot.app --env .env --smoke-test
```

**期望输出**：
```
smoke ok: 微信值班助手运行时可构建
```

### 4.2 单元测试

运行完整的测试套件：

```powershell
python -m unittest discover -s tests -v
```

**期望输出**：
```
Ran 38 tests in 0.3s
OK
```

### 4.3 Live Check（只读测试）

**不发送任何消息**，只读取当前新消息：

```powershell
python -m wechat_bot.app --env .env --live-check
```

**期望输出**：
```
live-check: read 2 personal text message(s)
- 张三: 在吗
- 李四: 明天开会
```

> 💡 **提示**：如果输出为 `read 0 personal text message(s)`，说明没有新消息，这是正常的。

---

## 第五步：现场验证

### 5.1 准备测试联系人

找一个测试用的微信联系人（**不要用重要联系人！**）。

### 5.2 发送测试消息

让测试联系人给你发送一条**低风险消息**：

```
在吗？
```

或

```
今天有空吗？
```

**避免发送风险消息**（会被拒绝自动回复）：
- ❌ "这个报价多少钱？"
- ❌ "微信支付链接"
- ❌ "帮我删除一下"
- ❌ "紧急！立即处理"

### 5.3 Dry-Run 测试

**保持 `DRY_RUN=true`**，启动控制台：

```powershell
python -m wechat_bot --env .env
```

控制台会显示：

```
微信值班状态：在线汇总 | 模式：auto | 空闲：0 秒
```

#### 触发自动回复（测试模式）

1. **让电脑空闲 10 分钟**（不动鼠标和键盘）
2. 状态变为：`离线值班 | 空闲：600 秒`
3. 让测试联系人再发一条消息
4. **20-60 秒后**，查看控制台"自动回复"标签页

**Dry-Run 模式下**：
- ✅ 会记录"准备发送"的消息
- ✅ 会显示在"自动回复"日志中
- ❌ **不会真实发送微信消息**

### 5.4 真实发送测试（谨慎！）

> ⚠️ **警告**：只有在 Dry-Run 测试完全正常后，才进行此步骤。

1. 编辑 `.env` 文件：
   ```env
   DRY_RUN=false
   ```

2. 重启控制台：
   ```powershell
   python -m wechat_bot --env .env
   ```

3. 重复上述步骤（空闲 10 分钟，测试联系人发消息）

4. **20-60 秒后**，测试联系人应收到自动回复：
   - "收到，我稍后看完回复你。"
   - "好的，我晚点回复你。"
   - "我现在不太方便，稍后回你。"

5. **验证完成后**，立即改回：
   ```env
   DRY_RUN=true
   ```

---

## 第六步：启动控制台

### 6.1 启动命令

```powershell
python -m wechat_bot --env .env
```

### 6.2 控制台界面

控制台包含以下区域：

```
┌─────────────────────────────────────────────────┐
│ 微信值班状态：离线值班 | 模式：auto | 空闲：650秒 │
├─────────────────────────────────────────────────┤
│ [ ] 暂停自动回复                                │
│ ( ) 自动检测  ( ) 强制在线  ( ) 强制离线        │
├─────────────────────────────────────────────────┤
│ [每日总览] [待办风险] [自动回复]                 │
│                                                 │
│ 每日 22:00 生成总览；当前尚未生成。              │
│                                                 │
└─────────────────────────────────────────────────┘
```

### 6.3 控制面板说明

#### 状态显示
- **在线汇总**: 用户活跃，只记录不回复
- **离线值班**: 用户离线，允许自动回复

#### 控制选项

| 选项 | 说明 |
|------|------|
| **暂停自动回复** | 勾选后，即使离线也不自动回复 |
| **自动检测** | 根据空闲时间自动判断在线/离线 |
| **强制在线** | 始终视为在线，不自动回复 |
| **强制离线** | 始终视为离线，允许自动回复 |

#### 信息标签页

| 标签 | 内容 |
|------|------|
| **每日总览** | 22:00 自动生成的每日消息汇总 |
| **待办风险** | 中风险消息（金额、投诉等） |
| **自动回复** | 已发送的自动回复日志 |

### 6.4 运行模式

#### 日常使用模式
```env
DRY_RUN=false           # 真实发送
IDLE_MINUTES=10         # 空闲 10 分钟触发
```

#### 测试模式
```env
DRY_RUN=true            # 不真实发送
IDLE_MINUTES=1          # 空闲 1 分钟即触发（方便测试）
```

#### 保守模式
```env
DRY_RUN=false
IDLE_MINUTES=30         # 空闲 30 分钟才触发
AUTO_REPLY_DELAY_MIN_SECONDS=60
AUTO_REPLY_DELAY_MAX_SECONDS=120
```

---

## 常见问题

### Q1: "微信 UI Automation 不可用"

**原因**：微信 4.1+ 隐藏了 UI Automation 元素。

**解决**：
1. 完全退出微信
2. 启动 Windows 讲述人（`Win + Ctrl + Enter`）
3. 重新登录微信
4. 保持讲述人运行 5 分钟
5. 关闭讲述人
6. 重试 `--live-check`

### Q2: 为什么不自动回复？

检查以下条件是否满足：

- [ ] 电脑空闲时间 ≥ `IDLE_MINUTES` 分钟
- [ ] 消息是**个人消息**（不是群聊）
- [ ] 消息是**低风险**（不包含"报价"、"转账"等关键词）
- [ ] 联系人冷却时间已过（距上次回复 ≥ `CONTACT_COOLDOWN_MINUTES` 分钟）
- [ ] 未勾选"暂停自动回复"
- [ ] `DRY_RUN=false`（真实发送模式）

### Q3: 如何查看详细日志？

数据库文件位于 `data/wechat_bot.sqlite3`，可用 SQLite 工具打开：

```powershell
# 安装 SQLite
choco install sqlite

# 查看数据库
sqlite3 data/wechat_bot.sqlite3

# 查询今日消息
SELECT * FROM messages WHERE date(received_at) = date('now');

# 查询自动回复
SELECT * FROM auto_replies WHERE date(sent_at) = date('now');
```

### Q4: 每日总览没有生成？

检查：
- [ ] 当前时间 ≥ 22:00
- [ ] 配置文件中 API 配置正确
- [ ] 控制台正在运行
- [ ] 今天有收到消息

手动触发总览生成（调试）：
```python
python -c "from wechat_bot.summary import DailySummaryService; from wechat_bot.db import BotDatabase; import datetime; db = BotDatabase('data/wechat_bot.sqlite3'); service = DailySummaryService(db=db, model_client=None); print(service.maybe_generate(now=datetime.datetime.now()))"
```

### Q5: 如何卸载？

```powershell
# 停止控制台
# 按 Ctrl+C 或关闭窗口

# 删除数据库
Remove-Item -Recurse -Force data/

# 删除配置
Remove-Item .env

# 卸载项目（可选）
Remove-Item -Recurse -Force D:\Desktop\WechatBot\
```

---

## 安全提示

### ✅ 安全实践

1. **`.env` 文件保密**
   - 包含 API 密钥，切勿上传到 GitHub
   - 已加入 `.gitignore`

2. **首次使用 Dry-Run**
   - 新环境先用 `DRY_RUN=true` 测试
   - 确认无误后再改为 `false`

3. **风险关键词覆盖**
   - 项目已内置 50+ 风险关键词
   - 金额、投诉、隐私等消息不会自动回复

4. **延迟二次确认**
   - 20-60 秒延迟期间，如果用户回来会取消发送
   - 防止"用户刚离开就自动回复"的尴尬

5. **数据本地存储**
   - 所有消息记录在本地 SQLite
   - 不上传到云端

### ⚠️ 风险提示

- **不建议用于商业客服**：自动回复是固定模板，不适合专业客服场景
- **不保证 100% 准确**：风险分类可能有误判
- **API 费用**：每日汇总会调用 LLM API（约 0.01-0.1 元/天）
- **微信政策**：自动化操作可能违反微信使用条款，后果自负

---

## 进阶配置

### 自定义回复模板

编辑 `wechat_bot/policy.py`：

```python
DEFAULT_TEMPLATES = (
    "收到，我稍后看完回复你。",
    "好的，我晚点回复你。",
    "我现在不太方便，稍后回你。",
    "已收到，稍后联系！",  # 新增
)
```

### 自定义风险关键词

编辑 `wechat_bot/policy.py`：

```python
MEDIUM_RISK_KEYWORDS = (
    # 现有关键词...
    "你的特定关键词",  # 新增
)
```

### 修改每日汇总时间

编辑 `wechat_bot/app.py`：

```python
summary_service = DailySummaryService(
    db=db, 
    model_client=client, 
    generate_hour=20  # 改为 20:00 生成
)
```

---

## 获取帮助

- **项目主页**: https://github.com/1-1-1-11/WeChatBot
- **问题反馈**: 创建 GitHub Issue
- **技术文档**: 
  - `README.md` - 项目概览
  - `Weixin4.0.md` - UI Automation 原理
  - `handoff.md` - 开发交接记录

---

## 下一步

现在你已经成功配置并运行 WeChatBot！建议：

1. ✅ 用测试联系人充分验证
2. ✅ 观察 1-2 天的运行情况
3. ✅ 根据实际使用调整配置
4. ✅ 定期查看"待办风险"标签页
5. ✅ 每周清理一次数据库（`purge_older_than`）

**祝使用愉快！** 🎉

---

*最后更新：2026-06-02*

# WeChatBot - PC 微信智能值班助手

> 基于 PC 微信的智能值班助手，当你离开电脑时自动回复微信消息。使用 AI 生成自然的回复内容，支持风险检测、冷却时间等智能策略。

**适用场景**：国内 PC 微信 / `Weixin.exe`（不支持国外 WeChat）

---

## ✨ 核心特性

- 🤖 **AI 智能回复** - 使用 OpenAI 兼容 API 生成自然回复
- 🎨 **现代化界面** - 深色主题、卡片式设计、实时状态监控
- 🛡️ **风险防护** - 自动识别敏感消息（转账、报价等）避免误回复
- ⏱️ **冷却机制** - 限制同一联系人回复频率，避免刷屏
- 📊 **数据统计** - 每日消息汇总、待办提醒、回复记录
- 🧪 **测试模式** - DRY_RUN 模式下只记录不发送，安全测试

---

## 🎯 工作原理

1. **在线时**：只记录消息，不自动回复
2. **电脑空闲 ≥10 分钟**：进入离线值班模式
3. **收到个人消息**：AI 分析并生成回复
4. **风险检测**：敏感消息（报价、转账等）进入待办，不自动回复
5. **延迟发送**：20-60 秒随机延迟，二次检查后发送
6. **每日总览**：22:00 自动生成每日汇总

---

## 📋 已实现功能

✅ **核心功能**
- `wechat_bot/` 业务包
- SQLite 本地数据存储（`data/` 目录）
- `.env` 配置文件支持
- 现代化 Tkinter 控制台（深色主题 + 经典界面）
- DRY_RUN 测试模式
- `pyweixin` 消息读取/发送适配层
- 完整的单元测试和烟雾测试

✅ **安全机制**
- 默认测试模式，不会误发消息
- 风险关键词检测（50+ 关键词）
- 冷却时间限制
- 发送前二次检查
- API Key 不记录到日志

📝 **待现场验证**
- 使用测试联系人验证 `pyweixin` 读取消息
- 关闭 `DRY_RUN` 后验证真实发送
- 验证 22:00 每日汇总生成

---

## 🚀 快速开始

### 前置要求

- **Windows 10/11**
- **Python 3.9+**
- **PC 微信 4.1+**（需启用 UI Automation）

### 安装步骤

#### 1️⃣ 克隆项目
```bash
git clone <your-repo-url>
cd WechatBot
```

#### 2️⃣ 安装依赖
```bash
pip install -r requirements.txt
```

#### 3️⃣ 配置环境变量
```bash
# 复制配置模板
copy .env.example .env

# 编辑配置文件
notepad .env
```

**必填项**：
```env
OPENAI_BASE_URL=https://api.openai.com
OPENAI_API_KEY=sk-your-api-key-here
MODEL_NAME=gpt-3.5-turbo
DRY_RUN=true  # 首次使用保持 true（测试模式）
```

**可选项**（使用默认值即可）：
```env
IDLE_MINUTES=10                      # 空闲多久触发离线
AUTO_REPLY_DELAY_MIN_SECONDS=20      # 回复延迟最小值
AUTO_REPLY_DELAY_MAX_SECONDS=60      # 回复延迟最大值
CONTACT_COOLDOWN_MINUTES=10          # 同一联系人冷却时间
DATA_DIR=data                        # 数据存储目录
```

#### 4️⃣ 配置微信 UI Automation（仅首次）

**为什么需要**：PC 微信 4.1+ 默认隐藏 UI Automation 元素，需要激活后才能读取消息。

**操作步骤**：
1. 按 `Win + Ctrl + Enter` 启动 Windows 讲述人
2. 登录 PC 微信
3. 等待 5 分钟
4. 按 `Win + Ctrl + Enter` 关闭讲述人

详见 [Weixin4.0.md](Weixin4.0.md)

#### 5️⃣ 启动程序

**方式 1：双击批处理文件（推荐）**
```
modern-start.bat       # 现代化深色界面（推荐）
quick-start.bat        # 经典界面（测试模式）
production-start.bat   # 经典界面（生产模式）
setup-wizard.bat       # 交互式配置向导
full-start.bat         # 完整启动（含环境检查）
```

**方式 2：命令行**
```bash
# 现代化界面（默认）
python -m wechat_bot --env .env

# 经典界面
python -m wechat_bot --env .env --classic-ui

# 烟雾测试（验证配置）
python -m wechat_bot --env .env --smoke-test

# 检查微信 UI Automation
python -m wechat_bot --env .env --live-check
```

---

## 📖 使用指南

### 现代化界面

详见 [现代界面使用指南.md](现代界面使用指南.md)

**核心功能**：
- 🟢 **状态指示灯** - 实时显示在线/离线/错误状态
- 🎛️ **快速控制** - 一键暂停、模式切换
- 📊 **实时统计** - 今日消息数、回复数、待办风险
- 📝 **消息日志** - 三个标签页（自动回复/待办风险/每日总览）

### 自动回复触发条件

**必须同时满足**以下所有条件：
1. ✅ 电脑空闲 ≥ 10 分钟（默认）
2. ✅ 收到个人消息（非群聊）
3. ✅ 低风险消息（不含"转账"、"报价"等关键词）
4. ✅ 距上次回复该联系人 ≥ 10 分钟
5. ✅ 未勾选"暂停自动回复"
6. ✅ DRY_RUN=false（生产模式）

### 风险关键词（不自动回复）

- **金融相关**：多少钱、报价、付款、转账、发票、合同等
- **敏感操作**：删除、修改、授权、密码、验证码等
- **紧急情况**：紧急、立即、马上、加急等
- **投诉风险**：投诉、不满意、退款、赔偿、法律等

---

## 🧪 测试流程

### 首次测试

1. 确保 `DRY_RUN=true`（测试模式）
2. 启动程序：`python -m wechat_bot --env .env`
3. 让电脑空闲 10 分钟（不动鼠标键盘）
4. 让测试联系人发送消息："在吗"
5. 查看控制台"💬 自动回复"标签页，应该看到记录但不会真实发送

### 生产部署

1. 充分测试后，修改 `.env`：
   ```env
   DRY_RUN=false
   ```
2. 重新启动程序
3. 电脑空闲后会真实发送回复

---

## 🔒 安全机制

- ✅ **默认测试模式** - `DRY_RUN=true` 不会发送任何消息
- ✅ **风险检测** - 50+ 敏感关键词自动拦截
- ✅ **二次检查** - 发送前再次验证在线状态和冷却时间
- ✅ **冷却限制** - 同一联系人 10 分钟内只回复一次
- ✅ **延迟发送** - 20-60 秒随机延迟，模拟真人
- ✅ **只处理个人消息** - 群聊和非文本消息自动忽略
- ✅ **API Key 保护** - 不记录到日志和控制台

---

## 📚 文档索引

- **[现代界面使用指南.md](现代界面使用指南.md)** - 新界面完整指南
- **[GETTING_STARTED.md](GETTING_STARTED.md)** - 详细入门教程（英文）
- **[QUICK_START.md](QUICK_START.md)** - 快速入门（英文）
- **[README_CN.txt](README_CN.txt)** - 简明中文说明
- **[Weixin4.0.md](Weixin4.0.md)** - 微信 4.0+ UI Automation 说明

---

## ❓ 常见问题

### Q1: 为什么不自动回复？
**检查清单**：
- [ ] `DRY_RUN=false`（生产模式）
- [ ] 电脑空闲 ≥ 10 分钟
- [ ] 收到的是个人消息（非群聊）
- [ ] 未勾选"暂停自动回复"
- [ ] 消息不含风险关键词
- [ ] 距上次回复该联系人 ≥ 10 分钟

### Q2: 提示"Python not found"
**解决**：
1. 下载 Python 3.9+：https://www.python.org/downloads/
2. 安装时勾选 "Add Python to PATH"

### Q3: 微信 UI Automation 不可用
**解决**：
1. 按 `Win + Ctrl + Enter` 启动讲述人
2. 登录微信，等待 5 分钟
3. 关闭讲述人，运行：`python -m wechat_bot --env .env --live-check`
4. 如果仍失败，查看 [Weixin4.0.md](Weixin4.0.md)

### Q4: 批处理文件显示乱码
**解决**：使用英文版批处理文件（已删除中文版）：
- `setup-wizard.bat`（配置向导）
- `quick-start.bat`（快速启动）
- `modern-start.bat`（现代界面）

### Q5: 如何查看数据库？
**位置**：`data/wechat_bot.sqlite3`

**查看工具**：
- [DB Browser for SQLite](https://sqlitebrowser.org/)
- [DBeaver](https://dbeaver.io/)

**表结构**：
- `messages` - 收到的消息记录
- `auto_replies` - 自动回复历史
- `pending_items` - 待办风险项

---

## 🛠️ 高级功能

### 命令行选项

```bash
# 烟雾测试（验证配置）
python -m wechat_bot --env .env --smoke-test

# 检查微信 UI Automation
python -m wechat_bot --env .env --live-check

# 使用经典界面
python -m wechat_bot --env .env --classic-ui
```

### 自定义配色（现代界面）

编辑 `wechat_bot/modern_dashboard.py` 的顶部常量：

```python
class ModernDashboard:
    # 深色主题配色
    BG_DARK = "#1e1e1e"        # 主背景
    BG_SIDEBAR = "#252526"     # 侧边栏背景
    BG_CARD = "#2d2d30"        # 卡片背景
    ACCENT_GREEN = "#4ec9b0"   # 在线状态
    ACCENT_ORANGE = "#ce9178"  # 离线状态
    ACCENT_RED = "#f48771"     # 错误状态
```

---

## 📊 项目结构

```
WechatBot/
├── wechat_bot/              # 核心业务包
│   ├── app.py               # 入口文件
│   ├── config.py            # 配置读取
│   ├── dashboard.py         # 经典界面
│   ├── modern_dashboard.py  # 现代化界面（新）
│   ├── db.py                # 数据库层
│   ├── policy.py            # 回复策略和风险检测
│   ├── presence.py          # 在线状态检测
│   ├── runtime.py           # 运行时核心逻辑
│   ├── summary.py           # 每日总览生成
│   ├── model_client.py      # OpenAI API 客户端
│   └── wechat_adapter.py    # 微信消息读取/发送
├── tests/                   # 单元测试
├── data/                    # 数据目录（SQLite）
├── .env.example             # 配置模板
├── requirements.txt         # Python 依赖
├── modern-start.bat         # 现代界面启动脚本
├── quick-start.bat          # 快速启动（测试模式）
├── production-start.bat     # 生产启动
├── setup-wizard.bat         # 配置向导
└── full-start.bat           # 完整启动（含检查）
```

---

## 🔧 技术栈

- **语言**：Python 3.9+
- **UI 框架**：Tkinter（内置）
- **数据库**：SQLite3
- **微信自动化**：`pyweixin` (基于 UI Automation)
- **AI 模型**：OpenAI 兼容 API
- **测试框架**：unittest

---

## 📝 开发笔记

### 线程安全设计
- UI 刷新在主线程，消息处理在工作线程
- 使用 `threading.Lock` 保护共享状态（暂停状态、冷却时间）
- 避免 Tkinter 跨线程访问问题

### 性能优化
- 日志最多显示 20 条（避免内存占用）
- 2-3 秒刷新间隔（平衡实时性和性能）
- 消息去重使用有界队列（maxlen=10000）

### 安全考量
- API Key 使用 `field(repr=False)` 隐藏
- 环境变量解析限制值长度和文件大小
- 网络请求限制响应大小（10MB）
- SQL 查询使用参数化（防注入）

---

## 🎉 开始使用

**双击运行**：`modern-start.bat`

或在命令行：
```bash
python -m wechat_bot --env .env
```

**祝使用愉快！** 🚀

---

## 📄 许可证与致谢

本项目基于 GitHub 资源 `Hello-Mr-Crab/pywechat`，固定导入 commit：

```text
27961984f59e506604c5c0e9f0c62c8844a047dd
```

4.1+ PC 微信自动化主要使用上游 `pyweixin` 模块。上游说明保留在 `Weixin4.0.md` 和源码目录中。

许可证沿用上游 `LICENSE`。

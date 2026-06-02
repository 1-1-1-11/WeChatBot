# 请阅读 - 批处理文件使用说明

## ⚠️ 重要提示

中文批处理文件（配置向导.bat、快速启动.bat、生产模式启动.bat）**有编码问题**，会显示乱码。

**请使用英文版本的批处理文件，它们功能完全相同且更稳定！**

---

## ✅ 推荐使用（英文版批处理文件）

### 方式 1：使用批处理文件

| 文件名 | 功能 | 何时使用 |
|--------|------|----------|
| **setup-wizard.bat** | 配置向导 | 首次使用，交互式配置 |
| **quick-start.bat** | 快速启动（测试模式） | 日常测试，不发送消息 |
| **production-start.bat** | 生产启动（真实发送） | 充分测试后正式使用 |
| **full-start.bat** | 完整启动（含检查） | 包含依赖和环境检查 |

**使用步骤**：
1. 双击 `setup-wizard.bat` 完成配置
2. 双击 `quick-start.bat` 开始测试
3. 测试成功后，双击 `production-start.bat` 正式使用

---

### 方式 2：直接用命令行（推荐新手）

这是最简单稳定的方法：

```powershell
# 打开 PowerShell，进入项目目录
cd D:\Desktop\WechatBot

# 1. 创建配置文件
copy .env.example .env

# 2. 编辑配置（用记事本打开）
notepad .env
```

在记事本中修改以下内容：
```
OPENAI_BASE_URL=https://api.openai.com
OPENAI_API_KEY=sk-你的密钥
MODEL_NAME=gpt-3.5-turbo
DRY_RUN=true
```
保存并关闭。

```powershell
# 3. 安装依赖
python -m pip install -r requirements.txt

# 4. 启动（测试模式）
python -m wechat_bot --env .env
```

---

## 📝 配置文件说明

编辑 `.env` 文件，必须修改的内容：

```env
# 必须修改
OPENAI_BASE_URL=https://api.openai.com    # 你的 API 地址
OPENAI_API_KEY=sk-your-key-here           # 你的 API 密钥
MODEL_NAME=gpt-3.5-turbo                  # 模型名称

# 可选修改
IDLE_MINUTES=10                           # 空闲多少分钟触发
DRY_RUN=true                              # true=测试，false=真实发送
```

---

## 🧪 测试流程

1. 确保 `DRY_RUN=true`（测试模式）
2. 启动程序
3. 让电脑空闲 10 分钟
4. 测试联系人发消息："在吗"
5. 查看控制台是否有记录（但不会真实发送）
6. 测试成功后，修改 `DRY_RUN=false`，重新启动

---

## ❓ 常见问题

### Q: 批处理文件显示乱码怎么办？
**A**: 使用英文版本：`setup-wizard.bat`、`quick-start.bat`

### Q: 提示"Python not found"？
**A**: 安装 Python 3.9+，记得勾选"Add Python to PATH"
https://www.python.org/downloads/

### Q: 为什么不自动回复？
**A**: 检查：
- DRY_RUN 是 false 吗？
- 电脑空闲 10 分钟了吗？
- 是个人消息（不是群聊）吗？

---

## 📚 完整文档

- **简单使用指南.md** - 中文简明指南（刚创建）
- **GETTING_STARTED.md** - 完整英文教程
- **QUICK_START.md** - 英文快速入门

---

## 💡 推荐新手使用

**最简单的方法**：
1. 用记事本编辑 `.env` 文件
2. 在 PowerShell 运行：`python -m wechat_bot --env .env`
3. 不使用批处理文件

这样最稳定，不会有任何编码问题！

---

## Git 推送说明

本地已提交（commit 9b228ba），但由于网络问题未推送到 GitHub。

网络恢复后可以运行：
```bash
git push origin main
```

---

**推荐阅读**：`简单使用指南.md`（完整中文说明）

**开始使用**：双击 `setup-wizard.bat` 或用命令行

# Quick Start Guide

## 3 Steps to Get Started

### Step 1: Configure (First Time Only)

Double-click: **`config-wizard.bat`**

Follow the prompts to enter:
- API endpoint (e.g., `https://api.openai.com`)
- API key (e.g., `sk-xxx`)
- Model name (e.g., `gpt-3.5-turbo`)
- Other settings (press Enter for defaults)

### Step 2: Setup WeChat (First Time Only)

1. Press `Win + Ctrl + Enter` to start **Windows Narrator**
2. Login to WeChat (if not logged in)
3. **Wait 5 minutes**
4. Press `Win + Ctrl + Enter` to close Narrator

> This enables WeChat 4.1+ UI Automation. Only needed once.

### Step 3: Start

Choose based on your needs:

#### 🧪 Test Mode (Recommended for First Use)
Double-click: **`快速启动.bat`** (quick-start.bat)
- Will NOT send real messages
- Safe for testing

#### 🚀 Production Mode (Real Sending)
Double-click: **`生产模式启动.bat`** (production-start.bat)
- WILL send real WeChat messages
- Use only after thorough testing

---

## Batch Files Overview

| File | Purpose | When to Use |
|------|---------|-------------|
| `config-wizard.bat` | Interactive setup | First time or reconfigure |
| `快速启动.bat` | Quick test mode | Daily testing |
| `生产模式启动.bat` | Production mode | Real usage after testing |
| `start.bat` | Full check startup | Includes dependency checks |

---

## Console Controls

After starting, you'll see:

```
┌─────────────────────────────────────────────────┐
│ Status: Offline duty | Mode: auto | Idle: 650s  │
├─────────────────────────────────────────────────┤
│ [ ] Pause auto reply                            │
│ (•) Auto detect  ( ) Force online  ( ) Offline  │
├─────────────────────────────────────────────────┤
│ [Daily Summary] [Pending Risks] [Auto Replies]  │
└─────────────────────────────────────────────────┘
```

**Controls:**
- **Pause auto reply**: Check to disable auto-reply
- **Auto detect**: Auto determine online/offline (recommended)
- **Force online**: Never auto-reply
- **Force offline**: Always allow auto-reply

---

## Auto-Reply Conditions

Auto-reply ONLY when ALL conditions met:

- ✅ Computer idle ≥ configured minutes (default 10)
- ✅ Personal message (not group chat)
- ✅ Low risk message (no keywords like "payment", "transfer", etc.)
- ✅ Cooldown period passed (default 10 minutes per contact)
- ✅ "Pause auto reply" NOT checked
- ✅ `DRY_RUN=false` (production mode)

---

## Troubleshooting

### Q: Batch file flashes and closes?

**Solution:**
- Right-click → "Run as administrator"
- Or run from PowerShell: `.\start.bat`

### Q: "Python not found"?

**Solution:**
1. Install Python 3.9+: https://www.python.org/downloads/
2. Check "Add Python to PATH" during installation

### Q: Not auto-replying?

**Check:**
- [ ] Idle time enough? (default 10 minutes)
- [ ] Personal message? (not group chat)
- [ ] Low risk message? (no "payment", "transfer" keywords)
- [ ] `DRY_RUN=false`? (test mode doesn't send)
- [ ] "Pause auto reply" checked?

### Q: "WeChat UI Automation unavailable"?

**Solution:** Follow Step 2 again (Narrator for 5 minutes)

---

## Safety Tips

⚠️ **Always test with `DRY_RUN=true` first**

⚠️ **`.env` file contains API key - keep it secret**

⚠️ **Production mode sends real messages - use carefully**

⚠️ **Test with test contacts first**

---

## More Documentation

- 📘 **GETTING_STARTED.md** - Detailed tutorial (English)
- 📙 **一键启动说明.md** - Quick guide (Chinese)
- 📗 **README.md** - Project overview

---

**Enjoy!** 🎉

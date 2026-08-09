# ⚡ Prompt Distiller

<p align="center">
  <img src="https://img.shields.io/badge/Python-3.11+-3776AB?style=for-the-badge&logo=python&logoColor=white" alt="Python Version" />
  <img src="https://img.shields.io/badge/FastAPI-0.110+-009688?style=for-the-badge&logo=fastapi&logoColor=white" alt="FastAPI" />
  <img src="https://img.shields.io/badge/MCP-Server-4682B4?style=for-the-badge" alt="MCP Server" />
  <img src="https://img.shields.io/badge/Local%20AI-Qwen%2035B%20%7C%2027B-6f42c1?style=for-the-badge" alt="Local AI" />
  <img src="https://img.shields.io/badge/License-MIT-green?style=for-the-badge" alt="License" />
</p>

> **A practical local helper tool that cleans up voice dictation and long-winded prompts in Russian and English before sending them to AI agents.**

---

## 💡 What This Actually Does

When using voice dictation or typing out thoughts quickly, prompts often come out messy:
* Speech stutters and vocal filler (*"э-э"*, *"короче"*, *"типа"*, *"ну"*, *"um"*, *"uh"*, *"you know"*).
* Spoken formatting commands like *"новая строка"* or *"абзац"*.
* Long, rambling sentences in Russian that take up extra tokens in English-optimized models.

**Prompt Distiller** sits between your voice dictation (or keyboard) and your AI agents (Antigravity, OpenCode, Kilocode, Hermes). 

It takes raw speech or written text, cleans out the noise, translates Russian requests into clear English instructions, and types the result directly into your active window.

> ℹ️ **Supported Languages:** Currently tuned for **Russian** and **English** inputs.

---

## 🇷🇺 Описание на русском языке

**Prompt Distiller** — это локальный инструмент и межпрограммный шлюз, который очищает голосовую диктовку и длинные «сырые» промпты (на русском и английском) перед их отправкой в ИИ-агенты (**Antigravity**, **OpenCode**, **Kilocode**, **Hermes**).

### Зачем это нужно?
Когда вы диктуете голосом через распознавание речи (Whisper) или быстро пишете мысли, промпты получаются шумными:
* Паразиты речи и междометия (*«э-э»*, *«короче»*, *«типа»*, *«ну»*, *«в общем»*).
* Устные команды разметки (*«новая строка»*, *«абзац»*).
* Длинные формулировки на русском языке, которые занимают лишний контекст у англоязычных моделей.

### Как это работает:
1. Вы нажимаете **`Shift+F4`** и надиктовываете задачу в микрофон.
2. Локальный Whisper распознает голос в текст.
3. **Prompt Distiller** пропускает текст через локальную модель (**Qwen 3.6 35B / 27B** на порту 1235), удаляет мусор и переводит в четкую инструкцию на английском.
4. Готовый промпт автоматически вставляется в активное окно редактора без автоотправки.


---

## 🛠️ Real-Life Example

### What you dictate into the mic (Russian):
> *"Слушай короче, у меня тут Docker контейнер на хосте вылетает с ошибкой exit code 137 при сборке, видимо памяти не хватает. Посмотри в docker-compose.yml и скажи как поднять лимиты по шагам, новая строка и ещё проверь swap."*

### What Prompt Distiller types into your active window (English):
> *"Troubleshoot Docker container crashing with exit code 137 (OOM) during build. Provide step-by-step instructions to increase memory limits in docker-compose.yml and verify host swap configuration."*

* **Result:** No speech fillers, clear technical constraints, and a direct prompt ready for your AI agent to execute.

---

## 📐 How It Works

```
┌───────────────────────────┐
│  Shift+F4 Keybind (Mic)   │
└─────────────┬─────────────┘
              │
              ▼
┌───────────────────────────┐
│   pw-record (PipeWire)    │ ──► /tmp/dictate_distill.wav
└─────────────┬─────────────┘
              │
              ▼
┌───────────────────────────┐
│  Wyoming Faster-Whisper   │ ──► Raw Transcript ("Слушай короче, контейнер...")
└─────────────┬─────────────┘
              │
              ▼
┌───────────────────────────┐
│  Prompt Distiller Engine  │ ──► Local Qwen 3.6 35B / 27B (Port 1235)
└─────────────┬─────────────┘
              │
              ▼
┌───────────────────────────┐
│ wtype / xdotool Injector  │ ──► Injects clean English prompt into active window!
└───────────────────────────┘     (Antigravity / Hermes / OpenCode / Kilocode)
```

---

## 🛠️ Desktop Setup

### Arch Linux + Hyprland (Wayland)

1. **Install System Dependencies:**
   ```bash
   sudo pacman -S pipewire wireplumber wtype libnotify
   ```

2. **Configure Keybind (`~/.config/hypr/hyprland.conf`):**
   ```ini
   # F4 = Plain raw dictation
   bind = , F4, exec, /path/to/dictation/dictate.py

   # Shift+F4 = Distilled AI Prompt Dictation
   bind = SHIFT, F4, exec, /path/to/prompt-distiller/scripts/dictate_distill.py
   ```

---

### Ubuntu + GNOME Desktop (X11 / Wayland)

1. **Install System Dependencies:**
   ```bash
   sudo apt update && sudo apt install -y \
       python3-venv python3-pip pipewire wireplumber wtype xdotool libnotify-bin git
   ```

2. **Add User to Audio Group:**
   ```bash
   sudo usermod -aG audio $USER
   ```

3. **Configure Custom Shortcut (`Shift + F4`):**
   - Open **Settings $\rightarrow$ Keyboard $\rightarrow$ Custom Shortcuts**
   - **Name:** `Distilled AI Dictation`
   - **Command:** `/path/to/prompt-distiller/scripts/dictate_distill.py`
   - **Shortcut:** `Shift + F4`

---

## 🔌 Agent Integration (MCP)

Prompt Distiller includes a standard Model Context Protocol (MCP) server at `app/mcp_server.py`.

### 1. Google Antigravity (`~/.gemini/config/mcp_config.json`)
```json
{
  "mcpServers": {
    "prompt-distiller": {
      "command": "/path/to/prompt-distiller/app/mcp_server.py"
    }
  }
}
```

### 2. OpenCode (`~/.opencode/opencode.json`)
```json
"mcp": {
  "prompt-distiller": {
    "command": ["/path/to/prompt-distiller/app/mcp_server.py"],
    "enabled": true,
    "type": "local"
  }
}
```

### 3. Kilocode (`~/.kilocode/mcp.json`)
```json
{
  "mcpServers": {
    "prompt-distiller": {
      "command": "/path/to/prompt-distiller/app/mcp_server.py"
    }
  }
}
```

### 4. Hermes Agent (`~/.hermes/config.yaml`)
```yaml
mcp_servers:
  prompt-distiller:
    command: /path/to/prompt-distiller/app/mcp_server.py
```

---

## ⚙️ Configuration (`config.yaml`)

```yaml
server:
  host: "0.0.0.0"
  port: 8008

models:
  provider: "local"
  api_base: "http://127.0.0.1:1235/v1"                 # Port where local Qwen server or Ollama runs
  distillation_model: "qwen3.6-35b-a3b-mtp@iq2_m"      # Or qwen3.6-27b@q3_k_s
  execution_model: "qwen3.6-35b-a3b-mtp@iq2_m"

distillation:
  translate_to_english_for_reasoning: true
  default_output_language: "ru"
```

---

## 🗑️ Uninstallation Guide

### 1. Remove Desktop Keybind
* **Hyprland:** Remove the `SHIFT, F4` line from `~/.config/hypr/hyprland.conf`.
* **GNOME:** Delete the custom shortcut in **Settings $\rightarrow$ Keyboard**.

### 2. Remove Agent MCP Registrations
Delete the `"prompt-distiller"` entry from your agent config file (`mcp_config.json`, `opencode.json`, `mcp.json`, or `config.yaml`).

### 3. Remove Project Files
```bash
rm -rf /path/to/prompt-distiller
rm -f /tmp/dictate_distill_recording.pid /tmp/dictate_distill.wav
```

---

## 📜 License

Distributed under the MIT License. See `LICENSE` for details.

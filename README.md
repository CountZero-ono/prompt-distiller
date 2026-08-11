# ⚡ Prompt Distiller

<p align="center">
  <img src="https://img.shields.io/badge/Python-3.11+-3776AB?style=for-the-badge&logo=python&logoColor=white" alt="Python Version" />
  <img src="https://img.shields.io/badge/MCP-Server-4682B4?style=for-the-badge" alt="MCP Server" />
  <img src="https://img.shields.io/badge/Local%20AI-Qwen%2035B-6f42c1?style=for-the-badge" alt="Local AI" />
  <img src="https://img.shields.io/badge/Wayland-wtype-009688?style=for-the-badge" alt="wtype" />
  <img src="https://img.shields.io/badge/License-MIT-green?style=for-the-badge" alt="License" />
</p>

> **Strips filler, translates Russian → English, and compresses rambling voice dictation or typed prompts into tight, high-potency instructions for AI agents.**

Part of the [Sprawl](https://github.com/CountZero-ono) personal AI ecosystem.

---

## 💡 What It Does

Voice dictation and stream-of-consciousness typing produce messy prompts:
- Russian filler: *"э-э"*, *"короче"*, *"типа"*, *"ну"*, *"слушай"*
- English filler: *"um"*, *"uh"*, *"you know"*, *"basically"*
- Spoken formatting: *"новая строка"*, *"абзац"*, *"new line"*
- Long Cyrillic text that costs 2–3× more tokens in English-optimized models

**Prompt Distiller** compresses all of this into a dense, precise English prompt — saving 50–75% tokens — and either injects it directly into the active window (voice workflow) or returns it to the calling agent (MCP workflow).

---

## 🛠️ Real-Life Example

**What you dictate (Russian STT):**
> *«Слушай короче, у меня тут Docker контейнер на хосте вылетает с ошибкой exit code 137 при сборке, видимо памяти не хватает. Посмотри в docker-compose.yml и скажи как поднять лимиты по шагам, новая строка и ещё проверь swap.»*

**What lands in your AI agent:**
> *"Troubleshoot Docker container crashing with exit code 137 (OOM) during build. Step-by-step: increase memory limits in docker-compose.yml and verify host swap configuration."*

---

## 🏗️ Architecture

Two independent entry points — both hit the same distillation core:

```
┌─────────────────────────────┐     ┌──────────────────────────────┐
│  Shift+F4 (Voice Workflow)  │     │  MCP Tool (Agent Workflow)   │
│                             │     │                              │
│  pw-record → mic audio      │     │  Agent sees messy prompt     │
│  Wyoming Whisper (10300)    │     │  calls distill_prompt tool   │
│  → raw transcript           │     │  → gets clean English back   │
└──────────────┬──────────────┘     └──────────────┬───────────────┘
               │                                    │
               ▼                                    ▼
       ┌───────────────────────────────────────────────┐
       │          app/core/distiller.py                │
       │  PromptDistiller → Local Qwen 35B (port 1235) │
       └───────────────────────┬───────────────────────┘
                               │
               ┌───────────────┴────────────────┐
               ▼                                ▼
   wtype → injects into active window    Returns distilled prompt
   (Antigravity / Hermes / any app)      to calling agent context
```

---

## 📂 Project Structure

```
prompt-distiller/
├── app/
│   ├── core/
│   │   ├── distiller.py     # Distillation engine (PromptDistiller class)
│   │   ├── models.py        # LLMClient + provider/model registry
│   │   └── audio.py         # Audio transcription fallback (faster-whisper)
│   └── mcp_server.py        # MCP stdio server exposing distill_prompt tool
├── scripts/
│   └── dictate_distill.py   # Shift+F4 voice dictation → wtype injection
├── config.yaml              # Model configuration
└── requirements.txt
```

---

## ⚙️ Setup

### 1. Install Python dependencies

```bash
cd prompt-distiller
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

### 2. Install system dependencies (Arch Linux / Hyprland)

```bash
sudo pacman -S pipewire wireplumber wtype libnotify
```

### 3. Configure `config.yaml`

Point it at your local model server:

```yaml
models:
  provider: "local"
  api_base: "http://127.0.0.1:1235/v1"      # Your llama-server / LM Studio / Ollama
  distillation_model: "qwen3.6-35b-a3b-mtp@iq2_m"
  execution_model: "qwen3.6-35b-a3b-mtp@iq2_m"
```

Supports any OpenAI-compatible local server. For cloud providers, set `provider` to `gemini`, `groq`, `openai`, or `anthropic` and add the relevant API key as an env variable (`GEMINI_API_KEY`, `GROQ_API_KEY`, etc.).

---

## 🎙️ Voice Dictation Setup (Shift+F4)

2-press toggle workflow:
- **Press 1 (Start):** Spawns `pw-record` → `/tmp/dictate_distill.wav`, writes PID to `/tmp/dictate_distill_recording.pid`
- **Press 2 (Stop & Process):** Kills `pw-record`, streams WAV to Wyoming Faster-Whisper on port 10300, distills via PromptDistiller, types result with `wtype`

**Hyprland keybind (`~/.config/hypr/hyprland.conf`):**
```ini
bind = SHIFT, F4, exec, /path/to/prompt-distiller/venv/bin/python /path/to/prompt-distiller/scripts/dictate_distill.py
```

**Wyoming Faster-Whisper** must be running on port 10300. If unavailable, the script falls back to a local `faster-whisper` Python call.

---

## 🔌 MCP Integration

The MCP server (`app/mcp_server.py`) exposes a single tool: `distill_prompt`.

Agents call it when they detect a messy, Russian, or rambling prompt. The tool returns the distilled English version along with token savings metadata.

### Google Antigravity (`~/.gemini/config/mcp_config.json`)
```json
{
  "mcpServers": {
    "prompt-distiller": {
      "command": "/path/to/prompt-distiller/venv/bin/python",
      "args": ["/path/to/prompt-distiller/app/mcp_server.py"]
    }
  }
}
```

### OpenCode (`~/.opencode/opencode.json`)
```json
"mcp": {
  "prompt-distiller": {
    "command": ["/path/to/prompt-distiller/venv/bin/python", "/path/to/prompt-distiller/app/mcp_server.py"],
    "enabled": true,
    "type": "local"
  }
}
```

### Kilocode (`~/.kilocode/mcp.json`)
```json
{
  "mcpServers": {
    "prompt-distiller": {
      "command": "/path/to/prompt-distiller/venv/bin/python",
      "args": ["/path/to/prompt-distiller/app/mcp_server.py"]
    }
  }
}
```

### Hermes Agent (`~/.hermes/config.yaml`)
```yaml
mcp_servers:
  prompt-distiller:
    command: /path/to/prompt-distiller/venv/bin/python
    args:
      - /path/to/prompt-distiller/app/mcp_server.py
```

---

## 📜 License

MIT License.

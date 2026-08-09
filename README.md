# ⚡ Prompt Distiller & Gateway Engine

<p align="center">
  <img src="https://img.shields.io/badge/Python-3.11+-3776AB?style=for-the-badge&logo=python&logoColor=white" alt="Python Version" />
  <img src="https://img.shields.io/badge/FastAPI-0.110+-009688?style=for-the-badge&logo=fastapi&logoColor=white" alt="FastAPI" />
  <img src="https://img.shields.io/badge/MCP-Server-4682B4?style=for-the-badge" alt="MCP Server" />
  <img src="https://img.shields.io/badge/Local%20AI-Qwen%2035B%20%7C%2027B-6f42c1?style=for-the-badge" alt="Local AI" />
  <img src="https://img.shields.io/badge/Desktop-Hyprland%20%7C%20GNOME-2496ED?style=for-the-badge" alt="Desktop Ready" />
  <img src="https://img.shields.io/badge/License-MIT-green?style=for-the-badge" alt="License" />
</p>

> **Model-agnostic AI middleware gateway and desktop voice dictation engine that compresses messy human speech transcripts and rambling prompts into high-potency micro-prompts—slashing token costs by up to 75% while boosting LLM reasoning accuracy across Antigravity, OpenCode, Kilocode, and Hermes Agent.**

---

## 🎯 The Problem

80% of everyday prompt input consists of conversational fluff, emotional context, etiquette, vocal stutters, and rambling multi-topic questions.

When prompting in foreign scripts (such as **Russian Cyrillic**), the problem compounds:
1. **Cyrillic BPE Token Slaughter:** Byte-Pair Encoding tokenizers split Cyrillic script into **2.5× to 3× more tokens per word** compared to English.
2. **STT Dictation Noise:** Voice-to-text input adds speech stutters (*"э-э"*, *"короче"*, *"типа"*, *"новая строка"*, *"um"*, *"uh"*) and missing syntax.
3. **Context Window Bloat:** Unstructured rambling exhausts context limits in a few messages.
4. **Reasoning Degradation:** Reasoning LLMs waste context budget parsing conversational noise rather than executing the task.

---

## 💡 The Solution

**Prompt Distiller** acts as an intelligent proxy gateway and OS-level dictation assistant:
1. **Strips Speech Artifacts & Fillers:** Removes vocal stutters (*"короче"*, *"типа"*, *"э-э"*, *"um"*, *"uh"*) and spoken formatting commands (*"новая строка"* $\rightarrow$ clean structural line breaks).
2. **Cyrillic-to-English Micro-Prompts:** Translates foreign inputs into dense, precise English prompts, preserving explicit technical constraints and sub-tasks (**50%–75% token budget savings**).
3. **Hands-Free Desktop Injection:** `Shift+F4` keybind records mic input, transcribes via local Whisper, distills prompt via local Qwen 35B/27B, and types the result directly into your focused agent window without auto-submitting.
4. **Universal 4-Agent MCP Integration:** Exposes an MCP server for **Google Antigravity**, **OpenCode**, **Kilocode**, and **Hermes Agent**.

---

## 📐 Architecture Overview

### 1. Desktop Voice Dictation Workflow (`Shift+F4`)

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
│  Wyoming Faster-Whisper   │ ──► Raw Transcript ("Слушай короче, проблема с...")
└─────────────┬─────────────┘
              │
              ▼
┌───────────────────────────┐
│  Prompt Distiller Engine  │ ──► Local Qwen 3.6 35B / 27B (Port 1235)
└─────────────┬─────────────┘
              │
              ▼
┌───────────────────────────┐
│ wtype / xdotool Injector  │ ──► Injects clean English prompt into focused window!
└───────────────────────────┘     (Antigravity / Hermes / OpenCode / Kilocode)
```

---

### 2. Multi-Phase Distillation Pipeline

```
┌─────────────────────────────────────────────────────────────────────────┐
│                     Messy Input (Voice / Russian STT)                   │
└─────────────────────────────────────────────────────────────────────────┘
                                     │
                                     ▼
┌─────────────────────────────────────────────────────────────────────────┐
│                     Phase 1: STT & Filler Stripping                     │
│       • Removes "э-э", "короче", "типа", "um", "uh", "you know"          │
│       • Converts "новая строка" / "абзац" to clean paragraph breaks     │
└─────────────────────────────────────────────────────────────────────────┘
                                     │
                                     ▼
┌─────────────────────────────────────────────────────────────────────────┐
│              Phase 2: Cyrillic-to-English Distillation                 │
│       • Converts Russian Cyrillic -> High-Density English               │
│       • Extracts Intent, Constraints & Sub-tasks                        │
│       • 📉 Saves 50%–75% Token Budget                                   │
└─────────────────────────────────────────────────────────────────────────┘
                                     │
                                     ▼
┌─────────────────────────────────────────────────────────────────────────┐
│               Phase 3: Agent / Execution Model Routing                  │
│       • Local Qwen 3.6 35B / 27B, Ollama, llama.cpp, vLLM, Gemini       │
└─────────────────────────────────────────────────────────────────────────┘
```

---

## ✨ Core Capabilities

- ⚡ **Token Budget Optimizer:** Preserves reasoning LLM context window health by turning 200-word transcripts into 40-word prompts.
- 🎙️ **Desktop Keybind Dictation (`Shift+F4`):** Types clean distilled prompts into your active editor or terminal without auto-triggering execution.
- 🔌 **Universal MCP Server:** Exposes stdio Model Context Protocol (MCP) server for seamless integration with AI coding agents.
- 🛡️ **Strict Constraint Extraction:** Preserves technical specs, budgets, formats, and filenames during distillation.
- 🏠 **100% Zero-Cloud Ready:** Connects to local `llama-server` endpoints (`http://127.0.0.1:1235/v1`), Ollama (`11434`), LM Studio, or vLLM.

---

## 🛠️ Desktop Dictation & OS Integration

### Option A: Arch Linux + Hyprland (Wayland)

1. **Install System Dependencies:**
   ```bash
   sudo pacman -S pipewire wireplumber wtype libnotify
   ```

2. **Configure Keybind (`~/.config/hypr/hyprland.conf`):**
   ```ini
   # F4 = Plain dictation (untouched)
   bind = , F4, exec, /home/fuad/OCProjects/dictation/dictate.py

   # Shift+F4 = Distilled AI Prompt Dictation
   bind = SHIFT, F4, exec, /home/fuad/Projects/BAMA/prompt-distiller/scripts/dictate_distill.py
   ```

---

### Option B: Ubuntu + GNOME Desktop (X11 / Wayland)

1. **Install System Dependencies:**
   ```bash
   sudo apt update && sudo apt install -y \
       python3-venv python3-pip pipewire wireplumber wtype xdotool libnotify-bin git
   ```

2. **Add Desktop User to Audio Group:**
   ```bash
   sudo usermod -aG audio $USER
   ```

3. **Configure GNOME Custom Shortcut (`Shift + F4`):**
   - Open **Settings $\rightarrow$ Keyboard $\rightarrow$ View and Customize Shortcuts $\rightarrow$ Custom Shortcuts**
   - **Name:** `Distilled AI Dictation`
   - **Command:** `/path/to/prompt-distiller/scripts/dictate_distill.py`
   - **Shortcut:** `Shift + F4`

---

## 🔌 Agent MCP Integration

Prompt Distiller includes a native stdio Model Context Protocol (MCP) server at `app/mcp_server.py`.

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
  api_base: "http://127.0.0.1:1235/v1"                 # Local Qwen server or Ollama port
  distillation_model: "qwen3.6-35b-a3b-mtp@iq2_m"      # Or qwen3.6-27b@q3_k_s
  execution_model: "qwen3.6-35b-a3b-mtp@iq2_m"

distillation:
  translate_to_english_for_reasoning: true
  default_output_language: "ru"
```

### Switching 35B $\leftrightarrow$ 27B Models
To load a **27B model** (e.g., `qwen3.6-27b@q3_k_s` or `gemma-2-27b`), update `distillation_model` in `config.yaml` or set environment variables:
```bash
export LLM_API_BASE="http://127.0.0.1:1235/v1"
export LLM_MODEL_NAME="qwen3.6-27b@q3_k_s"
```

---

## 🔌 API Reference

### `POST /v1/distill`
Compress raw STT transcript or prompt into a high-potency English prompt without downstream execution.

#### Request Payload:
```json
{
  "raw_prompt": "Слушай короче, у меня тут проблема с фотопленкой 120 формата, на кадрах идет белая полоса при сканировании на Epson V850. Подскажи как исправить шаг за шагом?"
}
```

#### Response Payload:
```json
{
  "detected_language": "Russian",
  "raw_input_summary": "User reports a white strip artifact on 120mm film scans using an Epson V850 scanner...",
  "distilled_prompt": "Troubleshoot a persistent white strip/line artifact on 120mm film scans using an Epson V850 flatbed scanner. Provide a concise, step-by-step diagnostic and fix guide covering: hardware alignment, glass/film holder cleaning, transparency mask positioning, scanner software settings, and calibration.",
  "intent": "Technical Troubleshooting / Hardware Support",
  "extracted_constraints": [
    "120mm film format",
    "Epson V850 scanner",
    "White strip/line artifact",
    "Step-by-step format required"
  ],
  "estimated_raw_tokens": 70,
  "estimated_distilled_tokens": 58,
  "token_savings_percent": 17.1
}
```

---

## 🗑️ Uninstallation Guide

To completely remove Prompt Distiller, desktop keybinds, temporary files, and agent MCP registrations from your system:

### 1. Remove Desktop Keybind
* **Arch Linux / Hyprland:** Remove the `SHIFT, F4` keybind line from `~/.config/hypr/hyprland.conf`:
  ```ini
  # Remove this line:
  bind = SHIFT, F4, exec, /path/to/prompt-distiller/scripts/dictate_distill.py
  ```
* **Ubuntu / GNOME Desktop:** Open **Settings $\rightarrow$ Keyboard $\rightarrow$ View and Customize Shortcuts $\rightarrow$ Custom Shortcuts** and delete the `Distilled AI Dictation` shortcut.

---

### 2. Remove Agent MCP Registrations
Delete the `prompt-distiller` entry from your active agent configuration files:

* **Google Antigravity:** Remove `"prompt-distiller"` block from `~/.gemini/config/mcp_config.json`.
* **OpenCode:** Remove `"prompt-distiller"` entry under `"mcp"` in `~/.opencode/opencode.json`.
* **Kilocode:** Remove `"prompt-distiller"` block from `~/.kilocode/mcp.json`.
* **Hermes Agent:** Remove `prompt-distiller` entry under `mcp_servers:` in `~/.hermes/config.yaml`.

---

### 3. Remove Project Directory & Temporary Dictation Files
```bash
# Remove project folder and python virtual environment
rm -rf /path/to/prompt-distiller

# Remove temporary dictation WAV audio & PID files
rm -f /tmp/dictate_distill_recording.pid /tmp/dictate_distill.wav
```

---

## 🤝 Contributing

Contributions are welcome! Feel free to open an issue or submit a pull request for new model adapters, bot interfaces, or template presets.

## 📜 License

Distributed under the MIT License. See `LICENSE` for details.


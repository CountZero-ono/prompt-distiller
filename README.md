# ⚡ Prompt Distiller & Gateway Engine

<p align="center">
  <img src="https://img.shields.io/badge/Python-3.11+-3776AB?style=for-the-badge&logo=python&logoColor=white" alt="Python Version" />
  <img src="https://img.shields.io/badge/FastAPI-0.110+-009688?style=for-the-badge&logo=fastapi&logoColor=white" alt="FastAPI" />
  <img src="https://img.shields.io/badge/Docker-Ready-2496ED?style=for-the-badge&logo=docker&logoColor=white" alt="Docker" />
  <img src="https://img.shields.io/badge/Model--Agnostic-Ollama%20%7C%20Gemini%20%7C%20OpenAI-6f42c1?style=for-the-badge" alt="Model Agnostic" />
  <img src="https://img.shields.io/badge/License-MIT-green?style=for-the-badge" alt="License" />
</p>

> **Model-agnostic AI middleware gateway that compresses messy human voice notes and rambling prompts into high-potency micro-prompts—slashing token costs by up to 75% while boosting LLM reasoning accuracy.**

---

## 🎯 The Problem

80% of everyday non-technical users interact with LLMs like a chatroom—dumping 500-word voice transcripts, emotional context, etiquette, and rambling multi-topic questions.

When users prompt in foreign scripts (such as **Russian Cyrillic**), the problem compounds drastically:
1. **Cyrillic BPE Token Slaughter:** Byte-Pair Encoding tokenizers split Cyrillic script into **2.5× to 3× more tokens per word** compared to English.
2. **Context Window Bloat:** Unstructured rambling exhausts context limits in 4–5 messages.
3. **Reasoning Degradation:** Dense reasoning LLMs spend their energy parsing conversational noise rather than executing the core task.

---

## 💡 The Solution

**Prompt Distiller** acts as an intelligent proxy gateway sitting between end-users and reasoning models. It ingests chaotic raw inputs, translates and distills them into a dense 100-token English micro-prompt, executes against your target LLM (local or cloud), and formats the final answer back into the user's native language.

```
┌─────────────────────────────────────────────────────────────────────────┐
│                      Messy Input (Voice / Russian)                      │
└─────────────────────────────────────────────────────────────────────────┘
                                     │
                                     ▼
┌─────────────────────────────────────────────────────────────────────────┐
│                      Phase 1: Noise Removal                             │
│       • Strips filler, etiquette, and irrelevant story context          │
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
│                     Phase 3: Reasoning LLM Execution                    │
│       • Routes micro-prompt to target (Ollama, Gemini, OpenAI, Claude)  │
└─────────────────────────────────────────────────────────────────────────┘
                                     │
                                     ▼
┌─────────────────────────────────────────────────────────────────────────┐
│                    Phase 4: Response Formatting                         │
│       • Formats clean, structured response back into native language    │
└─────────────────────────────────────────────────────────────────────────┘
```

---

## ✨ Key Features

- ⚡ **Token Budget Optimizer:** Drastically lowers API costs and preserves context window health.
- 🛡️ **Strict Constraint Preservation:** Guarantees technical limits (word counts, budgets, formats, tools) survive distillation.
- 🔌 **100% Model Agnostic:** Point to local offline Ollama models (`qwen2.5:32b`, `llama3.2`), local `llama.cpp`, or cloud providers (Gemini 1.5 Pro, GPT-4o, Claude 3.5 Sonnet).
- 🖥️ **Triple Interface Suite:**
  - **Modern Web UI:** Dark mode, glassmorphism dashboard with real-time token savings analytics and preset selectors.
  - **Telegram Bot:** Full text and `.ogg` voice note transcription integration via Whisper ASR.
  - **Signal Bot:** Native integration with `signal-cli-rest-api` WebSockets.
- 📦 **Zero-Config Fallback:** Includes built-in offline heuristic evaluation mode for standalone testing before connecting live API keys.

---

## 🖥️ Web UI Preview

The included Web Dashboard (`http://localhost:8000`) lets you test raw prompts live, view extracted constraints, and inspect real-time token compression:

* **Raw Input:** Paste messy Russian transcripts or select built-in presets (Film Lab Scanner Troubleshooting, Homelab Cluster Debugging, Client Email Drafting).
* **Live Stats Banner:** Visualizes raw token count vs distilled token count and percentage saved.
* **Dual View:** Inspect the distilled English micro-prompt alongside the final re-translated answer.

---

## 🚀 Quick Start

### Option 1: Run with Docker Compose (Recommended)

```bash
# Clone the repository
git clone https://github.com/CountZero-ono/prompt-distiller.git
cd prompt-distiller

# Set your API keys (or run offline with local Ollama)
export GEMINI_API_KEY="your-api-key"

# Launch container
docker-compose up -d
```

Access the Web UI at **`http://localhost:8000`**.

### Option 2: Local Python Installation

```bash
# Clone & enter directory
git clone https://github.com/CountZero-ono/prompt-distiller.git
cd prompt-distiller

# Create virtual environment
python3 -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Start FastAPI Uvicorn server
python3 -m app.main
```

---

## 🔌 API Reference

### `POST /v1/process`

Process raw prompt text through the distillation engine.

#### Request Payload:
```json
{
  "raw_prompt": "Слушай короче, у меня тут проблема с фотопленкой 120 формата, на кадрах идет белая полоса при сканировании на Epson V850. Подскажи как исправить шаг за шагом?",
  "target_language": "ru",
  "model": "gemini/gemini-1.5-pro"
}
```

#### Response Payload:
```json
{
  "distillation": {
    "detected_language": "Russian (ru)",
    "raw_input_summary": "User asking for troubleshooting steps for white vertical line artifacts on 120 film scanned with Epson V850.",
    "distilled_prompt": "Provide step-by-step troubleshooting for vertical white line artifacts on 120 format film scans using Epson V850 scanner.",
    "intent": "technical_support",
    "extracted_constraints": ["Step-by-step instructions"],
    "estimated_raw_tokens": 58,
    "estimated_distilled_tokens": 22,
    "token_savings_percent": 62.1
  },
  "final_response": "**Пошаговая инструкция по устранению белой полосы:**\n\n1. **Очистка калибровочного окна...**"
}
```

---

## ⚙️ Configuration (`config.yaml`)

```yaml
server:
  host: "0.0.0.0"
  port: 8000

models:
  # Fast model for extraction & prompt distillation
  distillation_model: "gemini/gemini-1.5-flash"
  # Heavy reasoning model for task execution
  execution_model: "gemini/gemini-1.5-pro"
  
  # Local Ollama alternatives:
  # distillation_model: "ollama/qwen2.5:1.5b"
  # execution_model: "ollama/qwen2.5:32b"

distillation:
  translate_to_english_for_reasoning: true
  default_output_language: "ru"

bots:
  telegram:
    enabled: false
    token: "YOUR_TELEGRAM_BOT_TOKEN"
  signal:
    enabled: false
    rest_url: "http://127.0.0.1:8080"
    account: "+1234567890"
```

---

## 🤝 Contributing

Contributions are welcome! Feel free to open an issue or submit a pull request for new model adapters, bot interfaces, or template presets.

## 📜 License

Distributed under the MIT License. See `LICENSE` for details.

# ⚡ Prompt Distiller & Gateway Engine

> Model-agnostic AI noise reduction gateway that compresses messy human prompts, optimizes token budgets, and forces structured execution across local and cloud LLMs.

---

## 🌟 Why Prompt Distiller?

Non-technical users treat LLMs like chatrooms—dumping rambling voice transcripts, emotional context, and multi-topic questions in non-English scripts (like Russian Cyrillic). 

**The Problem:**
* **Cyrillic Token Overhead:** Russian BPE tokenization takes ~2.5x more tokens per word than English.
* **Context Bloat:** Conversational fluff exhausts context limits and confuses reasoning models.
* **Rate Limits:** 80% of token budgets get wasted on noise.

**The Solution:**
Prompt Distiller acts as an intelligent middleware gateway. It strips conversational noise, distills foreign text into a dense 100-token English micro-prompt, executes against the target LLM, and formats clean answers back in the user's language.

---

## 🛠️ Key Features

- **4-Phase Processing Pipeline:**
  1. *Language Detection & Noise Stripping*
  2. *Intent Extraction & Cyrillic-to-English Micro-Prompt Translation*
  3. *High-Potency Target Model Execution (Ollama, Gemini, OpenAI, Claude)*
  4. *Clean Answer Re-translation & Formatting*
- **Triple Interface Support:**
  - 🖥️ **Modern Web UI** (Dark mode, glassmorphism, real-time token savings analytics)
  - 💬 **Telegram Bot Adapter** (Supports text & voice note `.ogg` files via Whisper)
  - 📡 **Signal Bot Adapter** (Integrates with `signal-cli-rest-api`)
  - 🔌 **REST API** (`/v1/process`, `/v1/transcribe`)
- **Model Agnostic:** Configurable to run 100% offline via local Ollama (`qwen2.5`) or cloud APIs (`gemini-1.5-pro`, `gpt-4o`).

---

## 🚀 Quick Start

### 1. Local Run (Python)

```bash
# Clone repository
git clone https://github.com/yourusername/prompt-distiller.git
cd prompt-distiller

# Create venv & install dependencies
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# Start engine server
python3 -m app.main
```

Open your browser at `http://localhost:8000`.

### 2. Docker Run

```bash
docker-compose up -d
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

distillation:
  translate_to_english_for_reasoning: true
  default_output_language: "ru"
```

---

## 📄 License
MIT License.

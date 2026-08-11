# Prompt Distiller — Agent Instructions

## Overview
This repository is the **Prompt Distiller**, a lightweight middleware tool that compresses messy human prompts and STT voice dictations (Russian, English, or mixed) into high-potency micro-prompts for reasoning LLMs.

## Architecture — Two Entry Points

### 1. Voice Dictation (`scripts/dictate_distill.py`)
- Triggered by `Shift+F4` keybind in Hyprland
- **Press 1 (Start):** Spawns `pw-record` → `/tmp/dictate_distill.wav`, PID file → `/tmp/dictate_distill_recording.pid`
- **Press 2 (Stop & Process):** Kills `pw-record`, streams WAV to Wyoming Faster-Whisper on `127.0.0.1:10300`, distills raw transcript via `PromptDistiller`, injects result into focused window via `wtype`
- Falls back to direct `PromptDistiller` Python import if HTTP server is unavailable

### 2. MCP Tool (`app/mcp_server.py`)
- Exposes `distill_prompt` tool over stdio JSON-RPC to Antigravity, OpenCode, Kilocode, and Hermes
- Agents call this tool when they detect a messy, rambling, or Russian prompt — agent decides autonomously when to distill
- Works on both STT-dictated and typed text

## Core Modules
- `app/core/distiller.py` — `PromptDistiller` class with `distill_only()` method; shared by both entry points
- `app/core/models.py` — `LLMClient` + `MODEL_REGISTRY`; local-first (port 1235), LiteLLM cloud fallback
- `app/core/audio.py` — Whisper fallback transcription (used only if Wyoming is unavailable)

## Local Model
- **Primary:** Qwen3.6-35B-A3B-MTP@IQ2_M on `http://127.0.0.1:1235/v1`
- **Provider config key:** `"local"` (maps to `custom_local` in the registry)

## What Does NOT Exist Here
- No FastAPI HTTP server
- No web UI
- No Telegram / Signal bots
- No Docker deployment (Dockerfile present but not used)

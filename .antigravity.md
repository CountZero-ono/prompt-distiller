# Prompt Distiller Workspace Agent Instructions

## Overview
This repository contains the **Prompt Distiller & Gateway Engine**, an intelligent middleware gateway that compresses messy human prompts & STT voice dictations (in Russian, English, or mixed) into high-potency micro-prompts for reasoning LLMs.

## Core Integration Points
1. **Local Model Server**: Connects to local Qwen 3.6 35B on `http://127.0.0.1:1235/v1`.
2. **Desktop Voice Dictation**: `Shift+F4` keybind triggers `scripts/dictate_distill.py` using a 2-press toggle workflow:
   - **Press 1 (Start)**: Spawns `pw-record` to record audio to `/tmp/dictate_distill.wav` and creates PID file `/tmp/dictate_distill_recording.pid`.
   - **Press 2 (Stop & Process)**: Sends `SIGINT` to `pw-record`, streams WAV to local Wyoming Faster-Whisper on `127.0.0.1:10300`, distills raw transcript via Prompt Distiller (`http://127.0.0.1:8008/v1/distill`), and injects distilled prompt into focused window via `wtype`.
3. **MCP Tooling (`distill_prompt`)**: Available across Antigravity, OpenCode, Kilocode, and Hermes Agent.
4. **FastAPI Endpoints**: `POST /v1/process` (full response) and `POST /v1/distill` (prompt distillation only).

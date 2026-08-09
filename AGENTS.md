# Prompt Distiller Workspace Agent Instructions

## Overview
This repository contains the **Prompt Distiller & Gateway Engine**, an intelligent middleware gateway that compresses messy human prompts & STT voice dictations (in Russian, English, or mixed) into high-potency micro-prompts for reasoning LLMs.

## Core Integration Points
1. **Local Model Server**: Connects to local Qwen 3.6 35B on `http://127.0.0.1:1235/v1`.
2. **Desktop Voice Dictation**: `Shift+F4` keybind triggers `scripts/dictate_distill.py` (records mic via PipeWire, transcribes via local Wyoming Whisper, distills prompt, types result into active window via `wtype`).
3. **MCP Tooling (`distill_prompt`)**: Available across Antigravity, OpenCode, Kilocode, and Hermes Agent.
4. **FastAPI Endpoints**: `POST /v1/process` (full response) and `POST /v1/distill` (prompt distillation only).

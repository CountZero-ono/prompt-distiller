# Prompt Distiller — Agent Instructions

## Overview
This repository is the **Prompt Distiller**, a lightweight middleware tool that compresses messy human prompts and STT voice dictations (Russian, English, or mixed) into high-potency micro-prompts for reasoning LLMs.

## Architecture

### Voice Dictation (`scripts/dictate_distill.py`)

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

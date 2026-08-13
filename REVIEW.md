# Prompt Distiller – Read-only Review

## Overview
Project at `/home/fuad/Projects/BAMA/prompt-distiller` implements a voice-dictation → distill → inject pipeline for messy Russian/English prompts into high-potency English micro-prompts.

## Files found
- README.md, AGENTS.md, .antigravity.md – descriptions
- app/core/distiller.py – PromptDistiller with distill_only() and full process()
- app/core/models.py – LLMClient with direct HTTP to http://127.0.0.1:1235/v1, LiteLLM fallback, heuristic fallback
- app/core/audio.py – AudioTranscriber with faster-whisper → openai-whisper → static demo fallback
- scripts/dictate_distill.py – Shift+F4 toggle: pw-record → Wyoming Faster-Whisper 10300 → distill → wl-copy + evdev paste
- scripts/evdev_paste.py – sends Ctrl+Shift+V via evdev/uinput
- config.yaml – local provider, api_base http://127.0.0.1:1235/v1, model qwen3.6-35b-a3b-mtp@iq2_m, translate_to_english_for_reasoning true, default_output_language ru
- requirements.txt – litellm>=1.30.0, pyyaml>=6.0.1, httpx>=0.27.0, python-dotenv>=1.0.1, faster-whisper>=1.0.0, openai-whisper>=20231117
- Dockerfile + docker-compose.yml – expose 8008, CMD uvicorn app.main:app
- .gitignore – standard Python ignores

## Issues / inconsistencies

### Missing FastAPI entrypoint
Dockerfile and docker-compose.yml start `uvicorn app.main:app --port 8008`. No `app/main.py` exists. AGENTS.md/.antigravity.md state "No FastAPI HTTP server". `scripts/dictate_distill.py` tries HTTP `http://127.0.0.1:8008/v1/distill` first, then falls back to local import. The primary path always fails.

### Config / model mismatch
config.yaml uses `distillation_model: "qwen3.6-35b-a3b-mtp@iq2_m"`. MODEL_REGISTRY aliases `local` → `custom_local` with defaults `openai/custom-model`. Provider defaults can silently override config.

### Token estimation heuristic
`estimate_tokens` uses len(words)*2.5 for Cyrillic and *1.3 otherwise. Rough word proxy, not real tokenizer counts. Heuristic fallback in LLMClient hard-codes Russian output.

### Audio fallback is static demo
AudioTranscriber.transcribe returns a hard-coded Russian sentence when both whisper engines fail. Will be distilled as real user speech.

### Missing runtime dependencies
dictate_distill.py imports yaml and wyoming.client but requirements.txt lacks wyoming-client and PyYAML is only listed as pyyaml. evdev is used but not declared.

### Hard-coded paths / race conditions
WAYLAND_DISPLAY defaults to wayland-0, XDG_RUNTIME_DIR guessed. wl-copy launched with Popen then sleep 300ms before paste. PID file in /tmp is world-writable.

### Security
wtype fallback builds shell string: subprocess.run(f'wtype "{safe_text}"', shell=True). Injection prone. No timeout on pw-record kill.

### Logging
dbg writes to /tmp/dictate_distill.log with no rotation. logger configured but handlers never attached.

### Docker drift
Base python:3.11-slim, installs ffmpeg but not audio libs needed for pw-record. Copies repo expecting app.main. README says no Docker deployment.

### No tests / tooling
No pytest, pyproject.toml, linting, CI. Empty __init__ files.

## Improvement suggestions
- Decide on server presence: remove Dockerfile/compose and HTTP path, or create app/main.py with FastAPI /v1/distill reusing PromptDistiller.
- Add missing deps: PyYAML, wyoming-client, evdev. Pin versions.
- Replace shell wtype with arg list, avoid shell=True. Prefer wl-copy + paste.
- Make audio fallback explicit, raise or return empty instead of demo transcript.
- Centralize config with pydantic-settings and fail fast.
- Use real token counting via tiktoken or model tokenizer when available.
- Add unit tests for parse_llm_json, estimate_tokens, distill_only with mock LLMClient.
- Clean Dockerfile to match actual entrypoint, multi-stage for heavy whisper deps.
- Add logging configuration and log rotation.

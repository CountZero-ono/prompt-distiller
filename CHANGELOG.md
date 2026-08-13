# Changelog

All notable changes to this project will be documented in this file.

## [Unreleased] - 2026-08-13

### Added
- Added `pydantic` and `pydantic-settings` to ensure strict parsing of `config.yaml`.
- Added `tiktoken` for accurate token estimation instead of heuristic character counting.
- Added `pytest` suite for automated logic validation and regression testing.
- Added `RotatingFileHandler` for proper log management in `~/.cache/prompt_distiller/dictate.log`.

### Changed
- Replaced world-writable `/tmp` files with secure, user-scoped `~/.cache/prompt_distiller/` directories.
- Completely removed dead HTTP/FastAPI server logic, `Dockerfile`, and `docker-compose.yml`.
- Refactored `dictate_distill.py` to directly import local modules for instant execution without network overhead.
- Updated `qwen3.6-35b-a3b-mtp` as the recommended optimal MoE model for unified memory environments (UMA).

### Fixed
- Fixed shell injection vulnerability in `wtype` fallback.
- Fixed race condition where `evdev_paste` would fire before Wayland registered clipboard contents.
- Fixed hard-coded fallback transcript in Whisper audio module.
- Added missing `wyoming-client` and `evdev` to `requirements.txt`.

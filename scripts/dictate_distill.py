#!/usr/bin/env python3
"""
Distilled Dictation Script for Linux / Hyprland.
Captures audio via pw-record, transcribes via local whisper.cpp,
compresses raw STT text into a high-potency English micro-prompt via PromptDistiller,
and types the distilled prompt into the focused window using wtype.

Leaves original dictate.py completely untouched.
Bind to Shift+F4 in Hyprland!
"""

import os
import sys
import signal
import subprocess
import asyncio
import wave
import json
import time
import traceback
import logging
from logging.handlers import RotatingFileHandler

CACHE_DIR = os.path.expanduser("~/.cache/prompt_distiller")
os.makedirs(CACHE_DIR, exist_ok=True)

PID_FILE = os.path.join(CACHE_DIR, "recording.pid")
WAV_FILE = os.path.join(CACHE_DIR, "recording.wav")
LOG_FILE = os.path.join(CACHE_DIR, "dictate.log")

# Setup logging
logger = logging.getLogger("dictate_distill")
logger.setLevel(logging.DEBUG)
handler = RotatingFileHandler(LOG_FILE, maxBytes=5 * 1024 * 1024, backupCount=2)
formatter = logging.Formatter("[%(asctime)s] %(message)s", "%H:%M:%S")
handler.setFormatter(formatter)
logger.addHandler(handler)

def dbg(msg: str):
    print(f"[{time.strftime('%H:%M:%S')}] {msg}", file=sys.stderr)
    logger.debug(msg)

def load_config():
    """Load whisper.cpp paths from config.yaml."""
    import yaml
    config_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "config.yaml")
    if os.path.exists(config_path):
        with open(config_path) as f:
            return yaml.safe_load(f)
    return {}

async def transcribe_audio():
    """
    Streams recorded WAV file to local wyoming-faster-whisper ASR server on port 10300.
    """
    dbg("transcribe_audio: START wyoming stream")
    try:
        from wyoming.client import AsyncTcpClient
        from wyoming.audio import AudioStart, AudioChunk, AudioStop
        from wyoming.asr import Transcribe, Transcript

        client = AsyncTcpClient('127.0.0.1', 10300)
        await client.connect()
        
        await client.write_event(Transcribe().event())
        
        with wave.open(WAV_FILE, 'rb') as wav:
            rate = wav.getframerate()
            width = wav.getsampwidth()
            channels = wav.getnchannels()
            
            await client.write_event(AudioStart(rate=rate, width=width, channels=channels).event())
            
            while True:
                chunk = wav.readframes(4096)
                if not chunk:
                    break
                await client.write_event(AudioChunk(rate=rate, width=width, channels=channels, audio=chunk).event())
                
            await client.write_event(AudioStop().event())
        
        while True:
            event = await client.read_event()
            if event is None:
                break
            if Transcript.is_type(event.type):
                transcript = Transcript.from_event(event)
                dbg(f"transcribe_audio: success (len={len(transcript.text)})")
                return transcript.text
    except Exception as e:
        dbg(f"transcribe_audio: Transcription error: {e}")
    return ""

def distill_prompt(raw_text: str) -> str:
    """
    Sends raw STT text to local PromptDistiller.
    """
    dbg(f"distill_prompt: raw_text len={len(raw_text)}")
    try:
        dbg("distill_prompt: importing PromptDistiller locally")
        sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
        from app.core.distiller import PromptDistiller
        from app.core.config import load_settings

        config_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "config.yaml")
        config = load_settings(config_path)

        distiller = PromptDistiller(config)
        dbg("distill_prompt: calling distill_only...")
        res = asyncio.run(distiller.distill_only(raw_text))
        distilled = res.get("distilled_prompt", raw_text)
        savings = res.get("token_savings_percent", 0)
        dbg(f"distill_prompt: local success, savings={savings}%")
        subprocess.run(["notify-send", "-t", "2500", "⚡ Distilled", f"Saved {savings}% tokens! Typing prompt..."])
        return distilled
    except Exception as ex:
        dbg(f"distill_prompt: offline fallback error ({type(ex).__name__}: {ex})")
        return raw_text

def start_recording():
    dbg("start_recording: START")
    print("Starting distilled recording...")
    subprocess.run(["notify-send", "-t", "2000", "🎙️ Distilled Dictation", "Listening for AI prompt..."])
    dbg("start_recording: launching pw-record...")
    try:
        proc = subprocess.Popen(["pw-record", "--channels=1", "--rate=16000", "--format=s16", WAV_FILE])
        dbg(f"start_recording: pw-record started pid={proc.pid}")
    except FileNotFoundError:
        dbg("start_recording: pw-record binary NOT FOUND")
        raise
    except Exception as e:
        dbg(f"start_recording: pw-record launch failed: {e}")
        raise
    with open(PID_FILE, "w") as f:
        f.write(str(proc.pid))
    dbg(f"start_recording: PID written to {PID_FILE}")
    print("Recording started. Trigger again to stop, distill, and type.")

def stop_recording_and_type():
    dbg("stop_recording_and_type: START")
    print("Stopping recording...")
    if not os.path.exists(PID_FILE):
        dbg(f"stop_recording_and_type: PID_FILE not found at {PID_FILE}, returning")
        return

    with open(PID_FILE, "r") as f:
        pid_str = f.read().strip()
    dbg(f"stop_recording_and_type: read PID={pid_str} from {PID_FILE}")
    pid = int(pid_str)

    os.remove(PID_FILE)
    dbg(f"stop_recording_and_type: removed {PID_FILE}")

    try:
        dbg(f"stop_recording_and_type: sending SIGINT to pid={pid}")
        os.kill(pid, signal.SIGINT)
        time.sleep(0.5)
        dbg("stop_recording_and_type: sleep 0.5s done")
    except ProcessLookupError:
        dbg(f"stop_recording_and_type: ProcessLookupError for pid={pid} (already dead)")
    except Exception as e:
        dbg(f"stop_recording_and_type: kill error: {type(e).__name__}: {e}")

    dbg(f"stop_recording_and_type: checking WAV file {WAV_FILE}")
    if os.path.isfile(WAV_FILE):
        dbg(f"stop_recording_and_type: WAV exists, size={os.path.getsize(WAV_FILE)} bytes")
    else:
        dbg(f"stop_recording_and_type: WAV file MISSING!")

    subprocess.run(["notify-send", "-t", "2000", "⚙️ Processing STT", "Transcribing and distilling prompt..."])
    dbg("stop_recording_and_type: calling transcribe_audio...")
    raw_text = asyncio.run(transcribe_audio())
    raw_text = raw_text.strip()
    dbg(f"stop_recording_and_type: transcribe_audio returned len={len(raw_text)}")

    if raw_text:
        print(f"Raw Transcribed: {raw_text}")
        dbg("stop_recording_and_type: calling distill_prompt...")
        distilled = distill_prompt(raw_text).strip()
        print(f"Distilled Prompt: {distilled}")
        dbg("stop_recording_and_type: running wtype...")

        dbg(f"stop_recording_and_type: typing text (len={len(distilled)})")
        try:
            # Write to temp file
            tmp_clip = os.path.join(CACHE_DIR, "clipboard.txt")
            with open(tmp_clip, "w", encoding="utf-8") as f:
                f.write(distilled)

            # GNOME shortcuts don't pass Wayland env vars, set them explicitly
            env = os.environ.copy()
            env["WAYLAND_DISPLAY"] = env.get("WAYLAND_DISPLAY", "wayland-0")
            env["XDG_RUNTIME_DIR"] = env.get("XDG_RUNTIME_DIR", f"/run/user/{os.getuid()}")

            # Popen with file as stdin — wl-copy forks, Popen returns immediately
            dbg("stop_recording_and_type: running wl-copy...")
            with open(tmp_clip, "rb") as f:
                subprocess.Popen(["wl-copy"], stdin=f, env=env)
            os.remove(tmp_clip)
            dbg("stop_recording_and_type: wl-copy launched, waiting 300ms...")
            time.sleep(0.3)
            dbg("stop_recording_and_type: sending Ctrl+Shift+V via evdev")
            result = subprocess.run(
                [sys.executable, os.path.join(os.path.dirname(os.path.abspath(__file__)), "evdev_paste.py")],
                timeout=5, env=env
            )
            dbg(f"stop_recording_and_type: evdev_paste exit code = {result.returncode}")
            dbg("stop_recording_and_type: paste done")
        except FileNotFoundError:
            dbg("stop_recording_and_type: wl-copy/ydotool NOT FOUND, falling back to wtype")
            try:
                subprocess.run(["wtype", distilled], timeout=10)
                dbg("stop_recording_and_type: wtype done")
            except Exception as e:
                dbg(f"stop_recording_and_type: wtype also failed: {e}")
    else:
        dbg("stop_recording_and_type: no raw text, sending notification")
        subprocess.run(["notify-send", "-t", "2000", "⚠️ Dictation", "No speech detected."])

if __name__ == "__main__":
    dbg(f"=== SCRIPT START pid={os.getpid()} ===")
    dbg(f"PID_FILE={PID_FILE} exists={os.path.exists(PID_FILE)}")
    if os.path.exists(PID_FILE):
        dbg("=> calling stop_recording_and_type()")
        stop_recording_and_type()
    else:
        dbg("=> calling start_recording()")
        start_recording()
    dbg("=== SCRIPT END ===")

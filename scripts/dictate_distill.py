#!/usr/bin/env python3
"""
Distilled Dictation Script for Linux / Hyprland.
Captures audio via pw-record, transcribes via wyoming-faster-whisper (port 10300),
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
import urllib.request
import urllib.error

PID_FILE = "/tmp/dictate_distill_recording.pid"
WAV_FILE = "/tmp/dictate_distill.wav"
PROMPT_DISTILLER_URL = "http://127.0.0.1:8008/v1/distill"

async def transcribe_audio():
    """
    Streams recorded WAV file to local wyoming-faster-whisper ASR server on port 10300.
    """
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
                return transcript.text
    except Exception as e:
        print(f"Transcription error: {e}")
    return ""

def distill_prompt(raw_text: str) -> str:
    """
    Sends raw STT text to PromptDistiller server or falls back to local module import.
    """
    payload = json.dumps({"raw_prompt": raw_text}).encode("utf-8")
    req = urllib.request.Request(
        PROMPT_DISTILLER_URL,
        data=payload,
        headers={"Content-Type": "application/json"}
    )
    
    try:
        with urllib.request.urlopen(req, timeout=10) as response:
            if response.status == 200:
                data = json.loads(response.read().decode("utf-8"))
                distilled = data.get("distilled_prompt", raw_text)
                savings = data.get("token_savings_percent", 0)
                subprocess.run(["notify-send", "-t", "2500", "⚡ Distilled", f"Saved {savings}% tokens! Typing prompt..."])
                return distilled
    except Exception as e:
        print(f"HTTP Distiller fallback notice ({e}). Attempting direct python import...")
    
    # Fallback if server isn't running on port 8008
    try:
        sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
        from app.core.distiller import PromptDistiller
        import yaml
        
        config_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "config.yaml")
        config = {}
        if os.path.exists(config_path):
            with open(config_path) as f:
                config = yaml.safe_load(f)
                
        distiller = PromptDistiller(config)
        res = asyncio.run(distiller.distill_only(raw_text))
        distilled = res.get("distilled_prompt", raw_text)
        savings = res.get("token_savings_percent", 0)
        subprocess.run(["notify-send", "-t", "2500", "⚡ Distilled (Offline)", f"Saved {savings}% tokens! Typing prompt..."])
        return distilled
    except Exception as ex:
        print(f"Fallback distiller error: {ex}")
        return raw_text

def start_recording():
    print("Starting distilled recording...")
    subprocess.run(["notify-send", "-t", "2000", "🎙️ Distilled Dictation", "Listening for AI prompt..."])
    proc = subprocess.Popen(["pw-record", "--channels=1", "--rate=16000", "--format=s16", WAV_FILE])
    with open(PID_FILE, "w") as f:
        f.write(str(proc.pid))
    print("Recording started. Trigger again to stop, distill, and type.")

def stop_recording_and_type():
    print("Stopping recording...")
    if not os.path.exists(PID_FILE):
        return
        
    with open(PID_FILE, "r") as f:
        pid = int(f.read().strip())
    
    os.remove(PID_FILE)
    
    try:
        os.kill(pid, signal.SIGINT)
        import time
        time.sleep(0.5)
    except ProcessLookupError:
        pass
    
    subprocess.run(["notify-send", "-t", "2000", "⚙️ Processing STT", "Transcribing and distilling prompt..."])
    raw_text = asyncio.run(transcribe_audio())
    raw_text = raw_text.strip()
    
    if raw_text:
        print(f"Raw Transcribed: {raw_text}")
        distilled = distill_prompt(raw_text).strip()
        print(f"Distilled Prompt: {distilled}")
        
        safe_text = distilled.replace('"', '\\"')
        subprocess.run(f'wtype "{safe_text}"', shell=True)
    else:
        subprocess.run(["notify-send", "-t", "2000", "⚠️ Dictation", "No speech detected."])

if __name__ == "__main__":
    if os.path.exists(PID_FILE):
        stop_recording_and_type()
    else:
        start_recording()

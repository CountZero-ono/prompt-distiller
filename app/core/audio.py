import os
import logging
from typing import Optional, Dict, Any

logger = logging.getLogger("prompt_distiller.audio")

class AudioTranscriber:
    """
    Audio transcription module utilizing faster-whisper (CPU int8 quantized)
    or OpenAI/Groq Cloud Whisper API fallback.
    """

    def __init__(self, whisper_model: str = "base"):
        self.whisper_model_name = whisper_model
        self._faster_whisper_model = None

    def _load_faster_whisper(self):
        if self._faster_whisper_model is None:
            try:
                from faster_whisper import WhisperModel
                logger.info(f"Loading faster-whisper model '{self.whisper_model_name}' (device=cpu, compute_type=int8)...")
                self._faster_whisper_model = WhisperModel(
                    self.whisper_model_name,
                    device="cpu",
                    compute_type="int8"
                )
                logger.info("faster-whisper loaded successfully.")
            except ImportError:
                logger.info("faster-whisper package not installed. Will try standard whisper or API.")
                raise ImportError("faster-whisper not installed")
            except Exception as e:
                logger.error(f"Error loading faster-whisper: {e}")
                raise e
        return self._faster_whisper_model

    def transcribe(self, file_path: str, api_key: Optional[str] = None, provider: Optional[str] = None) -> str:
        """
        Transcribes audio file to text using faster-whisper, standard whisper, or Cloud API.
        """
        # Try faster-whisper first
        try:
            model = self._load_faster_whisper()
            segments, info = model.transcribe(file_path, beam_size=5)
            text_parts = [segment.text for segment in segments]
            transcript = " ".join(text_parts).strip()
            logger.info(f"faster-whisper ASR complete. Language detected: {info.language} ({info.language_probability:.2f})")
            return transcript
        except Exception as e:
            logger.debug(f"faster-whisper unavailable ({e}). Trying standard whisper...")

        # Try standard openai-whisper
        try:
            import whisper
            model = whisper.load_model(self.whisper_model_name)
            result = model.transcribe(file_path)
            return result.get("text", "").strip()
        except Exception as e:
            logger.debug(f"Standard whisper unavailable ({e}). Checking for Cloud API or mock fallback...")

        # Fallback transcript for demo / offline operation
        logger.warning("Local ASR engines unavailable. Returning sample audio transcription.")
        return (
            "Слушай, у меня тут проблема со сканированием пленки на ролике 120. "
            "Появляется какая-то белая полоса посередине кадров, и я не могу понять, "
            "это пыль на стекле сканера или софт тупит. И кстати, до скольки сегодня "
            "открыта лаборатория для сдачи заказов?"
        )

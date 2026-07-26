import os
import logging
from typing import Dict, Any

logger = logging.getLogger("prompt_distiller.audio")

class AudioTranscriber:
    """
    Audio transcription module using Whisper or fallback mock for demo.
    """

    def __init__(self, whisper_model: str = "base"):
        self.whisper_model = whisper_model
        self._model = None

    def transcribe(self, file_path: str) -> str:
        """
        Transcribes audio file to text.
        """
        try:
            import whisper
            if self._model is None:
                self._model = whisper.load_model(self.whisper_model)
            result = self._model.transcribe(file_path)
            return result.get("text", "")
        except Exception as e:
            logger.warning(f"Local whisper unavailable ({e}). Using mock audio transcript.")
            return (
                "Слушай, у меня тут проблема со сканированием пленки на ролике 120. "
                "Появляется какая-то белая полоса посередине кадров, и я не могу понять, "
                "это пыль на стекле сканера или софт тупит. И кстати, до скольки сегодня "
                "открыта лаборатория для сдачи заказов?"
            )

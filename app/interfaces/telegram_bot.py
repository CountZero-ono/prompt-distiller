import logging
import asyncio
from typing import Dict, Any

logger = logging.getLogger("prompt_distiller.telegram")

class TelegramBotAdapter:
    """
    Telegram Bot Interface Adapter.
    Receives voice notes & text messages, passes through PromptDistiller, and replies cleanly.
    """

    def __init__(self, token: str, distiller_engine):
        self.token = token
        self.distiller = distiller_engine

    def start(self):
        """
        Starts Telegram long-polling / webhook listener.
        """
        logger.info("Initializing Telegram Bot adapter...")
        # Placeholder for python-telegram-bot application lifecycle
        # application = Application.builder().token(self.token).build()
        # application.add_handler(MessageHandler(filters.TEXT | filters.VOICE, self.handle_message))
        # application.run_polling()

    async def handle_message(self, user_text_or_audio_path: str, is_voice: bool = False) -> str:
        """
        Processes incoming telegram text or voice note.
        """
        if is_voice:
            from app.core.audio import AudioTranscriber
            transcriber = AudioTranscriber()
            raw_text = transcriber.transcribe(user_text_or_audio_path)
        else:
            raw_text = user_text_or_audio_path

        result = await self.distiller.process(raw_text, target_language="ru")
        return result["final_response"]

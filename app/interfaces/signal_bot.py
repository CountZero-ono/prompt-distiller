import logging
import httpx
from typing import Dict, Any

logger = logging.getLogger("prompt_distiller.signal")

class SignalBotAdapter:
    """
    Signal Bot Interface Adapter.
    Connects to signal-cli-rest-api via WebSocket / REST endpoints.
    """

    def __init__(self, rest_url: str, account: str, distiller_engine):
        self.rest_url = rest_url
        self.account = account
        self.distiller = distiller_engine

    async def send_message(self, recipient: str, message: str):
        """
        Sends message back via signal-cli REST API.
        """
        async with httpx.AsyncClient() as client:
            url = f"{self.rest_url}/v2/send"
            payload = {
                "number": self.account,
                "recipients": [recipient],
                "message": message
            }
            try:
                await client.post(url, json=payload)
            except Exception as e:
                logger.error(f"Failed to send Signal message: {e}")

    async def on_message_received(self, sender: str, raw_text: str):
        """
        Triggered on incoming Signal message.
        """
        result = await self.distiller.process(raw_text, target_language="ru")
        reply = result["final_response"]
        await self.send_message(sender, reply)

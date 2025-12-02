"""WhatsApp client for sending messages via YCloud API."""

import httpx
from functools import lru_cache
from typing import Optional

from ...config import get_settings
from ...logging_config import logger


class WhatsAppClient:
    """Client for YCloud WhatsApp API."""

    BASE_URL = "https://api.ycloud.com/v2"

    def __init__(self, api_key: str, phone_number: str) -> None:
        self.api_key = api_key
        self.phone_number = phone_number
        self._client: Optional[httpx.AsyncClient] = None

    async def _get_client(self) -> httpx.AsyncClient:
        """Get or create async HTTP client."""
        if self._client is None or self._client.is_closed:
            self._client = httpx.AsyncClient(
                base_url=self.BASE_URL,
                headers={
                    "Content-Type": "application/json",
                    "X-API-Key": self.api_key,
                },
                timeout=30.0,
            )
        return self._client

    async def send_text_message(self, to: str, message: str) -> dict:
        """Send a text message to a WhatsApp user.
        
        Args:
            to: Recipient phone number in international format (e.g., +1234567890)
            message: Text message content (max 4096 characters)
            
        Returns:
            YCloud API response with message ID and status
        """
        client = await self._get_client()
        
        payload = {
            "from": self.phone_number,
            "to": to,
            "type": "text",
            "text": {
                "body": message[:4096],
                "preview_url": False,
            },
        }

        logger.info(
            "Sending WhatsApp message",
            extra={"to": to, "message_length": len(message)},
        )

        try:
            response = await client.post("/whatsapp/messages", json=payload)
            response.raise_for_status()
            result = response.json()
            
            logger.info(
                "WhatsApp message sent",
                extra={"message_id": result.get("id"), "status": result.get("status")},
            )
            return result
            
        except httpx.HTTPStatusError as exc:
            logger.error(
                "WhatsApp API error",
                extra={
                    "status_code": exc.response.status_code,
                    "response": exc.response.text,
                },
            )
            raise
        except Exception as exc:
            logger.error("Failed to send WhatsApp message", extra={"error": str(exc)})
            raise

    async def close(self) -> None:
        """Close the HTTP client."""
        if self._client and not self._client.is_closed:
            await self._client.aclose()
            self._client = None


_whatsapp_client: Optional[WhatsAppClient] = None


def get_whatsapp_client() -> Optional[WhatsAppClient]:
    """Get the singleton WhatsApp client instance."""
    global _whatsapp_client
    
    if _whatsapp_client is None:
        settings = get_settings()
        if settings.ycloud_api_key and settings.ycloud_phone_number:
            _whatsapp_client = WhatsAppClient(
                api_key=settings.ycloud_api_key,
                phone_number=settings.ycloud_phone_number,
            )
        else:
            logger.warning("WhatsApp client not configured: missing YCLOUD_API_KEY or YCLOUD_PHONE_NUMBER")
            return None
    
    return _whatsapp_client

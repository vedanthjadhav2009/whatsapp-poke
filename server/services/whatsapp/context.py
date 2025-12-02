"""WhatsApp context management for tracking active conversations."""

from contextvars import ContextVar
from dataclasses import dataclass, field
from typing import List, Optional


@dataclass
class WhatsAppContext:
    """Context for the current WhatsApp conversation."""
    user_phone: str
    message_id: Optional[str] = None
    customer_name: Optional[str] = None
    messages_sent: List[str] = field(default_factory=list)

    def mark_message_sent(self, message: str) -> None:
        """Track that a message was sent via WhatsApp."""
        self.messages_sent.append(message)

    def was_message_sent(self, message: str) -> bool:
        """Check if a message was already sent."""
        return message in self.messages_sent


_whatsapp_context: ContextVar[Optional[WhatsAppContext]] = ContextVar(
    "whatsapp_context", default=None
)


def get_whatsapp_context() -> Optional[WhatsAppContext]:
    """Get the current WhatsApp context."""
    return _whatsapp_context.get()


def set_whatsapp_context(context: WhatsAppContext) -> None:
    """Set the WhatsApp context for the current request."""
    _whatsapp_context.set(context)


def clear_whatsapp_context() -> None:
    """Clear the WhatsApp context."""
    _whatsapp_context.set(None)

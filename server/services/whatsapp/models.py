"""Pydantic models for YCloud WhatsApp webhook payloads."""

from typing import Optional
from pydantic import BaseModel, ConfigDict, Field


class CustomerProfile(BaseModel):
    """WhatsApp customer profile."""
    model_config = ConfigDict(populate_by_name=True)
    name: Optional[str] = None


class TextContent(BaseModel):
    """Text message content."""
    model_config = ConfigDict(populate_by_name=True)
    body: str


class WhatsAppInboundMessage(BaseModel):
    """Inbound WhatsApp message from YCloud webhook."""
    model_config = ConfigDict(populate_by_name=True)
    id: str
    wamid: Optional[str] = None
    waba_id: Optional[str] = Field(None, alias="wabaId")
    from_number: str = Field(..., alias="from")
    customer_profile: Optional[CustomerProfile] = Field(None, alias="customerProfile")
    to: str
    send_time: Optional[str] = Field(None, alias="sendTime")
    type: str
    text: Optional[TextContent] = None


class WhatsAppWebhookPayload(BaseModel):
    """YCloud webhook event payload."""
    model_config = ConfigDict(populate_by_name=True)
    id: str
    type: str
    api_version: str = Field(..., alias="apiVersion")
    create_time: str = Field(..., alias="createTime")
    whatsapp_inbound_message: Optional[WhatsAppInboundMessage] = Field(
        None, alias="whatsappInboundMessage"
    )


class SendMessageRequest(BaseModel):
    """Request body for sending WhatsApp message via YCloud."""
    from_number: str = Field(..., alias="from")
    to: str
    type: str = "text"
    text: Optional[dict] = None

    class Config:
        populate_by_name = True


class SendMessageResponse(BaseModel):
    """Response from YCloud send message API."""
    id: str
    status: str
    from_number: Optional[str] = Field(None, alias="from")
    to: Optional[str] = None
    type: Optional[str] = None
    create_time: Optional[str] = Field(None, alias="createTime")

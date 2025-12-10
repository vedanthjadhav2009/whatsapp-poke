"""WhatsApp webhook routes for YCloud integration."""

import asyncio
from fastapi import APIRouter, Request, HTTPException, status
from fastapi.responses import JSONResponse

from ..config import get_settings
from ..logging_config import logger
from ..services.whatsapp import (
    get_whatsapp_client,
    WhatsAppContext,
    set_whatsapp_context,
    clear_whatsapp_context,
)
from ..services.whatsapp.signature import verify_ycloud_signature
from ..services.whatsapp.models import WhatsAppWebhookPayload
from ..agents.interaction_agent.runtime import InteractionAgentRuntime

router = APIRouter(prefix="/whatsapp", tags=["whatsapp"])


@router.post("/webhook", response_class=JSONResponse)
async def whatsapp_webhook(request: Request) -> JSONResponse:
    """Handle incoming WhatsApp messages from YCloud webhook.
    
    This endpoint receives webhook events from YCloud when users send
    messages to the WhatsApp Business number.
    """
    try:
        settings = get_settings()

        raw_body = await request.body()
        body_str = raw_body.decode("utf-8")

        signature_header = (
            request.headers.get("YCloud-Signature") or
            request.headers.get("ycloud-signature") or
            request.headers.get("Ycloud-Signature") or
            ""
        )

        if settings.ycloud_webhook_secret:
            if not verify_ycloud_signature(body_str, signature_header, settings.ycloud_webhook_secret):
                logger.warning("Invalid webhook signature")
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Invalid signature",
                )
        else:
            logger.warning("No webhook secret configured, skipping signature verification")
        
        try:
            payload = WhatsAppWebhookPayload.model_validate_json(body_str)
        except Exception as exc:
            logger.error("Failed to parse webhook payload", extra={"error": str(exc)})
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid payload",
            )

        if payload.type == "whatsapp.inbound_message.received":
            await _handle_inbound_message(payload)
        else:
            logger.info(f"Ignoring webhook event type: {payload.type}")

        return JSONResponse({"received": True}, status_code=status.HTTP_200_OK)
    
    except HTTPException:
        raise
    except Exception as exc:
        logger.exception(f"Unexpected error in webhook handler: {exc}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error",
        )


async def _handle_inbound_message(payload: WhatsAppWebhookPayload) -> None:
    """Process an inbound WhatsApp message."""
    message = payload.whatsapp_inbound_message
    
    if not message:
        logger.warning("No message in inbound webhook")
        return

    if message.type != "text" or not message.text:
        logger.info(f"Ignoring non-text message type: {message.type}")
        return

    user_phone = message.from_number
    user_message = message.text.body.strip()
    customer_name = message.customer_profile.name if message.customer_profile else None

    logger.info(
        "Received WhatsApp message",
        extra={
            "from": user_phone,
            "customer_name": customer_name,
            "message_length": len(user_message),
        },
    )

    context = WhatsAppContext(
        user_phone=user_phone,
        message_id=message.id,
        customer_name=customer_name,
    )
    set_whatsapp_context(context)

    async def _process_message() -> None:
        try:
            runtime = InteractionAgentRuntime()
            result = await runtime.execute(user_message=user_message)
            
            if result.success and result.response:
                if not context.was_message_sent(result.response):
                    client = get_whatsapp_client()
                    if client:
                        await client.send_text_message(user_phone, result.response)
                    else:
                        logger.error("WhatsApp client not available")
            elif not result.success:
                logger.error(
                    "Interaction agent failed",
                    extra={"error": result.error},
                )
                client = get_whatsapp_client()
                if client:
                    await client.send_text_message(
                        user_phone,
                        "Sorry, something went wrong. Please try again.",
                    )
        except Exception as exc:
            logger.error("Error processing WhatsApp message", extra={"error": str(exc)})
            client = get_whatsapp_client()
            if client:
                try:
                    await client.send_text_message(
                        user_phone,
                        "Sorry, an error occurred. Please try again later.",
                    )
                except Exception:
                    pass
        finally:
            clear_whatsapp_context()

    asyncio.create_task(_process_message())


@router.get("/health", response_class=JSONResponse)
async def whatsapp_health() -> JSONResponse:
    """Health check endpoint for WhatsApp integration."""
    settings = get_settings()
    
    configured = bool(
        settings.ycloud_api_key and 
        settings.ycloud_phone_number
    )
    
    return JSONResponse({
        "status": "ok" if configured else "not_configured",
        "configured": configured,
    })


__all__ = ["router"]

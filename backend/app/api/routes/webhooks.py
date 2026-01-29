"""
VoxParaguay 2026 - Webhook Routes
Handles incoming webhooks from Twilio (Voice) and Meta (WhatsApp/FB/IG)
"""

from fastapi import APIRouter, Request, HTTPException, Query
from fastapi.responses import PlainTextResponse
import json

from app.services.queue_service import queue_service
from app.core.config import settings

router = APIRouter()


# ============ META WEBHOOKS (WhatsApp, Facebook, Instagram) ============

@router.get("/meta")
async def verify_meta_webhook(
    hub_mode: str = Query(None, alias="hub.mode"),
    hub_verify_token: str = Query(None, alias="hub.verify_token"),
    hub_challenge: str = Query(None, alias="hub.challenge"),
):
    """
    Meta webhook verification endpoint.
    Required for initial webhook setup in Meta Developer Console.
    """
    if hub_mode == "subscribe" and hub_verify_token == settings.META_VERIFY_TOKEN:
        return PlainTextResponse(content=hub_challenge)
    raise HTTPException(status_code=403, detail="Token de verificación inválido")


@router.post("/meta")
async def handle_meta_webhook(request: Request):
    """
    Handle incoming messages from WhatsApp, Facebook Messenger, and Instagram.
    Messages are pushed to Redis queue for async processing.
    """
    try:
        body = await request.json()

        # Process each entry
        for entry in body.get("entry", []):
            # WhatsApp messages
            for change in entry.get("changes", []):
                if change.get("field") == "messages":
                    value = change.get("value", {})
                    messages = value.get("messages", [])

                    for message in messages:
                        await queue_service.push_message({
                            "channel": "whatsapp",
                            "from": message.get("from"),
                            "message_id": message.get("id"),
                            "timestamp": message.get("timestamp"),
                            "type": message.get("type"),
                            "content": _extract_message_content(message),
                            "metadata": value.get("metadata", {}),
                        })

            # Facebook/Instagram messages
            for messaging in entry.get("messaging", []):
                sender_id = messaging.get("sender", {}).get("id")
                message = messaging.get("message", {})

                if message:
                    channel = "instagram" if "instagram" in str(entry.get("id", "")) else "facebook"
                    await queue_service.push_message({
                        "channel": channel,
                        "from": sender_id,
                        "message_id": message.get("mid"),
                        "timestamp": messaging.get("timestamp"),
                        "type": "text" if message.get("text") else "attachment",
                        "content": message.get("text", ""),
                    })

        return {"status": "received"}

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error procesando webhook: {str(e)}")


# ============ TWILIO WEBHOOKS (Voice) ============

@router.post("/twilio/voice")
async def handle_twilio_voice(request: Request):
    """
    Handle incoming voice calls from Twilio.
    Returns TwiML for call handling.
    """
    form_data = await request.form()

    call_data = {
        "channel": "voice",
        "from": form_data.get("From"),
        "to": form_data.get("To"),
        "call_sid": form_data.get("CallSid"),
        "call_status": form_data.get("CallStatus"),
        "direction": form_data.get("Direction"),
    }

    await queue_service.push_message(call_data)

    # Return TwiML to connect to agent
    twiml = """<?xml version="1.0" encoding="UTF-8"?>
    <Response>
        <Say language="es-MX">Bienvenido a VoxParaguay. Por favor espere mientras lo conectamos con un agente.</Say>
        <Enqueue>encuestas</Enqueue>
    </Response>
    """
    return PlainTextResponse(content=twiml, media_type="application/xml")


@router.post("/twilio/voice/status")
async def handle_twilio_voice_status(request: Request):
    """
    Handle Twilio call status callbacks.
    """
    form_data = await request.form()

    await queue_service.push_message({
        "channel": "voice_status",
        "call_sid": form_data.get("CallSid"),
        "call_status": form_data.get("CallStatus"),
        "call_duration": form_data.get("CallDuration"),
    })

    return {"status": "received"}


@router.post("/twilio/transcription")
async def handle_twilio_transcription(request: Request):
    """
    Handle real-time transcription from Twilio.
    Used for Jopara (Spanish-Guaraní) speech recognition.
    """
    form_data = await request.form()

    await queue_service.push_message({
        "channel": "transcription",
        "call_sid": form_data.get("CallSid"),
        "transcription_text": form_data.get("TranscriptionText"),
        "confidence": form_data.get("Confidence"),
    })

    return {"status": "received"}


def _extract_message_content(message: dict) -> str:
    """Extract message content based on message type."""
    msg_type = message.get("type")

    if msg_type == "text":
        return message.get("text", {}).get("body", "")
    elif msg_type == "interactive":
        interactive = message.get("interactive", {})
        if interactive.get("type") == "button_reply":
            return interactive.get("button_reply", {}).get("title", "")
        elif interactive.get("type") == "list_reply":
            return interactive.get("list_reply", {}).get("title", "")
    elif msg_type == "button":
        return message.get("button", {}).get("text", "")

    return ""

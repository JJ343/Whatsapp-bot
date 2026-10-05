"""Thin wrapper around the WhatsApp Cloud API (Meta).

Design choice: if no real credentials are configured (see `config.py`),
every send function falls back to MOCK mode and prints to stdout instead
of calling the Graph API. That makes the bot demoable and testable
without a Meta account.
"""

import sys

import requests

import config

# Avoid UnicodeEncodeError on Windows consoles (cp1252).
try:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
except Exception:
    pass


def _safe_print(msg: str) -> None:
    try:
        print(msg)
    except UnicodeEncodeError:
        print(msg.encode("ascii", "backslashreplace").decode())


def _headers() -> dict:
    return {
        "Authorization": f"Bearer {config.WHATSAPP_TOKEN}",
        "Content-Type": "application/json",
    }


def send_text_message(to: str, body: str) -> dict:
    """Send a plain text message. Returns the API (or mock) response."""
    if not config.is_configured():
        _safe_print(f"[MOCK MODE] To {to}: {body}")
        return {"mock": True}

    payload = {
        "messaging_product": "whatsapp",
        "to": to,
        "type": "text",
        "text": {"body": body},
    }
    response = requests.post(
        config.GRAPH_URL, headers=_headers(), json=payload, timeout=15
    )
    response.raise_for_status()
    return response.json()


def send_menu_buttons(to: str, body_text: str, lang: str = "en") -> dict:
    """Send the main menu with interactive reply buttons (EN/ES)."""
    if not config.is_configured():
        _safe_print(f"[MOCK MODE] Buttons [{lang}] for {to}: {body_text}")
        return {"mock": True}

    if (lang or "en").lower().startswith("es"):
        buttons = [
            {"type": "reply", "reply": {"id": "2", "title": "💼 Servicios"}},
            {"type": "reply", "reply": {"id": "cotizar", "title": "📝 Cotizar"}},
            {"type": "reply", "reply": {"id": "4", "title": "🧑‍💻 Técnico"}},
        ]
    else:
        buttons = [
            {"type": "reply", "reply": {"id": "2", "title": "💼 Services"}},
            {"type": "reply", "reply": {"id": "quote", "title": "📝 Quote"}},
            {"type": "reply", "reply": {"id": "4", "title": "🧑‍💻 Technician"}},
        ]
    payload = {
        "messaging_product": "whatsapp",
        "to": to,
        "type": "interactive",
        "interactive": {
            "type": "button",
            "body": {"text": body_text[:1024]},
            "action": {"buttons": buttons},
        },
    }
    response = requests.post(
        config.GRAPH_URL, headers=_headers(), json=payload, timeout=15
    )
    response.raise_for_status()
    return response.json()


def mark_as_read(message_id: str) -> None:
    """Mark an incoming message as read (no-op in MOCK mode)."""
    if not config.is_configured():
        return
    try:
        requests.post(
            config.GRAPH_URL,
            headers=_headers(),
            json={
                "messaging_product": "whatsapp",
                "status": "read",
                "message_id": message_id,
            },
            timeout=10,
        )
    except Exception as exc:  # never break the webhook on a read receipt
        print(f"Could not mark message as read: {exc}")

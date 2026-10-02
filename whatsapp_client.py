"""Cliente para enviar mensajes con WhatsApp Cloud API (Meta)."""
import sys
import requests
import config

# Evita UnicodeEncodeError en consolas Windows (cp1252)
try:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
except Exception:
    pass


def _safe_print(msg: str):
    try:
        print(msg)
    except UnicodeEncodeError:
        print(msg.encode("ascii", "backslashreplace").decode())


def _headers():
    return {
        "Authorization": f"Bearer {config.WHATSAPP_TOKEN}",
        "Content-Type": "application/json",
    }


def send_text_message(to: str, body: str) -> dict:
    """Envía un mensaje de texto simple."""
    if not config.WHATSAPP_TOKEN or not config.PHONE_NUMBER_ID:
        _safe_print(f"[MODO PRUEBA] Para {to}: {body}")
        return {"mock": True}

    payload = {
        "messaging_product": "whatsapp",
        "to": to,
        "type": "text",
        "text": {"body": body},
    }
    r = requests.post(config.GRAPH_URL, headers=_headers(), json=payload, timeout=15)
    r.raise_for_status()
    return r.json()


def send_menu_buttons(to: str, body_text: str) -> dict:
    """Envía el menú con botones interactivos."""
    if not config.WHATSAPP_TOKEN or not config.PHONE_NUMBER_ID:
        _safe_print(f"[MODO PRUEBA] Botones para {to}: {body_text}")
        return {"mock": True}

    payload = {
        "messaging_product": "whatsapp",
        "to": to,
        "type": "interactive",
        "interactive": {
            "type": "button",
            "body": {"text": body_text[:1024]},
            "action": {
                "buttons": [
                    {"type": "reply", "reply": {"id": "1", "title": "🕒 Horarios"}},
                    {"type": "reply", "reply": {"id": "2", "title": "💼 Servicios"}},
                    {"type": "reply", "reply": {"id": "3", "title": "📍 Ubicación"}},
                ]
            },
        },
    }
    r = requests.post(config.GRAPH_URL, headers=_headers(), json=payload, timeout=15)
    r.raise_for_status()
    return r.json()


def mark_as_read(message_id: str) -> None:
    if not config.WHATSAPP_TOKEN or not config.PHONE_NUMBER_ID:
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
    except Exception as e:
        print(f"No se pudo marcar como leído: {e}")

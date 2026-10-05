"""Flask webhook for the WhatsApp Cloud API (Meta).

Two responsibilities only (business logic lives in `bot_logic.py`):
  GET  /webhook -> verification handshake required once by Meta.
  POST /webhook -> incoming message events (text + interactive buttons).

Run locally with `python app.py`, expose with ngrok, then register
`https://<your-ngrok-url>/webhook` in the Meta dashboard.
"""

from flask import Flask, jsonify, request

import config
import whatsapp_client
from bot_logic import get_user_lang, process_message

app = Flask(__name__)


@app.route("/", methods=["GET"])
def health():
    """Simple health check for browsers and uptime monitors."""
    return "TechFix bot is running. Use /webhook for Meta.", 200


@app.route("/webhook", methods=["GET"])
def verify():
    """Meta verification handshake (subscribe challenge)."""
    mode = request.args.get("hub.mode")
    token = request.args.get("hub.verify_token")
    challenge = request.args.get("hub.challenge")
    if mode == "subscribe" and token == config.VERIFY_TOKEN:
        return challenge, 200
    return "Invalid verify token", 403


def _extract_text(message: dict) -> str:
    """Extract user text from plain or interactive (button) messages."""
    msg_type = message.get("type", "")
    if msg_type == "text":
        return message.get("text", {}).get("body", "")
    if msg_type == "interactive":
        interactive = message.get("interactive", {})
        return (
            interactive.get("button_reply", {}).get("id", "")
            or interactive.get("list_reply", {}).get("id", "")
            or interactive.get("button_reply", {}).get("title", "")
        )
    return ""


def _is_menu_response(response: str) -> bool:
    return "1️⃣" in response and (
        "How can I help you" in response or "¿En qué puedo ayudarte" in response
    )


@app.route("/webhook", methods=["POST"])
def incoming():
    """Receive a WhatsApp event, compute a reply, send it back."""
    data = request.get_json(silent=True) or {}

    try:
        entry = data.get("entry", [{}])[0]
        change = entry.get("changes", [{}])[0]
        value = change.get("value", {})

        # Skip status updates (sent / delivered / read), no user text there.
        if "messages" not in value:
            return jsonify({"status": "ignored"}), 200

        message = value["messages"][0]
        from_number = message.get("from", "")
        msg_id = message.get("id", "")
        text = _extract_text(message)

        whatsapp_client.mark_as_read(msg_id)

        if not text:
            whatsapp_client.send_text_message(
                from_number,
                "I can only process text for now. Type *menu*.",
            )
            return jsonify({"status": "ok"}), 200

        response = process_message(from_number, text)

        # Menus look better as interactive buttons; everything else as text.
        # A send failure (e.g. expired test token) must not fail the webhook.
        try:
            if _is_menu_response(response):
                try:
                    lang = get_user_lang(from_number)
                    whatsapp_client.send_menu_buttons(from_number, response, lang=lang)
                except Exception:
                    whatsapp_client.send_text_message(from_number, response)
            else:
                whatsapp_client.send_text_message(from_number, response)
        except Exception as exc:
            print(f"Send failed (check WHATSAPP_TOKEN): {exc}")

        return jsonify({"status": "ok"}), 200

    except Exception as exc:
        # Always answer 200 so Meta stops retrying a poisoned event.
        print(f"Webhook error: {exc}")
        return jsonify({"status": "error", "detail": str(exc)}), 200


# Backwards-compatible alias (older imports / docs used the Spanish name).
def procesar_mensaje(user_id: str, texto: str) -> str:
    """Alias of :func:`process_message` kept for backwards compatibility."""
    return process_message(user_id, texto)


if __name__ == "__main__":
    print(f"Bot running at http://localhost:{config.PORT}")
    print(f"Webhook: http://localhost:{config.PORT}/webhook")
    app.run(host="0.0.0.0", port=config.PORT, debug=True)

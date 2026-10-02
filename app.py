"""Webhook Flask para WhatsApp Cloud API."""
from flask import Flask, request, jsonify
import config
from bot_logic import procesar_mensaje
import whatsapp_client

app = Flask(__name__)


@app.route("/", methods=["GET"])
def health():
    return "Bot WP servicio al cliente activo ✅. Usa /webhook para Meta.", 200


# 1. Verificación de Meta (solo GET)
@app.route("/webhook", methods=["GET"])
def verify():
    mode = request.args.get("hub.mode")
    token = request.args.get("hub.verify_token")
    challenge = request.args.get("hub.challenge")
    if mode == "subscribe" and token == config.VERIFY_TOKEN:
        return challenge, 200
    return "Token inválido", 403


# 2. Recepción de mensajes (POST)
@app.route("/webhook", methods=["POST"])
def incoming():
    data = request.get_json(silent=True) or {}
    # print(data)  # descomenta para debug

    try:
        entry = data.get("entry", [{}])[0]
        change = entry.get("changes", [{}])[0]
        value = change.get("value", {})

        # Ignorar estados (sent, delivered, read)
        if "messages" not in value:
            return jsonify({"status": "ignored"}), 200

        message = value["messages"][0]
        from_number = message.get("from", "")
        msg_id = message.get("id", "")
        msg_type = message.get("type", "")

        whatsapp_client.mark_as_read(msg_id)

        # Extraer texto: mensaje normal o botón interactivo
        if msg_type == "text":
            texto = message.get("text", {}).get("body", "")
        elif msg_type == "interactive":
            ir = message.get("interactive", {})
            texto = (
                ir.get("button_reply", {}).get("id", "")
                or ir.get("list_reply", {}).get("id", "")
                or ir.get("button_reply", {}).get("title", "")
            )
        else:
            texto = ""

        if not texto:
            whatsapp_client.send_text_message(from_number, "Solo puedo procesar mensajes de texto por ahora. Escribe *menu*.")
            return jsonify({"status": "ok"}), 200

        respuesta = procesar_mensaje(from_number, texto)

        # Si es el menú, mándalo con botones; si no, texto simple
        if "¿En qué puedo ayudarte" in respuesta:
            try:
                whatsapp_client.send_menu_buttons(from_number, respuesta)
            except Exception:
                whatsapp_client.send_text_message(from_number, respuesta)
        else:
            whatsapp_client.send_text_message(from_number, respuesta)

        return jsonify({"status": "ok"}), 200

    except Exception as e:
        print(f"Error en webhook: {e}")
        return jsonify({"status": "error", "detail": str(e)}), 200


if __name__ == "__main__":
    print(f"🚀 Bot iniciado en http://localhost:{config.PORT}")
    print("Webhook: http://localhost:{}/webhook".format(config.PORT))
    app.run(host="0.0.0.0", port=config.PORT, debug=True)

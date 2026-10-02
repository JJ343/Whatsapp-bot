"""
Lógica del bot de servicio al cliente.
Edita los textos de NEGOCIO_INFO para personalizarlo a tu empresa.
"""

NEGOCIO_INFO = {
    "nombre": "Mi Negocio",
    "horario": "Lunes a Viernes 9:00 - 18:00\nSábados 9:00 - 13:00",
    "servicios": "1. Asesoría general\n2. Cotizaciones\n3. Soporte técnico\n4. Seguimiento de casos",
    "precios": "Los precios varían según el servicio. Escribe *cotizar* para solicitar una cotización.",
    "ubicacion": "Av. Principal 123, Ciudad\nGoogle Maps: https://maps.google.com/?q=Av+Principal+123",
    "contacto_humano": "Un asesor te atenderá en breve. Horario de atención humana: Lun-Vie 9-18h.",
    "despedida": "Gracias por contactarnos. ¡Estamos para servirte! 🙌",
}

MENU_PRINCIPAL = """👋 Hola, soy el asistente virtual de *{nombre}*.

¿En qué puedo ayudarte hoy? Escribe el número o toca un botón:

1️⃣ Horarios de atención
2️⃣ Servicios y precios
3️⃣ Ubicación y contacto
4️⃣ Hablar con un asesor
5️⃣ Preguntas frecuentes

Escribe *menu* en cualquier momento para volver aquí.""".format(nombre=NEGOCIO_INFO["nombre"])

FAQ_TEXT = """❓ *Preguntas frecuentes:*

• ¿Tienen servicio a domicilio? → Sí, consúltanos por tu zona.
• ¿Qué medios de pago aceptan? → Efectivo, transferencia y tarjeta.
• ¿Cómo pido una cotización? → Escribe *cotizar* y te pedimos los datos.
• ¿Cómo hablo con una persona? → Escribe *asesor*.

Escribe *menu* para volver."""

# Memoria simple en RAM: {numero_wa: estado}
# Para producción usa Redis o una BD.
user_sessions = {}


def get_menu():
    return MENU_PRINCIPAL


def procesar_mensaje(user_id: str, texto: str) -> str:
    """
    Recibe el número del usuario y el texto normalizado.
    Devuelve el texto de respuesta a enviar.
    """
    t = (texto or "").strip().lower()

    # Comandos globales
    if t in ("hola", "buenas", "buenos dias", "buenos días", "hello", "hi", "menu", "menú", "inicio", "0"):
        user_sessions[user_id] = "menu"
        return MENU_PRINCIPAL

    if t in ("adios", "adiós", "gracias", "bye", "chao"):
        user_sessions.pop(user_id, None)
        return NEGOCIO_INFO["despedida"]

    estado = user_sessions.get(user_id, "menu")

    # Si estaba esperando datos de cotización
    if estado == "esperando_datos_cotizacion":
        user_sessions[user_id] = "menu"
        return (
            "✅ ¡Gracias! Recibimos tu solicitud:\n"
            f"\"{texto.strip()}\"\n\n"
            "Un asesor la revisará y te responderá pronto.\n\n"
            + MENU_PRINCIPAL
        )

    # Menú principal
    if t in ("1", "horario", "horarios", "hora", "atencion"):
        return f"🕒 *Horarios de atención:*\n{NEGOCIO_INFO['horario']}\n\nEscribe *menu* para ver más opciones."

    if t in ("2", "servicios", "precios", "precio", "servicio"):
        return f"💼 *Servicios:*\n{NEGOCIO_INFO['servicios']}\n\n💰 {NEGOCIO_INFO['precios']}\n\nEscribe *menu* para volver."

    if t in ("3", "ubicacion", "ubicación", "donde", "dirección", "direccion", "contacto"):
        return f"📍 *Ubicación y contacto:*\n{NEGOCIO_INFO['ubicacion']}\n\nEscribe *menu* para volver."

    if t in ("4", "asesor", "humano", "persona", "ayuda", "agente"):
        user_sessions[user_id] = "derivado_asesor"
        return (
            f"🙋 {NEGOCIO_INFO['contacto_humano']}\n"
            "Ya avisamos a nuestro equipo. Mientras tanto, cuéntanos brevemente tu consulta y te responderemos."
        )

    if t in ("5", "faq", "preguntas", "frecuentes", "dudas"):
        return FAQ_TEXT

    if "cotiz" in t:
        user_sessions[user_id] = "esperando_datos_cotizacion"
        return (
            "📝 Para cotizar necesito:\n"
            "1. Tu nombre\n"
            "2. Servicio que necesitas\n"
            "3. Tu ciudad\n\n"
            "Escríbelo todo en un solo mensaje, por favor."
        )

    # Si ya fue derivado, no spamear menú, solo acusar recibo
    if estado == "derivado_asesor":
        return "Anotado ✅. Un asesor te responderá en breve. Gracias por tu paciencia."

    # Fallback
    return (
        "🤔 No entendí tu mensaje.\n\n"
        + MENU_PRINCIPAL
    )

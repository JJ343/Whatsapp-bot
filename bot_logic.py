"""Bilingual (EN/ES) rule-based bot brain for a tech-services business.

How I designed it:
  - Pure function `process_message(user_id, text) -> str` with no I/O,
    so it is trivially unit-testable (see `tests/` and `demo.py`).
  - All copy lives in the `TEXTS` dict per language; add a language by
    adding one dict entry, no logic changes needed.
  - Tiny in-RAM state machine (`user_sessions`) handles multi-step flows
    such as the quote request. Swap it for Redis/DB in production.
  - Language is auto-detected per user from markers, persisted in
    `user_lang`, and switchable with `english` / `español`.

Example business: TechFix Solutions (PC repair, web dev, remote support).
Customize every string in `TEXTS` for your own business.
"""

TEXTS = {
    "en": {
        "horario": "Mon-Fri 9:00 AM - 7:00 PM\nSat 10:00 AM - 2:00 PM\nUrgent support 24/7 via WhatsApp",
        "servicios": "1. PC / Laptop repair\n2. Web dev & WhatsApp bots\n3. Remote support (TeamViewer / AnyDesk)\n4. Monthly maintenance plans for business",
        "precios": "Diagnosis $150 MXN (free with repair) / Remote support from $300 MXN / Websites from $4,999 MXN / Business plans from $999 MXN/mo. Type *quote* for a quote.",
        "ubicacion": "Remote all over Mexico + Lab: Av. Tecnologico 123, City\nGoogle Maps: https://maps.google.com/?q=Av+Tecnologico+123",
        "contacto_humano": "A technician will assist you shortly. Human support hours: Mon-Fri 9AM-7PM.",
        "despedida": "Thanks for contacting TechFix! We're here to help! 🙌",
        "menu": """👋 Hi, I'm the virtual assistant from *TechFix Solutions*.

How can I help you today? Type the number or tap a button:

1️⃣ Hours & urgent support
2️⃣ Services & pricing
3️⃣ Quote a project / repair
4️⃣ Talk to a technician
5️⃣ FAQ

Type *menu* anytime to come back here.
Type *español* to switch to Spanish.""",
        "faq": """❓ *FAQ:*

• Do you offer remote / home service? → Yes, via TeamViewer / AnyDesk all over Mexico.
• Do you offer warranty? → Yes, 30 days on labor.
• How long for a website / bot? → Usually 5-10 days.
• How do I get a quote? → Type *quote* and send your details.
• How do I talk to a human? → Type *technician*.

Type *menu* to go back.""",
        "hours": "🕒 *Support hours:*\n{horario}\n\nType *menu* for more options.",
        "services": "💼 *Services:*\n{servicios}\n\n💰 {precios}\n\nType *menu* to go back.",
        "location": "📍 *Location & remote support:*\n{ubicacion}\n\nWe can also help you 100% remote. Type *quote* to start.\n\nType *menu* to go back.",
        "to_technician": "🧑‍💻 {contacto}\nWe already notified our team. Meanwhile, briefly tell us your issue and we'll reply.",
        "ask_quote": "📝 To quote I need:\n1. Your name\n2. Type: repair / website / bot / remote support\n3. Model or idea + your city + budget\n\nPlease send it all in one single message.",
        "quote_ok": "✅ Thanks! We received your request:\n\"{texto}\"\n\nA technician will review it and reply soon.\n\n{menu}",
        "transferred_ack": "Noted ✅. A technician will reply shortly. Thanks for your patience.",
        "fallback": "🤔 I didn't understand that, I'm still in beta.\n\n{menu}",
        "lang_switched": "✅ Language switched to English.\n\n{menu}",
    },
    "es": {
        "horario": "Lun-Vie 9:00 - 19:00\nSáb 10:00 - 14:00\nSoporte urgente 24/7 por WhatsApp",
        "servicios": "1. Reparación de PC / Laptops\n2. Desarrollo web y bots de WhatsApp\n3. Soporte remoto (TeamViewer / AnyDesk)\n4. Planes de mantenimiento mensual para negocios",
        "precios": "Diagnóstico $150 MXN (gratis con reparación) / Soporte remoto desde $300 MXN / Sitios web desde $4,999 MXN / Planes negocios desde $999 MXN/mes. Escribe *cotizar* para cotizar.",
        "ubicacion": "Remoto a todo México + Taller: Av. Tecnológico 123, Ciudad\nGoogle Maps: https://maps.google.com/?q=Av+Tecnologico+123",
        "contacto_humano": "Un técnico te atenderá en breve. Horario humano: Lun-Vie 9-19h.",
        "despedida": "¡Gracias por contactar a TechFix! ¡Estamos para ayudarte! 🙌",
        "menu": """👋 Hola, soy el asistente virtual de *TechFix Solutions*.

¿En qué puedo ayudarte hoy? Escribe el número o toca un botón:

1️⃣ Horarios y soporte urgente
2️⃣ Servicios y precios
3️⃣ Cotizar proyecto / reparación
4️⃣ Hablar con un técnico
5️⃣ Preguntas frecuentes

Escribe *menu* en cualquier momento para volver aquí.
Escribe *english* para cambiar a inglés.""",
        "faq": """❓ *Preguntas frecuentes:*

• ¿Hacen servicio remoto / a domicilio? → Sí, por TeamViewer / AnyDesk a todo México.
• ¿Tienen garantía? → Sí, 30 días en mano de obra.
• ¿Cuánto tarda una web / bot? → Normalmente 5-10 días.
• ¿Cómo cotizo? → Escribe *cotizar* y envíanos tus datos.
• ¿Cómo hablo con un humano? → Escribe *técnico*.

Escribe *menu* para volver.""",
        "hours": "🕒 *Horarios de atención:*\n{horario}\n\nEscribe *menu* para más opciones.",
        "services": "💼 *Servicios:*\n{servicios}\n\n💰 {precios}\n\nEscribe *menu* para volver.",
        "location": "📍 *Ubicación y soporte remoto:*\n{ubicacion}\n\nTambién te ayudamos 100% remoto. Escribe *cotizar* para empezar.\n\nEscribe *menu* para volver.",
        "to_technician": "🧑‍💻 {contacto}\nYa avisamos a nuestro equipo. Mientras tanto, cuéntanos brevemente tu problema y te respondemos.",
        "ask_quote": "📝 Para cotizar necesito:\n1. Tu nombre\n2. Tipo: reparación / web / bot / soporte remoto\n3. Modelo o idea + tu ciudad + presupuesto\n\nEnvíalo todo en un solo mensaje, por favor.",
        "quote_ok": "✅ ¡Gracias! Recibimos tu solicitud:\n\"{texto}\"\n\nUn técnico la revisará y te responderá pronto.\n\n{menu}",
        "transferred_ack": "Anotado ✅. Un técnico te responderá en breve. Gracias por tu paciencia.",
        "fallback": "🤔 No entendí eso, aún estoy en beta.\n\n{menu}",
        "lang_switched": "✅ Idioma cambiado a español.\n\n{menu}",
    },
}

NOMBRE_NEGOCIO = "TechFix Solutions"

# Backward compat: old imports keep working (default English)
NEGOCIO_INFO = {
    "nombre": NOMBRE_NEGOCIO,
    "horario": TEXTS["en"]["horario"],
    "servicios": TEXTS["en"]["servicios"],
    "precios": TEXTS["en"]["precios"],
    "ubicacion": TEXTS["en"]["ubicacion"],
    "contacto_humano": TEXTS["en"]["contacto_humano"],
    "despedida": TEXTS["en"]["despedida"],
}
MENU_PRINCIPAL = TEXTS["en"]["menu"]
FAQ_TEXT = TEXTS["en"]["faq"]

# Simple in-RAM memory: {wa_number: state} + {wa_number: lang}
# For production use Redis or a DB.
user_sessions = {}
user_lang = {}


SPANISH_MARKERS = {
    "hola", "buenas", "buenos dias", "buenos días", "buenas tardes", "buenas noches",
    "gracias", "adios", "adiós", "cotizar", "cotizacion", "cotización",
    "asesor", "tecnico", "técnico", "humano", "ayuda", "horario", "horarios",
    "ubicacion", "ubicación", "precio", "precios", "servicio", "servicios",
    "español", "espanol", "dudas", "preguntas",
}

ENGLISH_MARKERS = {
    "hello", "hi", "hey", "thanks", "thank you", "quote", "technician",
    "hours", "pricing", "services", "location", "warranty", "english",
}


def detect_lang(user_id: str, t: str) -> str:
    """Detect and persist user language. Returns 'en' or 'es'."""
    # Explicit switch always wins
    if t in ("english", "ingles", "inglés", "en"):
        user_lang[user_id] = "en"
        return "en"
    if t in ("spanish", "español", "espanol", "es"):
        user_lang[user_id] = "es"
        return "es"

    # Marker-based detection: Spanish markers -> es, English -> en.
    # Check Spanish first (hola, gracias, cotizar... are unambiguous).
    has_es = any(m in t for m in SPANISH_MARKERS) if len(t) > 2 else t in SPANISH_MARKERS
    has_en = any(m in t for m in ENGLISH_MARKERS) if len(t) > 2 else t in ENGLISH_MARKERS

    if has_es and not has_en:
        user_lang[user_id] = "es"
        return "es"
    if has_en and not has_es:
        user_lang[user_id] = "en"
        return "en"
    # Neutral (numbers, menu, single words): keep previous, default en
    return user_lang.get(user_id, "en")


def get_user_lang(user_id: str) -> str:
    return user_lang.get(user_id, "en")


def get_menu(lang: str = "en") -> str:
    return TEXTS.get(lang, TEXTS["en"])["menu"]


def procesar_mensaje(user_id: str, texto: str) -> str:
    """Spanish alias kept for backwards compatibility.

    Receives user number and raw text.
    Auto-detects EN/ES, persists preference, replies in that language.
    """
    return process_message(user_id, texto)


def process_message(user_id: str, texto: str) -> str:
    """
    Core entry point: receives user number and raw text.
    Auto-detects EN/ES, persists preference, replies in that language.
    """
    raw = (texto or "").strip()
    t = raw.lower()

    # Explicit language switch -> confirm + menu in new lang
    if t in ("english", "ingles", "inglés", "en"):
        user_lang[user_id] = "en"
        user_sessions[user_id] = "menu"
        return TEXTS["en"]["lang_switched"].format(menu=TEXTS["en"]["menu"])
    if t in ("spanish", "español", "espanol", "es"):
        user_lang[user_id] = "es"
        user_sessions[user_id] = "menu"
        return TEXTS["es"]["lang_switched"].format(menu=TEXTS["es"]["menu"])

    lang = detect_lang(user_id, t)
    L = TEXTS[lang]

    # Global commands (bilingual)
    if t in ("hello", "hi", "hey", "good morning", "good afternoon",
             "hola", "buenas", "buenos dias", "buenos días", "buenas tardes",
             "menu", "menú", "start", "inicio", "home", "0"):
        user_sessions[user_id] = "menu"
        return L["menu"]

    if t in ("bye", "goodbye", "thanks", "thank you", "see you",
             "adios", "adiós", "gracias", "chao"):
        user_sessions.pop(user_id, None)
        return L["despedida"]

    estado = user_sessions.get(user_id, "menu")

    # If waiting for quote details -> confirm in user's lang
    if estado == "esperando_datos_cotizacion":
        user_sessions[user_id] = "menu"
        return L["quote_ok"].format(texto=raw, menu=L["menu"])

    # 1 Hours
    if t in ("1", "hours", "schedule", "open", "urgent",
             "horario", "horarios", "hora", "atencion", "atención"):
        return L["hours"].format(horario=L["horario"])

    # 2 Services
    if t in ("2", "services", "pricing", "price", "prices", "plans", "plan",
             "servicios", "precios", "precio", "servicio", "planes"):
        return L["services"].format(servicios=L["servicios"], precios=L["precios"])

    # 3 Location
    if t in ("3", "location", "where", "address", "remote", "lab", "map",
             "ubicacion", "ubicación", "donde", "direccion", "dirección", "contacto", "mapa"):
        return L["location"].format(ubicacion=L["ubicacion"])

    # 4 Technician / human
    if t in ("4", "technician", "human", "agent", "person", "help", "support",
             "asesor", "tecnico", "técnico", "humano", "persona", "ayuda", "agente"):
        user_sessions[user_id] = "derivado_asesor"
        return L["to_technician"].format(contacto=L["contacto_humano"])

    # 5 FAQ
    if t in ("5", "faq", "questions", "frequent", "warranty", "guarantee",
             "preguntas", "frecuentes", "dudas", "garantia", "garantía"):
        return L["faq"]

    # Quote flow (bilingual keywords + substrings)
    if ("quot" in t or "cotiz" in t or "estimate" in t
            or "presupuesto" in t or t in ("price", "precio")):
        user_sessions[user_id] = "esperando_datos_cotizacion"
        return L["ask_quote"]

    # If already transferred, acknowledge in user's lang
    if estado == "derivado_asesor":
        return L["transferred_ack"]

    # Fallback in user's lang
    return L["fallback"].format(menu=L["menu"])

"""Unit tests for the rule-based bot brain (no network, no Flask)."""

import bot_logic
from bot_logic import get_user_lang, process_message


def fresh(user: str = "test-user"):
    bot_logic.user_sessions.pop(user, None)
    bot_logic.user_lang.pop(user, None)
    return user


def test_greeting_returns_menu_english():
    u = fresh()
    reply = process_message(u, "hello")
    assert "How can I help you" in reply
    assert "1️⃣" in reply


def test_greeting_returns_menu_spanish():
    u = fresh()
    reply = process_message(u, "hola")
    assert "¿En qué puedo ayudarte" in reply
    assert get_user_lang(u) == "es"


def test_option_1_hours():
    u = fresh()
    process_message(u, "hi")
    reply = process_message(u, "1")
    assert "Mon-Fri" in reply or "Lun-Vie" in reply


def test_option_2_services():
    u = fresh()
    process_message(u, "hi")
    reply = process_message(u, "2")
    assert "PC" in reply or "Servicios" in reply


def test_quote_flow_asks_then_confirms():
    u = fresh()
    process_message(u, "hi")
    ask = process_message(u, "quote")
    assert "name" in ask.lower() or "nombre" in ask.lower()
    confirm = process_message(u, "Alice, website, CDMX, 5000")
    assert "Thanks" in confirm or "Gracias" in confirm


def test_technician_handoff():
    u = fresh()
    process_message(u, "hi")
    reply = process_message(u, "4")
    assert "technician" in reply.lower() or "técnico" in reply.lower()


def test_language_switch():
    u = fresh()
    process_message(u, "hello")
    reply = process_message(u, "español")
    assert "español" in reply.lower() or "spanish" in reply.lower()
    assert get_user_lang(u) == "es"


def test_fallback_keeps_menu():
    u = fresh()
    process_message(u, "hi")
    reply = process_message(u, "asdfghjkl")
    assert "menu" in reply.lower()

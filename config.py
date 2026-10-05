"""Centralized configuration loaded from environment variables.

Copy `.env.example` to `.env` and fill in your Meta credentials.
All values have safe defaults so the bot runs in MOCK mode without them.
"""

import os

from dotenv import load_dotenv

load_dotenv()

# Token Meta sends back to verify our webhook (you invent this value).
VERIFY_TOKEN: str = os.getenv("VERIFY_TOKEN", "")
# Short-lived test token from developers.facebook.com > WhatsApp > API Setup.
WHATSAPP_TOKEN: str = os.getenv("WHATSAPP_TOKEN", "")
# Phone Number ID of the Meta test number.
PHONE_NUMBER_ID: str = os.getenv("PHONE_NUMBER_ID", "")
API_VERSION: str = os.getenv("API_VERSION", "v22.0")
PORT: int = int(os.getenv("PORT", "8000"))

GRAPH_URL: str = (
    f"https://graph.facebook.com/{API_VERSION}/{PHONE_NUMBER_ID}/messages"
    if PHONE_NUMBER_ID
    else ""
)


def is_configured() -> bool:
    """Return True only when real Meta credentials are present."""
    tok = (WHATSAPP_TOKEN or "").strip()
    pid = (PHONE_NUMBER_ID or "").strip()
    if not tok or not pid:
        return False
    # Ignore placeholder values shipped in .env.example
    if tok.startswith("YOUR_") or pid.startswith("YOUR_"):
        return False
    if tok.startswith("TU_") or pid.startswith("TU_"):
        return False
    return True

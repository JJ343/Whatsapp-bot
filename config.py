import os
from dotenv import load_dotenv

load_dotenv()

VERIFY_TOKEN = os.getenv("VERIFY_TOKEN", "mi_token_secreto_123")
WHATSAPP_TOKEN = os.getenv("WHATSAPP_TOKEN", "")
PHONE_NUMBER_ID = os.getenv("PHONE_NUMBER_ID", "")
API_VERSION = os.getenv("API_VERSION", "v22.0")
PORT = int(os.getenv("PORT", "8000"))

GRAPH_URL = f"https://graph.facebook.com/{API_VERSION}/{PHONE_NUMBER_ID}/messages" if PHONE_NUMBER_ID else ""

# WhatsApp Customer-Service Bot — Python + Official Meta Cloud API

A small, production-shaped demo of how I build a WhatsApp bot: a pure,
testable conversation brain, a thin Flask webhook, and a mockable API client.
Bilingual EN/ES out of the box, with interactive buttons.

> Try it in 10 seconds with no Meta account: `python demo.py --scripted`

## What it does

- Main menu: hours, services & pricing, location, quote flow, human handoff, FAQ
- `quote` / `cotizar` multi-step flow that collects name + need + city + budget
- `technician` / `técnico` handoff state (anything typed after is acknowledged)
- `menu` always returns home; `english` / `español` switches language per user
- Interactive reply buttons on the menu (falls back to text automatically)
- MOCK mode: runs and prints locally when no Meta credentials are set

Example business baked in: **TechFix Solutions** (PC repair, web dev,
WhatsApp bots, remote support). All copy lives in one `TEXTS` dict in
`bot_logic.py` — swap it for your business.

## How I structured it

```
app.py                  Flask webhook: Meta verification (GET) + events (POST)
bot_logic.py            Pure brain: process_message(user_id, text) -> str, no I/O
whatsapp_client.py      Cloud API wrapper with MOCK fallback (no creds = print)
config.py               Env loading + is_configured() check
demo.py                 Offline terminal demo (scripted + interactive)
tests/test_bot_logic.py Unit tests for menu, quote flow, handoff, i18n
examples/               Sample Meta webhook payload
```

Design choices I would defend in an interview:

1. **Logic has zero I/O.** `process_message` never touches HTTP or env,
   so it is unit-tested without mocks (`tests/`, 8 tests).
2. **State machine is explicit and tiny.** `user_sessions` dict with two
   states (`esperando_datos_cotizacion`, `derivado_asesor`). Easy to move to
   Redis/Postgres later without changing call sites.
3. **i18n is data, not branches.** One `TEXTS[lang]` dict; detection is a
   marker list + persisted per-user preference.
4. **Webhook never fails Meta.** `incoming()` always returns 200 (even on
   error) so Meta stops retrying poisoned events; real errors go to logs.
5. **MOCK by default.** No credentials → console output instead of API
   calls. Demoable in CI, interviews, and offline.

## Quickstart

```powershell
cd "wp bot"
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
copy .env.example .env
```

### 1. Offline demo (no WhatsApp, no Meta)

```powershell
python demo.py --scripted
python -m pytest -q
```

Expected: a full scripted conversation (ES quote flow + EN services) and
`8 passed`.

### 2. Local webhook

```powershell
python app.py
# http://localhost:8000/ -> "TechFix bot is running..."
```

Simulate a Meta event without WhatsApp (see `examples/`):

```powershell
curl -X POST http://localhost:8000/webhook `
  -H "Content-Type: application/json" `
  -d "@examples/webhook_text_message.json"
```

With empty `.env` you will see `[MOCK MODE] To ...` in the Flask console.
That proves `app.py -> bot_logic.py -> whatsapp_client.py` end to end.

### 3. Real WhatsApp (free Meta trial)

Meta cannot reach `localhost`, so expose it:

1. Get free credentials at https://developers.facebook.com/
   (Business app + WhatsApp product → `WHATSAPP_TOKEN`, `PHONE_NUMBER_ID`).
2. Invent a `VERIFY_TOKEN` and put all three in `.env`.
3. Expose: `ngrok http 8000` → `https://xxxx.ngrok-free.dev/webhook`.
4. Meta Dashboard → WhatsApp → Configuration → Webhook:
   paste the URL + same verify token → Verify → subscribe to `messages`.
5. Add your personal number as a test recipient, then send `hola` from your
   WhatsApp to the Meta test number.

Test script: `hola → 2 → cotizar → "Juan, laptop HP, CDMX, 3000" → 4 → menu`.

Common gotchas: test tokens expire in ~24h (regenerate + restart Flask);
ngrok free URLs change on restart (re-paste in Meta); first message must be
user → bot in trial mode.

## Configuration

| Var | Required | What |
|-----|----------|------|
| `VERIFY_TOKEN` | webhook only | Any long random string you invent; must match Meta dashboard |
| `WHATSAPP_TOKEN` | live sends | Test token from Meta API Setup (`EAAG...`) |
| `PHONE_NUMBER_ID` | live sends | Numeric ID of the Meta test number |
| `API_VERSION` | no | Default `v22.0` |
| `PORT` | no | Default `8000` |

Without `WHATSAPP_TOKEN` / `PHONE_NUMBER_ID` the app stays in MOCK mode —
safe for demos and CI.

## Deploy (when ngrok gets old)

Any host that runs `gunicorn app:app` works:

```bash
gunicorn app:app --bind 0.0.0.0:$PORT
```

Set the five env vars on Render / Railway / Fly.io, then point Meta's
webhook at `https://your-app/webhook` once (stable URL, no ngrok needed).

## Roadmap (what I would add next)

- [ ] Persist sessions + transcripts in SQLite/Postgres
- [ ] Notify the human (email/Telegram) on handoff with the transcript
- [ ] LLM fallback for free-text questions, keeping the menu as guardrails
- [ ] Template message for proactive outreach (24h window rule)
- [ ] Rate limiting + signature verification (`X-Hub-Signature-256`)

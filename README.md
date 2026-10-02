# Bot de Servicio al Cliente para WhatsApp (Python + API Oficial Meta)

Bot con menú interactivo para negocios de servicios. Funciona con la **WhatsApp Business Cloud API** (gratis y oficial).

## Funciones
- Menú principal: horarios, servicios/precios, ubicación, asesor, FAQ
- Comando `cotizar` para pedir datos de cotización
- Comando `asesor` para derivar a humano
- Botones interactivos de WhatsApp
- `menu` en cualquier momento para volver al inicio

## 1. Instalar

```powershell
cd "C:\Users\JUAN JOSE\Documents\PROYECTOS\Python\wp bot"
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
copy .env.example .env
```

Edita `.env` con tus datos (ver paso 2).

## 2. Conseguir credenciales gratis en Meta (5 min)

1. Ve a https://developers.facebook.com/ → Crear app → Tipo **Business** → Agrega producto **WhatsApp**.
2. En **API Setup** obtienes:
   - `WHATSAPP_TOKEN` (token temporal de prueba)
   - `PHONE_NUMBER_ID` (ID del número de prueba)
3. En `.env` pon:
   ```
   VERIFY_TOKEN=un_texto_que_tu_inventes_123
   WHATSAPP_TOKEN=pega_aqui_tu_token
   PHONE_NUMBER_ID=pega_aqui_tu_id
   ```
4. Personaliza tu negocio en `bot_logic.py` → diccionario `NEGOCIO_INFO`.

## 3. Probar local

```powershell
python app.py
```

Deberías ver: `🚀 Bot iniciado en http://localhost:8000`

Prueba la lógica sin WhatsApp:
```powershell
python -c "from bot_logic import procesar_mensaje; print(procesar_mensaje('123','hola')); print(procesar_mensaje('123','2'))"
```

## 4. Exponer a internet (Meta necesita URL pública)

Meta no puede llamar a `localhost`. Usa ngrok:

```powershell
ngrok http 8000
```

Te da una URL como `https://xxxx.ngrok-free.app`. Tu webhook será:
```
https://xxxx.ngrok-free.app/webhook
```

## 5. Conectar en Meta Dashboard

En WhatsApp → Configuration → Webhook:
- URL: `https://tu-url.ngrok-free.app/webhook`
- Verify token: el mismo `VERIFY_TOKEN` de tu `.env`
- Suscribir a campo `messages`.

Luego agrega tu número personal como destinatario de prueba y envía "hola" por WhatsApp al número de prueba de Meta.

## Estructura
- `app.py` → webhook Flask (verificación GET + recepción POST)
- `bot_logic.py` → menú y respuestas (¡edítalo!)
- `whatsapp_client.py` → envío a Cloud API
- `config.py` → lee `.env`

## Siguiente nivel
- Guardar conversaciones en SQLite/Postgres
- Avisar al asesor por email/Telegram cuando piden humano
- Agregar IA: conectar OpenAI para respuestas libres
- Desplegar en Render/Railway para no usar ngrok

Dime qué quieres agregar y lo implementamos.

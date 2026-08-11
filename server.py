"""
Komara AI Agent - Serveur Indépendant
FastAPI + Telegram Webhook + WhatsApp Bot
Aucune dépendance Base44 - 100% autonome
"""

import os
import json
import logging
from fastapi import FastAPI, Request
from fastapi.responses import PlainTextResponse
import httpx

# ============ CONFIG ============
BOT_TOKEN = os.environ.get("TELEGRAM_BOT_TOKEN_2", os.environ.get("TELEGRAM_BOT_TOKEN", ""))
TG_API = f"https://api.telegram.org/bot{BOT_TOKEN}"

# ============ RÉPONSES BOT ============
PRICES = """💰 *Tarifs Komara Agency*

🎨 Logo pro: 300k - 500k GNF
🖼 Affiche/Flyer: 300k GNF
📸 Retouche photo: sur discussion
🤖 Bots: sur devis
✨ Branding: sur devis
🎬 Montage vidéo: sur devis

✅ 2 révisions gratuites
💰 Révision sup: 50k GNF
⚡ Express 24h: +30%
💳 Orange Money, MTN, Virement, PayPal"""

WELCOME = """Salut ! 👋 Je suis le bot de Komara Agency 🇬🇳

On fait du logo, des affiches, de la retouche photo, des bots et des vidéos IA sur mesure.

Dis-moi ce qui t'intéresse 👇"""

KEYBOARD = {
    "inline_keyboard": [
        [{"text": "💰 Tarifs", "callback_data": "tarifs"}, {"text": "🛒 Commander", "callback_data": "commander"}],
        [{"text": "📞 Contact", "callback_data": "contact"}, {"text": "🎨 Portfolio", "callback_data": "portfolio"}],
        [{"text": "🎬 Vidéo IA", "callback_data": "video"}],
    ]
}

# ============ LOGIC ============
def detect_intent(text):
    t = (text or "").lower().strip()
    if t == "/start" or "bonjour" in t or "salut" in t or "salam" in t or "hello" in t:
        return "welcome"
    if "prix" in t or "tarif" in t or "combien" in t or "coût" in t or "cout" in t:
        return "tarifs"
    if "commander" in t or "commande" in t or "acheter" in t or "je veux" in t:
        return "commander"
    if "contact" in t or "numero" in t or "numéro" in t or "whatsapp" in t:
        return "contact"
    if "portfolio" in t or "travaux" in t or "exemple" in t:
        return "portfolio"
    if "logo" in t:
        return "logo"
    if "affiche" in t or "flyer" in t:
        return "affiche"
    if "vidéo" in t or "video" in t or "reel" in t or "reels" in t:
        return "video"
    if "délai" in t or "delai" in t or "combien de temps" in t:
        return "delai"
    if "merci" in t or "thanks" in t:
        return "merci"
    return "default"

async def handle_intent(chat_id, intent, client=None):
    responses = {
        "welcome": WELCOME,
        "tarifs": PRICES,
        "commander": "🛒 *Pour commander*, dis-moi:\n1. Le type de service\n2. Tes idées ou références\n3. Ton délai souhaité (normal ou express 24h)\n\nOn discute des détails et je te donne le prix exact 💬",
        "contact": "📞 *Contact Komara Agency*\n\nWhatsApp: +212 701-986219\nRéponse rapide garantie 🚀",
        "portfolio": "🎨 *Portfolio Komara Agency*\n\nDécouvre nos réalisations!\nDemande-moi des exemples de logos, affiches ou retouches 📸",
        "logo": "🎨 *Logo Pro*\n\nPrix: 300k - 500k GNF\nDélai: 2-3 jours (Express 24h: +30%)\nInclus: 2 révisions gratuites\n\nDis-moi le style que tu veux 👌",
        "affiche": "🖼 *Affiche/Flyer*\n\nPrix: 300k GNF\nDélai: 1-2 jours (Express 24h: +30%)\n\nEnvoie-moi le texte et les infos 🚀",
        "video": "🎬 *Vidéo IA Premium*\n\nGénération de vidéos IA ultra-réalistes:\n4 à 15 secondes, qualité 2K avec audio\n\n💰 Vidéo 6s: 500k GNF\n💰 Vidéo 10s: 800k GNF\n💰 Vidéo 15s: 1M GNF\n⚡ Express 24h: +30%\n\nDécris-moi la vidéo que tu veux 👇",
        "delai": "⏱ *Délais habituels*\n\nLogo: 2-3 jours\nAffiche: 1-2 jours\nRetouche: 24-48h\nVidéo IA: 24-72h\n\nExpress 24h disponible (+30%) ⚡",
        "merci": "Avec plaisir ! 😊\nKomara Agency 🇬🇳 — Vision. Impact. Excellence.",
        "default": "Je n'ai pas bien compris 🤔\n\nTape un mot-clé:\n1. Logo\n2. Affiche\n3. Retouche photo\n4. Vidéo IA\n5. Bots\n\nOu tape *prix*, *commander*, *contact* 👇",
    }
    msg = responses.get(intent, responses["default"])
    if client:
        await client.post(f"{TG_API}/sendMessage", json={
            "chat_id": chat_id,
            "text": msg,
            "parse_mode": "Markdown",
            "reply_markup": KEYBOARD,
        })

# ============ FASTAPI APP ============
app = FastAPI(title="Komara AI Agent", version="2.0")
logger = logging.getLogger("komara")

@app.get("/")
async def root():
    return {"status": "online", "bot": "Komara Agency", "version": "2.0"}

@app.get("/health")
async def health():
    return {"status": "healthy"}

@app.post(f"/telegram/{BOT_TOKEN}")
async def telegram_webhook(request: Request):
    """Webhook Telegram - réponse instantanée"""
    try:
        update = await request.json()
        async with httpx.AsyncClient(timeout=30) as client:
            if update.get("callback_query"):
                cq = update["callback_query"]
                chat_id = cq["message"]["chat"]["id"]
                await client.post(f"{TG_API}/answerCallbackQuery", json={"callback_query_id": cq["id"]})
                await handle_intent(chat_id, cq["data"], client)
            elif update.get("message"):
                msg = update["message"]
                chat_id = msg["chat"]["id"]
                text = msg.get("text", "")
                intent = detect_intent(text)
                await handle_intent(chat_id, intent, client)
        return {"ok": True}
    except Exception as e:
        logger.error(f"Telegram error: {e}")
        return {"ok": False, "error": str(e)}

@app.post("/whatsapp")
async def whatsapp_webhook(request: Request):
    """Webhook WhatsApp via Twilio"""
    try:
        form = await request.form()
        incoming_msg = form.get("Body", "")
        from_number = form.get("From", "")
        
        intent = detect_intent(incoming_msg)
        responses = {
            "welcome": WELCOME,
            "tarifs": PRICES,
            "commander": "🛒 Pour commander, dis-moi le type de service et tes idées 👇",
            "contact": "📞 WhatsApp: +212 701-986219",
            "default": "Je n'ai pas compris 🤔 Tape 'tarifs' ou 'commander'",
        }
        reply = responses.get(intent, responses["default"])
        
        twiml = f'<?xml version="1.0" encoding="UTF-8"?><Response><Message>{reply}</Message></Response>'
        return PlainTextResponse(twiml, media_type="text/xml")
    except Exception as e:
        logger.error(f"WhatsApp error: {e}")
        return PlainTextResponse(
            '<?xml version="1.0" encoding="UTF-8"?><Response><Message>Erreur temporaire</Message></Response>',
            media_type="text/xml"
        )

# ============ STARTUP ============
@app.on_event("startup")
async def set_telegram_webhook():
    """Configure le webhook Telegram au démarrage"""
    if not BOT_TOKEN:
        logger.warning("TELEGRAM_BOT_TOKEN not set")
        return
    server_url = os.environ.get("SERVER_URL", "")
    if server_url:
        async with httpx.AsyncClient() as client:
            webhook_url = f"{server_url}/telegram/{BOT_TOKEN}"
            resp = await client.post(f"{TG_API}/setWebhook", json={
                "url": webhook_url,
                "allowed_updates": ["message", "callback_query"],
            })
            logger.info(f"Webhook set: {resp.json()}")

if __name__ == "__main__":
    import uvicorn
    port = int(os.environ.get("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)

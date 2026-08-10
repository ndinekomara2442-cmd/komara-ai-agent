"""
Komara Agency - Telegram Bot
Webhook: https://base44.app/api/apps/6a52ee926419c166ff7bb13d/functions/telegramWebhook
Bot: @Komara_Agency_botbot
"""

import json
import requests

BOT_TOKEN = "YOUR_TELEGRAM_BOT_TOKEN"
TG_API = f"https://api.telegram.org/bot{BOT_TOKEN}"

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
💳 Paiement: Orange Money, MTN, Virement, PayPal"""

WELCOME = """Salut ! 👋 Je suis le bot de Komara Agency 🇬🇳

On fait du logo, des affiches, de la retouche photo et des bots sur mesure.

Dis-moi ce qui t'intéresse, ou choisis une option en dessous 👇"""

KEYBOARD = {
    "inline_keyboard": [
        [{"text": "💰 Tarifs", "callback_data": "tarifs"}, {"text": "🛒 Commander", "callback_data": "commander"}],
        [{"text": "📞 Contact", "callback_data": "contact"}, {"text": "🎨 Portfolio", "callback_data": "portfolio"}],
    ]
}

def send_message(chat_id, text, keyboard=None):
    body = {"chat_id": chat_id, "text": text, "parse_mode": "Markdown"}
    if keyboard:
        body["reply_markup"] = keyboard
    requests.post(f"{TG_API}/sendMessage", json=body)

def detect_intent(text):
    t = (text or "").lower().strip()
    if t == "/start" or "bonjour" in t or "salut" in t or "hello" in t:
        return "welcome"
    if "prix" in t or "tarif" in t or "combien" in t:
        return "tarifs"
    if "commander" in t or "commande" in t:
        return "commander"
    if "contact" in t or "whatsapp" in t:
        return "contact"
    if "portfolio" in t or "exemple" in t:
        return "portfolio"
    if "logo" in t:
        return "logo"
    if "affiche" in t or "flyer" in t:
        return "affiche"
    if "delai" in t or "délai" in t:
        return "delai"
    return "default"

def handle_intent(chat_id, intent):
    responses = {
        "welcome": WELCOME,
        "tarifs": PRICES,
        "commander": "🛒 Pour commander, dis-moi:\\n1. Le type de service\\n2. Tes idées\\n3. Ton délai",
        "contact": "📞 WhatsApp: +212 701-986219\\nRéponse rapide garantie 🚀",
        "portfolio": "🎨 Portfolio Komara Agency\\nDemande-moi des exemples 📸",
        "logo": "🎨 Logo Pro\\nPrix: 300k-500k GNF\\nDélai: 2-3 jours\\nExpress 24h: +30%",
        "affiche": "🖼 Affiche/Flyer\\nPrix: 300k GNF\\nDélai: 1-2 jours",
        "delai": "⏱ Logo: 2-3j\\nAffiche: 1-2j\\nExpress 24h: +30%",
    }
    send_message(chat_id, responses.get(intent, "Je n'ai pas compris 🤔 Choisis une option!"), KEYBOARD)

def handle_update(update):
    if "callback_query" in update:
        cq = update["callback_query"]
        chat_id = cq["message"]["chat"]["id"]
        requests.post(f"{TG_API}/answerCallbackQuery", json={"callback_query_id": cq["id"]})
        handle_intent(chat_id, cq["data"])
    elif "message" in update:
        msg = update["message"]
        chat_id = msg["chat"]["id"]
        intent = detect_intent(msg.get("text", ""))
        handle_intent(chat_id, intent)

if __name__ == "__main__":
    # Webhook mode
    import os
    update = json.loads(os.environ.get("UPDATE", "{}"))
    if update:
        handle_update(update)

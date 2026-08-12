"""
Komara AI Agent — Serveur Intelligent
FastAPI + Telegram Webhook + WhatsApp + IA Conversationnelle
Génération d'images via Pollinations.ai (100% gratuit)
Compréhension d'intentions via Hugging Face (Mistral-7B)
"""

import os
import json
import logging
import urllib.parse
import requests
import asyncio
from fastapi import FastAPI, Request, Response
from fastapi.responses import PlainTextResponse, JSONResponse
import httpx

# ============ CONFIG ============
BOT_TOKEN = os.environ.get("TELEGRAM_BOT_TOKEN_2", os.environ.get("TELEGRAM_BOT_TOKEN", ""))
TG_API = f"https://api.telegram.org/bot{BOT_TOKEN}"

HF_TOKEN = os.environ.get("HUGGING_FACE_ACCESS_TOKEN", os.environ.get("HF_TOKEN", ""))
HF_CHAT_MODEL = "mistralai/Mistral-7B-Instruct-v0.3"
HF_API_URL = f"https://api-inference.huggingface.co/models/{HF_CHAT_MODEL}"

KNOWLEDGE = {
    "name": "Komara Agency",
    "slogan": "Vision. Impact. Excellence.",
    "founder": "Ndine Komara",
    "whatsapp": "+212 701-986219",
    "email": "ndinekomara2442@gmail.com",
    "hours": "7j/7 de 8h à 22h (GMT)",
    "portfolio": "https://ndinekomara2442-cmd.github.io/komara-agency-portfolio/",
}

SYSTEM_PROMPT = f"""Tu es l'assistant virtuel de {KNOWLEDGE['name']} 🇬🇳, une agence de création visuelle premium.
Fondée par {KNOWLEDGE['founder']}. Slogan: {KNOWLEDGE['slogan']}.

SERVICES ET TARIFS:
- Logo Pro: 300k à 500k GNF, délai 2-3 jours
- Affiche & Flyer: 300k GNF, délai 1-2 jours
- Retouche Photo: prix sur discussion, 24-48h
- Bots WhatsApp/Telegram: sur devis
- Branding Complet: sur devis
- Vidéo IA / Montage: sur devis, 24-72h

CONDITIONS:
- Express 24h: +30%
- 2 révisions gratuites, puis 50k GNF par révision
- Paiement: Orange Money, MTN Money, Virement, PayPal

CONTACT:
- WhatsApp: {KNOWLEDGE['whatsapp']}
- Email: {KNOWLEDGE['email']}
- Horaires: {KNOWLEDGE['hours']}

STYLE:
- Chaleureux, pro, direct — pas robotique
- Concis: 2-5 lignes max
- 1-2 emojis max par message
- Si le client veut une image, dis-lui d'envoyer "genere: [description]"
- NE JAMAIS inventer des prix
- Propose toujours la prochaine étape
"""

logger = logging.getLogger("komara")
logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")

# ============ IA: RÉPONSE CONVERSATIONNELLE ============

async def ai_respond(user_message: str, chat_history: list = None) -> str:
    """
    Utilise Hugging Face (Mistral-7B) pour générer une réponse naturelle.
    Fallback sur détection locale si HF indisponible.
    """
    if HF_TOKEN:
        try:
            conversation = f"<s>[INST] {SYSTEM_PROMPT}\n\nMessage du client: {user_message} [/INST]"
            headers = {"Authorization": f"Bearer {HF_TOKEN}", "Content-Type": "application/json"}
            payload = {
                "inputs": conversation,
                "parameters": {
                    "max_new_tokens": 250,
                    "temperature": 0.7,
                    "top_p": 0.9,
                    "do_sample": True,
                    "return_full_text": False,
                },
            }
            async with httpx.AsyncClient(timeout=30) as client:
                resp = await client.post(HF_API_URL, headers=headers, json=payload)
                if resp.status_code == 200:
                    data = resp.json()
                    if isinstance(data, list) and data:
                        text = data[0].get("generated_text", "")
                        if text and len(text.strip()) > 5:
                            return text.strip()
                elif resp.status_code == 503:
                    logger.warning("HF model loading, using fallback")
        except Exception as e:
            logger.warning(f"HF API error: {e}, using fallback")
    return local_intent_response(user_message)


def local_intent_response(text: str) -> str:
    """Fallback: détection d'intent locale avec réponses naturelles."""
    t = text.lower().strip()

    if t.startswith("genere:") or t.startswith("crée:") or t.startswith("genere ") or t.startswith("cree "):
        return "📸 Envoie ta description après 'genere:'\nEx: genere logo luxury africain noir et or"

    if any(w in t for w in ["/start", "bonjour", "salut", "salam", "hello", "bonsoir"]):
        return ("Hey ! 👋 Bienvenue chez Komara Agency 🇬🇳\n\n"
                "On fait du logo, des affiches, retouche photo, branding et vidéos IA.\n"
                "Tu cherches quoi au juste ?")

    if any(w in t for w in ["prix", "tarif", "combien", "coût", "cout", "cher"]):
        return ("💰 Nos tarifs:\n\n"
                "🎨 Logo: 300k-500k GNF (2-3j)\n"
                "🖼️ Affiche: 300k GNF (1-2j)\n"
                "📸 Retouche: sur discussion\n"
                "🎬 Vidéo IA: sur devis\n"
                "🤖 Bots: sur devis\n\n"
                "⚡ Express 24h: +30% | 2 révisions gratuites\n\n"
                "Quel service t'intéresse ?")

    if any(w in t for w in ["commander", "commande", "acheter", "je veux"]):
        return ("Parfait ! 🛒 Pour te préparer un devis:\n\n"
                "1. Quel service? (logo, affiche, retouche...)\n"
                "2. Tes idées ou références\n"
                "3. Délai souhaité (normal ou express?)\n\n"
                "Dis-moi tout 👇")

    if any(w in t for w in ["contact", "numero", "numéro", "whatsapp", "joindre"]):
        return (f"📞 Contact:\n\n"
                f"WhatsApp: {KNOWLEDGE['whatsapp']}\n"
                f"Email: {KNOWLEDGE['email']}\n"
                f"Horaires: {KNOWLEDGE['hours']}\n\n"
                f"Réponse rapide garantie 🚀")

    if "logo" in t:
        return ("🎨 Logo Pro — 300k à 500k GNF\n\n"
                "Inclus: 2 révisions, délai 2-3 jours\n"
                "Tu as une idée du style? moderne, minimaliste, luxury?")

    if any(w in t for w in ["affiche", "flyer", "poster"]):
        return ("🖼️ Affiche & Flyer — 300k GNF\n\n"
                "Délai: 1-2 jours\n"
                "Envoie le texte et les infos à inclure 🚀")

    if any(w in t for w in ["retouche", "photo", "edit", "modifier"]):
        return ("📸 Retouche Photo\n\n"
                "Envoie ta photo et dis-moi ce que tu veux changer:\n"
                "Fond, lumière, couleurs, supprimer/ajouter des éléments\n\n"
                "Prix sur discussion selon le travail 👇")

    if any(w in t for w in ["vidéo", "video", "reel", "reels", "montage"]):
        return ("🎬 Vidéo IA & Montage\n\n"
                "Vidéos IA ultra-réalistes (4-15s, 2K) et reels\n\n"
                "Décris-moi ce que tu imagines 👇")

    if any(w in t for w in ["délai", "delai", "temps", "rapidement"]):
        return ("⏱️ Délais:\n\n"
                "Logo: 2-3j | Affiche: 1-2j | Retouche: 24-48h | Vidéo: 24-72h\n\n"
                "⚡ Express 24h: +30%")

    if any(w in t for w in ["merci", "thanks", "thank"]):
        return "Avec plaisir ! 😊 Komara Agency 🇬🇳 — Vision. Impact. Excellence."

    if any(w in t for w in ["portfolio", "travaux", "exemple", "réalisation"]):
        return (f"🎨 Voir nos réalisations:\n{KNOWLEDGE['portfolio']}\n\n"
                "Tu veux voir un style en particulier ?")

    return ("Je n'ai pas bien compris 🤔\n\n"
            "Tu peux demander:\n"
            "• 'prix' — voir les tarifs\n"
            "• Commander un service\n"
            "• 'genere: [description]' — générer une image IA\n"
            "• 'contact' — nous joindre\n\n"
            "Qu'est-ce qui t'intéresse ?")


# ============ GÉNÉRATION D'IMAGES ============

async def generate_image_pollinations(prompt: str, chat_id: str, client: httpx.AsyncClient):
    """Génère une image via Pollinations.ai (gratuit) et l'envoie sur Telegram."""
    enhanced = f"{prompt}, luxury African brand, noir and gold, cinematic lighting, 8k, photorealistic, premium quality"
    encoded = urllib.parse.quote(enhanced)
    url = f"https://image.pollinations.ai/prompt/{encoded}?width=768&height=1344&nologo=true"

    try:
        await client.post(f"{TG_API}/sendMessage", json={
            "chat_id": chat_id,
            "text": f"🎨 Génération en cours...\n📝 {prompt[:100]}\n⏳ ~10-15 secondes",
        })

        resp = await client.get(url, timeout=60)
        if resp.status_code == 200:
            import tempfile
            with tempfile.NamedTemporaryFile(suffix=".jpg", delete=False) as tmp:
                tmp.write(resp.content)
                tmp_path = tmp.name

            with open(tmp_path, "rb") as photo:
                files = {"photo": ("image.jpg", photo, "image/jpeg")}
                await client.post(
                    f"{TG_API}/sendPhoto",
                    data={"chat_id": chat_id, "caption": f"🎨 Komara Agency 🇬🇳\n📝 {prompt[:80]}"},
                    files=files,
                )
            os.unlink(tmp_path)
        else:
            await client.post(f"{TG_API}/sendMessage", json={
                "chat_id": chat_id,
                "text": "❌ Erreur de génération. Réessaie avec une description plus simple.",
            })
    except Exception as e:
        logger.error(f"Image gen error: {e}")
        await client.post(f"{TG_API}/sendMessage", json={
            "chat_id": chat_id,
            "text": "❌ Erreur temporaire. Réessaie dans quelques secondes.",
        })


# ============ KEYBOARD ============

INLINE_KEYBOARD = {
    "inline_keyboard": [
        [
            {"text": "💰 Tarifs", "callback_data": "tarifs"},
            {"text": "🛒 Commander", "callback_data": "commander"},
        ],
        [
            {"text": "📞 Contact", "callback_data": "contact"},
            {"text": "🎨 Portfolio", "callback_data": "portfolio"},
        ],
        [
            {"text": "🎬 Vidéo IA", "callback_data": "video"},
        ],
    ]
}

# ============ FASTAPI APP ============

app = FastAPI(title="Komara AI Agent", version="3.0")
chat_contexts: dict = {}

@app.get("/")
async def root():
    return {
        "status": "online",
        "bot": "Komara Agency 🇬🇳",
        "version": "3.0",
        "ai": "Mistral-7B" if HF_TOKEN else "local-intent",
        "image_gen": "Pollinations.ai",
    }

@app.get("/health")
async def health():
    return {"status": "healthy", "ai_enabled": bool(HF_TOKEN), "image_gen_enabled": True}

@app.post(f"/telegram/{BOT_TOKEN}")
async def telegram_webhook(request: Request):
    """Webhook Telegram — IA conversationnelle + génération d'images"""
    try:
        update = await request.json()
        async with httpx.AsyncClient(timeout=60) as client:

            # Callback query (boutons inline)
            if update.get("callback_query"):
                cq = update["callback_query"]
                chat_id = cq["message"]["chat"]["id"]
                await client.post(f"{TG_API}/answerCallbackQuery", json={"callback_query_id": cq["id"]})
                callback_map = {
                    "tarifs": "prix",
                    "commander": "je veux commander",
                    "contact": "contact",
                    "portfolio": "portfolio",
                    "video": "vidéo",
                }
                text = callback_map.get(cq.get("data", ""), cq.get("data", ""))
                response = await ai_respond(text, chat_contexts.get(chat_id, []))
                await client.post(f"{TG_API}/sendMessage", json={
                    "chat_id": chat_id, "text": response, "parse_mode": "HTML",
                })
                return {"ok": True}

            # Message texte
            if update.get("message"):
                msg = update["message"]
                chat_id = msg["chat"]["id"]
                text = msg.get("text", "").strip()
                if not text:
                    return {"ok": True}

                lower = text.lower()

                # Détection: génération d'image
                if lower.startswith("genere:") or lower.startswith("crée:") or lower.startswith("genere ") or lower.startswith("cree "):
                    if ":" in text:
                        prompt = text.split(":", 1)[-1].strip()
                    else:
                        prompt = text.split(" ", 1)[-1].strip() if " " in text else ""
                    if len(prompt) < 3:
                        await client.post(f"{TG_API}/sendMessage", json={
                            "chat_id": chat_id,
                            "text": "📝 Envoie une description après 'genere:'\nEx: genere logo luxury africain noir et or",
                        })
                        return {"ok": True}
                    await generate_image_pollinations(prompt, chat_id, client)
                    return {"ok": True}

                # Réponse IA conversationnelle
                history = chat_contexts.get(chat_id, [])
                response = await ai_respond(text, history)
                history.append({"user": text, "bot": response})
                chat_contexts[chat_id] = history[-5:]

                await client.post(f"{TG_API}/sendMessage", json={
                    "chat_id": chat_id,
                    "text": response,
                    "parse_mode": "HTML",
                    "reply_markup": INLINE_KEYBOARD,
                })
                return {"ok": True}

        return {"ok": True}
    except Exception as e:
        logger.error(f"Telegram error: {e}")
        return {"ok": False, "error": str(e)}

@app.post("/whatsapp")
async def whatsapp_webhook(request: Request):
    """Webhook WhatsApp via Twilio — IA conversationnelle"""
    try:
        form = await request.form()
        incoming_msg = form.get("Body", "")
        response = await ai_respond(incoming_msg)
        twiml = f'<?xml version="1.0" encoding="UTF-8"?><Response><Message>{response}</Message></Response>'
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
            await client.post(f"{TG_API}/setMyCommands", json={
                "commands": [
                    {"command": "start", "description": "Démarrer / Accueil"},
                    {"command": "prix", "description": "Voir les tarifs"},
                    {"command": "contact", "description": "Nous contacter"},
                    {"command": "genere", "description": "Générer une image IA"},
                ]
            })
    else:
        logger.warning("SERVER_URL not set — webhook not configured")

if __name__ == "__main__":
    import uvicorn
    port = int(os.environ.get("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)

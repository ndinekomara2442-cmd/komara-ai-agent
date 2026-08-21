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

# Groq — gratuit, ultra-rapide (get key: https://console.groq.com/keys)
GROQ_TOKEN = os.environ.get("GROQ_API_KEY", "")
GROQ_MODEL = "llama-3.1-8b-instant"
GROQ_API_URL = "https://api.groq.com/openai/v1/chat/completions"

# Gemini — Google AI (get key: https://aistudio.google.com/apikey)
GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY", "")
# Liste de modèles Gemini en cascade (du meilleur au plus stable)
GEMINI_MODELS = [
    "gemini-2.5-flash",
    "gemini-2.0-flash",
    "gemini-1.5-flash",
]
GEMINI_API_BASE = "https://generativelanguage.googleapis.com/v1beta"

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

async def call_gemini(user_message: str, chat_history: list = None) -> str | None:
    """IA principale: Gemini (Google AI) avec cascade de modèles."""
    if not GEMINI_API_KEY:
        return None

    # Construire l'historique de conversation pour Gemini
    contents = []
    if chat_history:
        for msg in chat_history[-5:]:  # Garder les 5 derniers échanges
            contents.append({"role": "user", "parts": [{"text": msg.get("user", "")}]})
            contents.append({"role": "model", "parts": [{"text": msg.get("bot", "")}]})
    contents.append({"role": "user", "parts": [{"text": user_message}]})

    for model_name in GEMINI_MODELS:
        url = f"{GEMINI_API_BASE}/models/{model_name}:generateContent?key={GEMINI_API_KEY}"
        payload = {
            "contents": contents,
            "systemInstruction": {"parts": [{"text": SYSTEM_PROMPT}]},
            "generationConfig": {
                "maxOutputTokens": 300,
                "temperature": 0.7,
                "topP": 0.9,
            },
        }

        try:
            transport = httpx.AsyncHTTPTransport(retries=2, local_address="0.0.0.0")
            async with httpx.AsyncClient(timeout=25, transport=transport) as client:
                resp = await client.post(url, json=payload)
                if resp.status_code == 200:
                    data = resp.json()
                    candidates = data.get("candidates", [])
                    if candidates:
                        parts = candidates[0].get("content", {}).get("parts", [])
                        for part in parts:
                            text = part.get("text", "").strip()
                            # Ignorer les parts de "thinking"
                            if part.get("thought"):
                                continue
                            if text and len(text) > 5:
                                return text
                else:
                    logger.warning(f"Gemini {model_name} HTTP {resp.status_code}: {resp.text[:200]}")
        except Exception as e:
            logger.warning(f"Gemini {model_name} error: {e}")

    return None


async def call_huggingface(user_message: str) -> str | None:
    """Appelle Mistral-7B via Hugging Face, avec retry (résilient aux blips DNS/réseau)."""
    if not HF_TOKEN:
        return None

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

    for attempt in range(3):
        try:
            # transport avec retries intégrés + force IPv4 (évite les blips DNS/IPv6 sur Railway)
            transport = httpx.AsyncHTTPTransport(retries=2, local_address="0.0.0.0")
            async with httpx.AsyncClient(timeout=30, transport=transport) as client:
                resp = await client.post(HF_API_URL, headers=headers, json=payload)
                if resp.status_code == 200:
                    data = resp.json()
                    if isinstance(data, list) and data:
                        text = data[0].get("generated_text", "")
                        if text and len(text.strip()) > 5:
                            return text.strip()
                    return None
                elif resp.status_code == 503:
                    logger.warning(f"HF model loading (tentative {attempt+1}/3)")
                    await asyncio.sleep(2)
                    continue
                else:
                    logger.warning(f"HF HTTP {resp.status_code}: {resp.text[:200]}")
                    return None
        except Exception as e:
            logger.warning(f"HF API error (tentative {attempt+1}/3): {e}")
            await asyncio.sleep(1)
            continue
    return None


async def call_groq(user_message: str) -> str | None:
    """Fallback IA #2: Groq (gratuit, ultra-rapide, nécessite clé)."""
    if not GROQ_TOKEN:
        return None
    try:
        transport = httpx.AsyncHTTPTransport(retries=2, local_address="0.0.0.0")
        async with httpx.AsyncClient(timeout=20, transport=transport) as client:
            resp = await client.post(
                GROQ_API_URL,
                headers={
                    "Authorization": f"Bearer {GROQ_TOKEN}",
                    "Content-Type": "application/json",
                },
                json={
                    "model": GROQ_MODEL,
                    "messages": [
                        {"role": "system", "content": SYSTEM_PROMPT},
                        {"role": "user", "content": user_message},
                    ],
                    "max_tokens": 250,
                    "temperature": 0.7,
                },
            )
            if resp.status_code == 200:
                data = resp.json()
                text = data.get("choices", [{}])[0].get("message", {}).get("content", "")
                if text and len(text.strip()) > 5:
                    return text.strip()
            else:
                logger.warning(f"Groq HTTP {resp.status_code}: {resp.text[:200]}")
    except Exception as e:
        logger.warning(f"Groq API error: {e}")
    return None


async def ai_respond(user_message: str, chat_history: list = None) -> str:
    """
    Cascade IA: Gemini (Google) -> Groq -> Hugging Face -> fallback local.
    """
    # 1. Gemini (priorité — le plus stable avec clé API)
    text = await call_gemini(user_message, chat_history)
    if text:
        return text

    # 2. Groq (ultra-rapide, gratuit)
    text = await call_groq(user_message)
    if text:
        return text

    # 3. Hugging Face (gratuit, peut être lent)
    text = await call_huggingface(user_message)
    if text:
        return text

    logger.warning("Tous les fournisseurs IA ont échoué, utilisation du fallback local intelligent")
    return smart_respond(user_message)


def smart_respond(text: str) -> str:
    """Moteur de réponse contextuelle intelligent — pas robotique."""
    t = text.lower().strip()
    original = text.strip()

    # === DÉTECTION: Génération d'image ===
    if any(t.startswith(p) for p in ["genere:", "crée:", "genere ", "cree ", "generez", "dessine"]):
        return "📸 Envoie ta description après 'genere:'\nEx: genere logo luxury africain noir et or"

    # === DÉTECTION: Accueil ===
    greetings = ["/start", "bonjour", "salut", "salam", "hello", "bonsoir", "coucou", "hey", "cc"]
    if any(t == g or t.startswith(g) for g in greetings) or t in ["/start"]:
        # Réponse dynamique selon l'heure
        hour = __import__("datetime").datetime.utcnow().hour
        if 5 <= hour < 12:
            phase = "Bonjour"
        elif 12 <= hour < 18:
            phase = "Bon après-midi"
        elif 18 <= hour < 22:
            phase = "Bonsoir"
        else:
            phase = "Salut"
        return (f"{phase} ! 👋 Bienvenue chez Komara Agency 🇬🇳\n\n"
                "On fait du logo, des affiches, retouche photo, branding et vidéos IA.\n"
                "Dis-moi ce que tu cherches, je te guide.")

    # === DÉTECTION: Question d'identité ===
    identity_words = ["tu es qui", "qui es-tu", "qui es tu", "c'est qui", "qui êtes vous",
                      "comment tu t'appelles", "ton nom", "présente", "presente", "que fais",
                      "que faites", "vos services", "tu fais quoi"]
    if any(w in t for w in identity_words):
        return ("Je suis l'assistant de Komara Agency 🇬🇳\n"
                "On crée des logos, affiches, retouches photo, branding et vidéos IA.\n"
                "Tu cherches quelque chose en particulier ?")

    # === DÉTECTION: Tarifs ===
    price_words = ["prix", "tarif", "combien", "coût", "cout", "cher", "coute", "coûte", "gratuit"]
    if any(w in t for w in price_words):
        # Détecter si un service spécifique est mentionné
        if "logo" in t:
            return ("Le logo Pro c'est 300k à 500k GNF selon la complexité.\n"
                    "2 révisions incluses, livré en 2-3 jours.\n"
                    "Tu as une idée du style que tu veux ?")
        if any(w in t for w in ["affiche", "flyer", "poster"]):
            return ("L'affiche ou flyer c'est 300k GNF, livré en 1-2 jours.\n"
                    "Tu as le texte et les infos prêtes ?")
        if any(w in t for w in ["retouche", "photo"]):
            return ("La retouche photo, le prix dépend du travail.\n"
                    "Dis-moi ce que tu veux changer, je te donne un prix juste.")
        if any(w in t for w in ["vidéo", "video", "reel"]):
            return ("La vidéo IA c'est sur devis — ça dépend de la durée et la complexité.\n"
                    "Décris-moi ton idée, je te chiffrage ça.")
        # Prix général
        return ("💰 Voici nos tarifs:\n\n"
                "🎨 Logo: 300k-500k GNF (2-3j)\n"
                "🖼️ Affiche: 300k GNF (1-2j)\n"
                "📸 Retouche: sur discussion\n"
                "🎬 Vidéo IA: sur devis\n"
                "🤖 Bots: sur devis\n\n"
                "⚡ Express 24h: +30% | 2 révisions gratuites\n\n"
                "Quel service t'intéresse ?")

    # === DÉTECTION: Commander ===
    order_words = ["commander", "commande", "acheter", "je veux", "je cherche", "j'ai besoin",
                   "je voudrais", "je souhaite", "je cherche un", "je cherche une"]
    if any(w in t for w in order_words):
        # Extraire ce que le client cherche
        service = ""
        for s in ["logo", "affiche", "flyer", "poster", "retouche", "photo", "vidéo", "video",
                   "reel", "branding", "bot", "site", "website", "carte", "menu"]:
            if s in t:
                service = s
                break
        if service:
            return (f"Super, je te prépare ça ! 🛒\n\n"
                    f"Pour le {service}, dis-moi:\n"
                    f"1. Ton style ou idée\n"
                    f"2. Ton délai (normal ou express 24h ?)\n"
                    f"3. Toutes les infos utiles\n\n"
                    f"Je te donne un prix précis après ça 👇")
        return ("Super ! 🛒 Pour te préparer un devis précis, dis-moi:\n\n"
                "1. Quel service? (logo, affiche, retouche, vidéo...)\n"
                "2. Tes idées ou références\n"
                "3. Délai souhaité (normal ou express?)\n\n"
                "Je t'écoute 👇")

    # === DÉTECTION: Contact ===
    contact_words = ["contact", "numero", "numéro", "whatsapp", "joindre", "appeler",
                     "téléphone", "telephone", "email", "mail", "où vous trouver", "ou vous trouver"]
    if any(w in t for w in contact_words):
        return (f"📞 Voici comment nous joindre:\n\n"
                f"WhatsApp: {KNOWLEDGE['whatsapp']}\n"
                f"Email: {KNOWLEDGE['email']}\n"
                f"Horaires: {KNOWLEDGE['hours']}\n\n"
                f"Réponse rapide garantie 🚀")

    # === DÉTECTION: Services spécifiques ===
    if "logo" in t:
        # Extraire le style mentionné
        styles = {"moderne": "moderne", "minimaliste": "minimaliste", "luxury": "luxury",
                  "classique": "classique", "africain": "africain", "3d": "3D", "animé": "animé"}
        found_styles = [s for w, s in styles.items() if w in t]
        if found_styles:
            return (f"Logo {', '.join(found_styles)} — bonne choix ! 🎨\n\n"
                    f"Prix: 300k-500k GNF selon la complexité\n"
                    f"Délai: 2-3 jours, 2 révisions incluses\n\n"
                    f"Tu as déjà une idée précise ou tu veux qu'on en discute ?")
        return ("🎨 Logo Pro — 300k à 500k GNF\n"
                "2 révisions incluses, livré en 2-3 jours.\n"
                "Tu as une idée du style? moderne, minimaliste, luxury, africain?")

    if any(w in t for w in ["affiche", "flyer", "poster"]):
        return ("🖼️ Affiche & Flyer — 300k GNF, livré en 1-2 jours.\n"
                "Envoie-moi le texte, les infos et le style que tu veux 🚀")

    if any(w in t for w in ["retouche", "photo", "edit", "modifier", "restaurer", "améliorer", "ameliorer"]):
        return ("📸 Envoie ta photo et dis-moi ce que tu veux changer:\n"
                "Fond, lumière, couleurs, supprimer/ajouter un élément, restauration...\n\n"
                "Je te donne un prix selon le travail 👇")

    if any(w in t for w in ["vidéo", "video", "reel", "reels", "montage", "tiktok"]):
        return ("🎬 Vidéo IA & Montage\n"
                "Vidéos ultra-réalistes (4-15s, 2K) et reels pour réseaux sociaux.\n\n"
                "Décris-moi ton idée, je te dis ce qui est possible 👇")

    if any(w in t for w in ["branding", "identité", "identite", "charte", "brand"]):
        return ("✨ Branding complet — identité visuelle de A à Z.\n"
                "Logo, couleurs, typographie, cartes, templates...\n"
                "Sur devis selon le scope. Tu veux qu'on en discute ?")

    if any(w in t for w in ["bot", "robot", "automatisation", "automat"]):
        return ("🤖 On crée des bots WhatsApp et Telegram sur mesure.\n"
                "Sur devis selon les fonctionnalités.\n"
                "Tu veux un bot pour quoi faire ?")

    # === DÉTECTION: Délais ===
    delay_words = ["délai", "delai", "combien de temps", "rapidement", "quand", "urgence"]
    if any(w in t for w in delay_words):
        return ("⏱️ Délais:\n"
                "Logo: 2-3j | Affiche: 1-2j | Retouche: 24-48h | Vidéo: 24-72h\n\n"
                "⚡ Express 24h: +30% — t'es pressé ?")

    # === DÉTECTION: Gratitude ===
    if any(w in t for w in ["merci", "thanks", "thank", "cool", "super", "génial", "genial", "nickel", "parfait"]):
        return "Avec plaisir ! 😊 Komara Agency 🇬🇳 — Vision. Impact. Excellence.\nTu as besoin d'autre chose ?"

    # === DÉTECTION: Portfolio ===
    if any(w in t for w in ["portfolio", "travaux", "exemple", "réalisation", "realisation", "voir", "montrer"]):
        return (f"🎨 Découvre nos réalisations:\n{KNOWLEDGE['portfolio']}\n\n"
                "Tu veux voir un style en particulier ?")

    # === DÉTECTION: Questions générales (qui, quoi, comment, pourquoi) ===
    question_words = ["qui", "quoi", "comment", "pourquoi", "où", "ou", "est-ce", "c'est quoi", "que"]
    if any(t.startswith(w) or f" {w} " in f" {t} " for w in question_words):
        # Question générale — rediriger intelligemment
        return ("Bonne question ! 🤔\n\n"
                "Je peux t'aider avec nos services: logo, affiche, retouche, vidéo, branding.\n"
                "Tu peux aussi taper 'prix' pour les tarifs ou 'contact' pour nous joindre.\n\n"
                "Dis-moi ce que tu cherches exactement 👇")

    # === FALLBACK: Message non compris ===
    # Analyser la longueur pour adapter la réponse
    if len(t) < 10:
        return ("Je n'ai pas bien compris ça 🤔\n\n"
                "Tape 'prix' pour les tarifs, 'contact' pour nous joindre,\n"
                "ou 'genere: [description]' pour créer une image IA.")
    return (f"Je vois que tu parles de \"{original[:50]}\" 🤔\n\n"
            "Je peux t'aider avec: logo, affiche, retouche photo, vidéo IA, branding.\n"
            "Tape 'prix' pour les tarifs ou 'contact' pour nous joindre.\n\n"
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
processed_updates: set = set()  # anti-doublon Telegram (retry webhook)
MAX_PROCESSED = 2000

@app.get("/")
async def root():
    return {
        "status": "online",
        "bot": "Komara Agency 🇬🇳",
        "version": "3.0",
        "ai": "Gemini" if GEMINI_API_KEY else ("Groq" if GROQ_TOKEN else ("Mistral-7B" if HF_TOKEN else "local-intent")),
        "image_gen": "Pollinations.ai",
    }

@app.get("/debug/ai")
async def debug_ai():
    """Diagnostic temporaire: teste chaque fournisseur IA et renvoie le résultat/erreur."""
    result = {}

    # Test Gemini (capture l'erreur réelle sans passer par le warning silencieux)
    if GEMINI_API_KEY:
        gemini_errors = []
        gemini_success = None
        for model_name in GEMINI_MODELS:
            url = f"{GEMINI_API_BASE}/models/{model_name}:generateContent?key={GEMINI_API_KEY}"
            payload = {
                "contents": [{"role": "user", "parts": [{"text": "dis bonjour en un mot"}]}],
                "generationConfig": {"maxOutputTokens": 50},
            }
            try:
                async with httpx.AsyncClient(timeout=20) as client:
                    resp = await client.post(url, json=payload)
                    if resp.status_code == 200:
                        gemini_success = model_name
                        break
                    else:
                        gemini_errors.append(f"{model_name}: HTTP {resp.status_code} - {resp.text[:200]}")
            except Exception as e:
                gemini_errors.append(f"{model_name}: {type(e).__name__}: {e}")
        result["gemini"] = {"key_set": True, "success_model": gemini_success, "errors": gemini_errors}
    else:
        result["gemini"] = {"key_set": False}

    # Test Groq
    if GROQ_TOKEN:
        try:
            async with httpx.AsyncClient(timeout=15) as client:
                resp = await client.post(
                    GROQ_API_URL,
                    headers={"Authorization": f"Bearer {GROQ_TOKEN}", "Content-Type": "application/json"},
                    json={"model": GROQ_MODEL, "messages": [{"role": "user", "content": "dis bonjour en un mot"}], "max_tokens": 20},
                )
                result["groq"] = {"key_set": True, "status": resp.status_code, "body": resp.text[:200]}
        except Exception as e:
            result["groq"] = {"key_set": True, "error": f"{type(e).__name__}: {e}"}
    else:
        result["groq"] = {"key_set": False}

    result["hf"] = {"key_set": bool(HF_TOKEN)}
    return result


@app.get("/debug/models")
async def debug_models():
    """Liste les modèles réellement disponibles avec les clés configurées."""
    out = {}
    if GEMINI_API_KEY:
        try:
            async with httpx.AsyncClient(timeout=15) as client:
                resp = await client.get(f"{GEMINI_API_BASE}/models?key={GEMINI_API_KEY}")
                if resp.status_code == 200:
                    data = resp.json()
                    models = [m["name"] for m in data.get("models", [])
                              if "generateContent" in m.get("supportedGenerationMethods", [])]
                    out["gemini_models"] = models
                else:
                    out["gemini_models_error"] = resp.text[:300]
        except Exception as e:
            out["gemini_models_error"] = str(e)
    if GROQ_TOKEN:
        try:
            async with httpx.AsyncClient(timeout=15) as client:
                resp = await client.get("https://api.groq.com/openai/v1/models",
                                          headers={"Authorization": f"Bearer {GROQ_TOKEN}"})
                if resp.status_code == 200:
                    data = resp.json()
                    out["groq_models"] = [m["id"] for m in data.get("data", [])]
                else:
                    out["groq_models_error"] = resp.text[:300]
        except Exception as e:
            out["groq_models_error"] = str(e)
    return out


@app.get("/health")
async def health():
    return {"status": "healthy", "ai_enabled": bool(GEMINI_API_KEY or GROQ_TOKEN or HF_TOKEN), "image_gen_enabled": True}

@app.post(f"/telegram/{BOT_TOKEN}")
async def telegram_webhook(request: Request):
    """Webhook Telegram — IA conversationnelle + génération d'images"""
    try:
        update = await request.json()

        # Anti-doublon: Telegram peut renvoyer le même update si la réponse est lente
        update_id = update.get("update_id")
        if update_id is not None:
            if update_id in processed_updates:
                logger.info(f"Update {update_id} déjà traité, ignoré (doublon)")
                return {"ok": True}
            processed_updates.add(update_id)
            if len(processed_updates) > MAX_PROCESSED:
                # Purge simple pour éviter une fuite mémoire
                processed_updates.clear()
                processed_updates.add(update_id)

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

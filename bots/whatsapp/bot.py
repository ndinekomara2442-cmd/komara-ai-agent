"""
Komara Agency - WhatsApp Business Bot
Number: +212 701-986219
Configuré via WhatsApp Business API
"""

WELCOME = """Bonjour 👋 Merci de contacter Komara Agency 🇬🇳

Nos services:
1. Logo pro (300k-500k GNF)
2. Affiche/Flyer (300k GNF)
3. Retouche photo
4. Bots sur mesure

Répondez par le numéro de votre choix 👆"""

QUICK_REPLIES = [
    "💰 Voir les tarifs",
    "🛒 Commander",
    "📞 Nous contacter",
    "🎨 Voir le portfolio",
]

def detect_intent(text):
    t = text.lower().strip()
    if any(w in t for w in ["bonjour", "salut", "hello"]):
        return "welcome"
    if any(w in t for w in ["prix", "tarif", "combien"]):
        return "tarifs"
    if "commander" in t or "commande" in t:
        return "commander"
    return "default"

def get_response(intent):
    responses = {
        "welcome": WELCOME,
        "tarifs": "💰 Logo: 300k-500k GNF\n🖼 Affiche: 300k GNF\n⚡ Express 24h: +30%\n💳 Orange Money, MTN, PayPal",
        "commander": "🛒 Pour commander:\n1. Type de service\n2. Vos idées\n3. Délai souhaité\n\nEnvoyez ces infos ici 👇",
        "default": "Je n'ai pas bien compris 🤔 Tapez 'tarifs' ou 'commander'",
    }
    return responses.get(intent, responses["default"])

if __name__ == "__main__":
    # Example usage
    print(get_response("welcome"))

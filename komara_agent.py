"""
Komara AI Agent — Agent IA pour Komara Agency
Agent conversationnel autonome pour la gestion client et le conseil créatif.
Auteur: Ndine Komara
Version: 1.0.0
"""

import json
import os
import datetime
import random
from typing import Dict, List, Optional, Tuple


class KomaraAgent:
    """
    Agent IA autonome pour Komara Agency.
    Gère les conversations client, conseille sur les services,
    et oriente vers les solutions adaptées.
    """

    def __init__(self, api_key: str = None):
        self.name = "Komara AI"
        self.version = "1.0.0"
        self.api_key = api_key or os.getenv("OPENAI_API_KEY") or os.getenv("GEMINI_API_KEY")
        self.conversation_history: List[Dict] = []
        self.user_context: Dict = {}
        self.load_knowledge()

    # ==================== BASE DE CONNAISSANCE ====================

    def load_knowledge(self):
        """Charge la base de connaissances de Komara Agency"""
        self.knowledge = {
            "agency": {
                "name": "Komara Agency",
                "slogan": "Vision. Impact. Excellence.",
                "founder": "Ndine Komara",
                "location": "Guinée / Maroc",
                "whatsapp": "+212 701-986219",
                "email": "ndinekomara2442@gmail.com",
                "portfolio": "https://ndinekomara2442-cmd.github.io/komara-agency-portfolio/",
                "hours": "7j/7 de 8h à 22h (GMT)",
            },
            "services": {
                "logo": {
                    "name": "Logo Pro",
                    "price": "300k - 500k GNF",
                    "delivery": "48h-72h",
                    "revisions": "2 gratuites",
                    "express": "+30% (24h)",
                    "description": "Logo unique et sur mesure pour ta marque",
                },
                "affiche": {
                    "name": "Affiche & Flyer",
                    "price": "300k GNF",
                    "delivery": "24h-48h",
                    "revisions": "2 gratuites",
                    "express": "+30% (24h)",
                    "description": "Design percutant pour tes événements et promos",
                },
                "retouche": {
                    "name": "Retouche Photo",
                    "price": "sur discussion",
                    "delivery": "24h-48h",
                    "revisions": "2 gratuites",
                    "description": "Retouche pro: fond, lumière, couleur, peau. Rendu 8K",
                },
                "bots": {
                    "name": "Bots WhatsApp / Telegram",
                    "price": "sur devis",
                    "delivery": "sur discussion",
                    "description": "Automatisation: bienvenue, réponses auto, relances",
                },
                "branding": {
                    "name": "Branding Complet",
                    "price": "sur devis",
                    "delivery": "sur discussion",
                    "description": "Identité visuelle: logo, couleurs, typographie, guidelines",
                },
                "video": {
                    "name": "Montage Vidéo / Reels",
                    "price": "sur devis",
                    "delivery": "24h-72h",
                    "description": "Reels Instagram, TikTok, vidéos promos",
                },
            },
            "pricing": {
                "logo": "300k - 500k GNF",
                "affiche": "300k GNF",
                "retouche": "sur discussion",
                "bots": "sur devis",
                "branding": "sur devis",
                "video": "sur devis",
                "express_surcharge": "+30%",
                "free_revisions": 2,
                "extra_revision_cost": "50k GNF",
            },
            "payment": ["Orange Money", "MTN Money", "Virement bancaire", "PayPal"],
            "languages": ["Français", "Soussou", "Malinké"],
        }

    # ==================== INTENTION DETECTION ====================

    def detect_intent(self, message: str) -> Tuple[str, float]:
        """Détecte l'intention de l'utilisateur à partir du message"""
        msg = message.lower().strip()

        intents = {
            "greeting": ["salut", "bonjour", "salam", "hello", "bonsoir", "slt", "cc", "hi", "salamu"],
            "logo_info": ["logo", "logotype", "identité", "marque"],
            "affiche_info": ["affiche", "flyer", "poster", "événement", "event"],
            "retouche_info": ["retouche", "photo", "éditer", "modifier photo", "fond"],
            "bots_info": ["bot", "automatisation", "whatsapp bot", "telegram"],
            "branding_info": ["branding", "charte", "identité visuelle", "couleurs"],
            "video_info": ["vidéo", "video", "reel", "reels", "montage", "tiktok", "instagram"],
            "pricing": ["prix", "tarif", "combien", "coût", "cout", "price", "cher"],
            "order": ["commander", "commande", "je veux", "je prends", "acheter", "réserver"],
            "payment": ["payer", "paiement", "payment", "orange money", "mtn", "virement", "paypal"],
            "delivery": ["délai", "delai", "quand", "rapidement", "urgent"],
            "revision": ["révision", "revision", "modifier", "changer", "correction"],
            "contact": ["contact", "téléphone", "numero", "numéro", "joindre", "appeler"],
            "portfolio": ["portfolio", "site", "website", "voir vos travaux", "galerie"],
            "thanks": ["merci", "thanks", "thank you", "cool", "super"],
            "bye": ["au revoir", "bye", "à bientôt", "ciao", "tchao"],
        }

        scores = {}
        for intent, keywords in intents.items():
            score = sum(1 for kw in keywords if kw in msg)
            if score > 0:
                scores[intent] = score

        if not scores:
            return ("unknown", 0.0)

        best_intent = max(scores, key=scores.get)
        confidence = scores[best_intent] / max(len(msg.split()), 1)

        return (best_intent, min(confidence, 1.0))

    # ==================== GÉNÉRATION DE RÉPONSES ====================

    def generate_response(self, message: str) -> str:
        """Génère une réponse selon l'intention détectée"""
        intent, confidence = self.detect_intent(message)

        # Sauvegarder dans l'historique
        self.conversation_history.append({
            "role": "user",
            "content": message,
            "timestamp": datetime.datetime.now().isoformat(),
            "intent": intent,
        })

        response = self._get_response_by_intent(intent, message)

        self.conversation_history.append({
            "role": "agent",
            "content": response,
            "timestamp": datetime.datetime.now().isoformat(),
        })

        return response

    def _get_response_by_intent(self, intent: str, message: str) -> str:
        """Retourne la réponse appropriée selon l'intention"""

        if intent == "greeting":
            return self._greeting_response()

        elif intent == "logo_info":
            return self._service_response("logo")

        elif intent == "affiche_info":
            return self._service_response("affiche")

        elif intent == "retouche_info":
            return self._service_response("retouche")

        elif intent == "bots_info":
            return self._service_response("bots")

        elif intent == "branding_info":
            return self._service_response("branding")

        elif intent == "video_info":
            return self._service_response("video")

        elif intent == "pricing":
            return self._pricing_response()

        elif intent == "order":
            return self._order_response(message)

        elif intent == "payment":
            return self._payment_response()

        elif intent == "delivery":
            return self._delivery_response()

        elif intent == "revision":
            return self._revision_response()

        elif intent == "contact":
            return self._contact_response()

        elif intent == "portfolio":
            return self._portfolio_response()

        elif intent == "thanks":
            return "Avec plaisir ! 😊\nN'hésite pas si tu as d'autres questions.\n\nKomara Agency 🇬🇳 — Vision. Impact. Excellence."

        elif intent == "bye":
            return "À bientôt ! 👋\nKomara Agency 🇬🇳\nTu peux nous rejoindre sur WhatsApp: +212 701-986219"

        else:
            return self._default_response()

    def _greeting_response(self) -> str:
        return (
            f"Salut ! 👋 Bienvenue chez {self.knowledge['agency']['name']} 🇬🇳\n\n"
            f"Je suis {self.knowledge['agency']['founder']}, ton créateur digital.\n"
            f"Voici ce que je propose :\n\n"
            f"1. 🎨 Logo pro\n"
            f"2. 🖼️ Affiche & Flyer\n"
            f"3. 📸 Retouche photo\n"
            f"4. 🤖 Bots WhatsApp/Telegram\n"
            f"5. ✨ Branding complet\n"
            f"6. 🎬 Montage vidéo/Reels\n\n"
            f"Tape le numéro du service qui t'intéresse 👇"
        )

    def _service_response(self, service_key: str) -> str:
        service = self.knowledge["services"][service_key]
        emoji_map = {
            "logo": "🎨", "affiche": "🖼️", "retouche": "📸",
            "bots": "🤖", "branding": "✨", "video": "🎬"
        }
        emoji = emoji_map.get(service_key, "💼")

        response = f"{emoji} *{service['name']}*\n\n"
        response += f"{service['description']}\n\n"
        response += f"💰 Tarif: {service['price']}\n"
        response += f"⏱️ Délai: {service['delivery']}\n"

        if "revisions" in service:
            response += f"✅ {service['revisions']} révisions gratuites\n"

        if "express" in service:
            response += f"⚡ Express 24h: {service['express']}\n"

        response += f"\nTape *commander* pour lancer ta demande 👇"
        return response

    def _pricing_response(self) -> str:
        p = self.knowledge["pricing"]
        return (
            "💰 *Tarifs Komara Agency*\n\n"
            f"🎨 Logo pro: {p['logo']}\n"
            f"🖼️ Affiche/Flyer: {p['affiche']}\n"
            f"📸 Retouche photo: {p['retouche']}\n"
            f"🤖 Bots: {p['bots']}\n"
            f"✨ Branding: {p['branding']}\n"
            f"🎬 Montage vidéo: {p['video']}\n\n"
            f"✅ {p['free_revisions']} révisions gratuites\n"
            f"💰 Révision sup: {p['extra_revision_cost']}\n"
            f"⚡ Express 24h: {p['express_surcharge']}\n"
            f"💳 Paiement: {', '.join(self.knowledge['payment'])}"
        )

    def _order_response(self, message: str) -> str:
        return (
            "Super ! 🚀 Pour lancer ta commande, j'ai besoin de:\n\n"
            "1. Le type de projet (logo, affiche, retouche, etc.)\n"
            "2. Une description de ce que tu veux\n"
            "3. Ton délai souhaité (normal ou express 24h)\n\n"
            "Écris-moi les détails ici 👇"
        )

    def _payment_response(self) -> str:
        methods = "\n".join(f"{i+1}. {m}" for i, m in enumerate(self.knowledge["payment"]))
        return (
            "💳 *Modes de paiement*\n\n"
            f"{methods}\n\n"
            "Le paiement se fait après validation du devis.\n"
            "Tape *commander* pour commencer 👇"
        )

    def _delivery_response(self) -> str:
        return (
            "⏱️ *Délais de livraison*\n\n"
            "Normal: 24h-72h selon le projet\n"
            "Express 24h: +30% sur le tarif\n\n"
            "Le délai commence après validation du devis et paiement."
        )

    def _revision_response(self) -> str:
        return (
            "✏️ *Révisions*\n\n"
            "2 révisions gratuites incluses.\n"
            "Révision supplémentaire: 50k GNF\n\n"
            "Dis-moi ce que tu veux modifier 👇"
        )

    def _contact_response(self) -> str:
        a = self.knowledge["agency"]
        return (
            "📞 *Contact Komara Agency*\n\n"
            f"WhatsApp: {a['whatsapp']}\n"
            f"Email: {a['email']}\n"
            f"Portfolio: {a['portfolio']}\n\n"
            f"Disponible {a['hours']}"
        )

    def _portfolio_response(self) -> str:
        return (
            f"🎨 *Portfolio Komara Agency*\n\n"
            f"Découvre mes travaux ici:\n"
            f"{self.knowledge['agency']['portfolio']}\n\n"
            f"Tu peux aussi me suivre sur Facebook: N-dine K fans"
        )

    def _default_response(self) -> str:
        return (
            "Je n'ai pas bien compris 🤔\n\n"
            "Tape un mot-clé:\n"
            "1. Logo\n"
            "2. Affiche\n"
            "3. Retouche photo\n"
            "4. Bots\n"
            "5. Branding\n"
            "6. Montage vidéo\n\n"
            "Ou tape *prix*, *commander*, *contact* 👇"
        )

    # ==================== CONSEIL CRÉATIF ====================

    def creative_advice(self, project_type: str, context: str = "") -> str:
        """Génère un conseil créatif personnalisé"""
        advice_base = {
            "logo": (
                "Pour un logo qui marque les esprits:\n\n"
                "1. Opte pour 1-2 couleurs max (mémorisation)\n"
                "2. Pense à la version noir & blanc (impression)\n"
                "3. Évite les détails trop fins (lisibilité petit format)\n"
                "4. Ta marque doit être reconnaissable même sans le nom\n\n"
                "Je peux te proposer 2 directions créatives, tu choisis ta préférée."
            ),
            "affiche": (
                "Pour une affiche qui attire l'attention:\n\n"
                "1. Un message principal lisible à 3m\n"
                "2. Une hiérarchie visuelle claire (titre > infos > contact)\n"
                "3. Des couleurs qui contrastent avec le support\n"
                "4. Un appel à l'action visible\n\n"
                "Quel est ton événement? Je t'oriente sur le meilleur design."
            ),
            "retouche": (
                "Pour une retouche photo naturelle:\n\n"
                "1. On garde ta peau naturelle (pas de plastique)\n"
                "2. On ajuste la lumière pour un rendu pro\n"
                "3. Le fond peut être changé selon ton besoin\n"
                "4. Format 9:16 pour les réseaux sociaux\n\n"
                "Envoie-moi ta photo, je te dis ce qui est possible."
            ),
            "branding": (
                "Pour une identité visuelle cohérente:\n\n"
                "1. Définis 2-3 couleurs qui représentent ton activité\n"
                "2. Choisis 1-2 polices max\n"
                "3. Crée un logo déclinable (horizontal, vertical, icône)\n"
                "4. Établis des règles d'usage (marges, taille mini)\n\n"
                "Parle-moi de ton activité, je te construis une charte."
            ),
        }

        return advice_base.get(project_type, "Décris-moi ton projet, je te conseille sur la meilleure approche créative.")

    # ==================== ANALYSE DE SENTIMENT ====================

    def analyze_sentiment(self, message: str) -> str:
        """Analyse simple du sentiment du message"""
        positive = ["content", "super", "génial", "parfait", "merci", "top", "excellent", "cool", "j'aime"]
        negative = ["déçu", "problème", "cher", "trop", "non", "pas bon", "nul", "bug"]
        neutral = ["ok", "d'accord", "compris", "oui", "d'accord"]

        msg = message.lower()
        if any(w in msg for w in positive):
            return "positif"
        elif any(w in msg for w in negative):
            return "négatif"
        else:
            return "neutre"

    # ==================== SUGGESTION PROACTIVE ====================

    def suggest_next_step(self, last_intent: str) -> str:
        """Suggère la prochaine étape selon le contexte"""
        suggestions = {
            "greeting": "Tu veux voir nos tarifs? Tape *prix*",
            "logo_info": "Tu veux commander un logo? Tape *commander*",
            "affiche_info": "Tu veux commander une affiche? Tape *commander*",
            "pricing": "Tu veux passer commande? Tape *commander*",
            "order": "N'oublie pas: le paiement se fait après validation du devis",
            "contact": "Tu peux m'écrire directement sur WhatsApp",
            "unknown": "Tape *prix* pour voir nos tarifs, ou *commander* pour passer commande",
        }
        return suggestions.get(last_intent, "Tape *commander* pour passer commande 👇")

    # ==================== HISTORIQUE & CONTEXT ====================

    def get_history(self) -> List[Dict]:
        """Retourne l'historique de conversation"""
        return self.conversation_history

    def clear_history(self):
        """Efface l'historique de conversation"""
        self.conversation_history = []
        self.user_context = {}

    def get_stats(self) -> Dict:
        """Retourne les statistiques de conversation"""
        intents = {}
        for msg in self.conversation_history:
            if msg["role"] == "user":
                intent = msg.get("intent", "unknown")
                intents[intent] = intents.get(intent, 0) + 1

        return {
            "total_messages": len(self.conversation_history),
            "user_messages": sum(1 for m in self.conversation_history if m["role"] == "user"),
            "agent_messages": sum(1 for m in self.conversation_history if m["role"] == "agent"),
            "intents_detected": intents,
        }

    # ==================== MODE API EXTERNE (optionnel) ====================

    def chat_with_api(self, message: str, system_prompt: str = None) -> str:
        """
        Utilise une API externe (OpenAI/Gemini) pour des réponses plus intelligentes.
        Nécessite une clé API configurée.
        """
        if not self.api_key:
            return self.generate_response(message)

        try:
            # Tentative avec OpenAI
            import urllib.request

            default_prompt = (
                f"Tu es {self.knowledge['agency']['name']}, une agence créative "
                f"basée en Guinée. Tu parles français, sois chaleureux et professionnel. "
                f"Services: logo, affiche, retouche photo, bots, branding, montage vidéo. "
                f"Tarifs logo: 300k-500k GNF, affiche: 300k GNF. "
                f"Contact: +212 701-986219. "
                f"Réponds de façon concise et naturelle."
            )

            prompt = system_prompt or default_prompt

            data = json.dumps({
                "model": "gpt-4o-mini",
                "messages": [
                    {"role": "system", "content": prompt},
                    {"role": "user", "content": message}
                ],
                "max_tokens": 300,
                "temperature": 0.7,
            }).encode()

            req = urllib.request.Request(
                "https://api.openai.com/v1/chat/completions",
                data=data,
                headers={
                    "Authorization": f"Bearer {self.api_key}",
                    "Content-Type": "application/json",
                }
            )

            with urllib.request.urlopen(req) as response:
                result = json.loads(response.read())
                return result["choices"][0]["message"]["content"]

        except Exception as e:
            print(f"[Komara AI] API error, falling back to local: {e}")
            return self.generate_response(message)


# ==================== EXEMPLE D'UTILISATION ====================

if __name__ == "__main__":
    agent = KomaraAgent()

    print("=" * 60)
    print(f"🤖 {agent.name} v{agent.version}")
    print(f"   {agent.knowledge['agency']['name']} — {agent.knowledge['agency']['slogan']}")
    print("=" * 60)
    print()

    # Simulation de conversation
    test_conversation = [
        "Salam",
        "Je veux un logo pour mon restaurant",
        "C'est combien?",
        "Quels sont vos délais?",
        "Je veux commander",
        "Merci beaucoup!",
    ]

    for msg in test_conversation:
        print(f"👤 Client: {msg}")
        response = agent.generate_response(msg)
        print(f"🤖 Agent: {response}")
        print(f"💡 Suggestion: {agent.suggest_next_step(agent.detect_intent(msg)[0])}")
        print("-" * 60)

    # Stats finales
    print("\n📊 Statistiques de conversation:")
    stats = agent.get_stats()
    print(json.dumps(stats, indent=2, ensure_ascii=False))

    # Conseil créatif
    print("\n🎨 Conseil créatif pour un logo:")
    print(agent.creative_advice("logo"))

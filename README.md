# 🤖 Komara AI Agent

Agent IA autonome pour **Komara Agency** 🇬🇳 — Gestion client, conseil créatif et automatisation.

## ✨ Fonctionnalités

- *Détection d'intention* — Comprend ce que le client demande
- *Réponses automatiques* — Tarifs, services, délais, paiement
- *Conseil créatif* — Recommandations personnalisées par projet
- *Analyse de sentiment* — Détecte l'humeur du client
- *Suggestions proactives* — Guide le client vers la prochaine étape
- *Historique de conversation* — Garde le contexte
- *API externe* — Compatible OpenAI / Gemini (optionnel)
- *Multilingue* — Français, Soussou, Malinké

## 🚀 Installation

```bash
git clone https://github.com/ndinekomara2442-cmd/komara-ai-agent.git
cd komara-ai-agent
pip install -r requirements.txt
```

## 💬 Utilisation

### Mode local (sans API)

```python
from komara_agent import KomaraAgent

agent = KomaraAgent()
response = agent.generate_response("Salam")
print(response)
```

### Mode API (OpenAI)

```python
from komara_agent import KomaraAgent

agent = KomaraAgent(api_key="sk-votre-cle")
response = agent.chat_with_api("Je veux un logo pour mon restaurant")
print(response)
```

### Test rapide

```bash
python komara_agent.py
```

## 🎯 Services gérés

1. 🎨 Logo Pro (300k-500k GNF)
2. 🖼️ Affiche & Flyer (300k GNF)
3. 📸 Retouche Photo
4. 🤖 Bots WhatsApp/Telegram
5. ✨ Branding Complet
6. 🎬 Montage Vidéo/Reels

## 📁 Structure

```
komara-ai-agent/
├── komara_agent.py     # Agent principal
├── knowledge.json      # Base de connaissances
├── requirements.txt    # Dépendances
└── README.md           # Documentation
```

## 🔧 Configuration

Modifie `knowledge.json` pour:
- Changer les tarifs
- Ajouter des services
- Mettre à jour les coordonnées

## 🌐 Intégration

Cet agent peut être intégré dans:
- WhatsApp Business (via Twilio)
- Telegram Bot
- Site web (Flask/FastAPI)
- Application desktop

## 📞 Contact

- WhatsApp: +212 701-986219
- Email: ndinekomara2442@gmail.com
- Portfolio: https://ndinekomara2442-cmd.github.io/komara-agency-portfolio/

---

**Komara Agency** 🇬🇳 — *Vision. Impact. Excellence.*

Made with ❤️ by Ndine Komara

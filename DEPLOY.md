# Déploiement Komara AI Agent

3 options gratuites pour héberger ton agent:

## Option 1: Railway.app (Recommandé)
1. Va sur https://railway.app
2. Connecte ton GitHub
3. Sélectionne le repo komara-ai-agent
4. Railway détecte le Dockerfile automatiquement
5. Ajoute les variables d'environnement:
   - TELEGRAM_BOT_TOKEN_2
   - GEMINI_API_KEY (PRIORITÉ — get it: https://aistudio.google.com/apikey)
   - GROQ_API_KEY (OPTIONNEL — get it: https://console.groq.com/keys)
   - SERVER_URL=https://komara-ai-agent.up.railway.app
6. Deploy — ton agent est en ligne!

## Option 2: Render.com
1. Va sur https://render.com
2. New > Web Service > Connect GitHub
3. Sélectionne komara-ai-agent
4. Build: pip install -r requirements.txt
5. Start: python server.py
6. Ajoute les variables d'environnement
7. Deploy

## Option 3: VPS (Hetzner/OVH ~3€/mois)
```bash
git clone https://github.com/ndinekomara2442-cmd/komara-ai-agent.git
cd komara-ai-agent
cp .env.example .env
nano .env
docker-compose up -d
```

## Vérification
Une fois déployé, teste:
- Health: https://ton-url/health
- Telegram: envoie /start au bot
- Le webhook se configure automatiquement au démarrage

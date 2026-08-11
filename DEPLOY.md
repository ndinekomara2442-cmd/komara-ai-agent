# Déploiement Komara AI Agent - 100% Autonome

3 options gratuites pour héberger ton agent sans Base44:

## Option 1: Railway.app (Recommandé - Gratuit)
1. Va sur https://railway.app
2. Connecte ton GitHub
3. Sélectionne le repo komara-ai-agent
4. Railway détecte le Dockerfile automatiquement
5. Ajoute les variables d'environnement:
   - TELEGRAM_BOT_TOKEN_2
   - TWILIO_ACCOUNT_SID
   - TWILIO_AUTH_TOKEN
   - SERVER_URL=https://komara-ai-agent.up.railway.app
6. Deploy - ton agent est en ligne!

## Option 2: Render.com (Gratuit)
1. Va sur https://render.com
2. New > Web Service > Connect GitHub
3. Sélectionne komara-ai-agent
4. Build Command: pip install -r requirements.txt
5. Start Command: python server.py
6. Ajoute les variables d'environnement
7. Deploy

## Option 3: VPS (Hetzner/OVH - ~3€/mois)
```bash
# Sur le serveur
git clone https://github.com/ndinekomara2442-cmd/komara-ai-agent.git
cd komara-ai-agent
cp .env.example .env
# Édite .env avec tes clés
nano .env
docker-compose up -d
```

## Option 4: Fly.io (Gratuit)
```bash
flyctl launch
flyctl secrets set TELEGRAM_BOT_TOKEN_2=xxx
flyctl deploy
```

## Vérification
Une fois déployé, teste:
- Health: https://ton-url/health
- Telegram: envoie /start au bot
- Le webhook se configure automatiquement au démarrage

## Avantages vs Base44
- 100% contrôle du code
- Pas de limite de crédits
- Tu peux ajouter n'importe quelle librairie
- Base de données custom possible
- Coût: gratuit ou ~3€/mois

# ReelTok — Dashboard

Dashboard web pour créer et publier des carrousels TikTok.

## Prérequis

- Node.js 18+
- Python 3.12+
- Variables d'environnement configurées (voir `.env.example`)

## Lancer en local

### 1. Backend (FastAPI)

```bash
# À la racine du projet
pip install -r requirements.txt
playwright install chromium

# Variables dans .env : GEMINI_API_KEY, UPLOAD_POST_USER, UPLOAD_POST_API_KEY, etc.

.venv/bin/uvicorn backend.main:app --reload --port 8000
```

### 2. Frontend (Next.js)

```bash
cd dashboard
cp .env.example .env.local
# Éditer .env.local : NEXT_PUBLIC_API_URL=http://localhost:8000

npm run dev
```

Ouvre http://localhost:3000

## Déploiement

Voir le guide complet : [DEPLOY.md](../DEPLOY.md)

- **Vercel** : root directory `dashboard/`, variable `NEXT_PUBLIC_API_URL`
- **Railway** : Dockerfile à la racine, volume sur `/app/data`, 2 Go+ RAM

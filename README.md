# ReelTok

Générateur de carrousels TikTok avec dashboard web : contenu Gemini, images IA, overlay, publication via upload-post.com, et automatisation depuis Google Sheets.

## Structure

```
reeltok/
├── backend/          # API FastAPI
├── dashboard/        # Frontend Next.js
├── assets/           # Images preset (fille1–9, leafee)
├── data/             # Queue automation, historique (local, gitignored)
├── docker-compose.yml
└── requirements.txt
```

## Démarrage local

### Backend

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
playwright install chromium
cp .env.example .env   # puis remplir les clés API

.venv/bin/uvicorn backend.main:app --reload --port 8000
```

### Frontend

```bash
cd dashboard
cp .env.example .env.local
npm install
npm run dev
```

Ouvre http://localhost:3000

## Pages

- `/editor` — création manuelle de carrousels
- `/automation` — import Google Sheets + publication planifiée
- `/config` — configuration des prompts

## Déploiement

Déploiement via **Coolify** (Docker Compose) : voir [DEPLOY.md](DEPLOY.md)

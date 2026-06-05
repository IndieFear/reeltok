# ReelTok Dashboard

Frontend Next.js du projet ReelTok.

## Développement local

```bash
cp .env.example .env.local
# NEXT_PUBLIC_API_URL=http://localhost:8000

npm install
npm run dev
```

Backend requis sur le port 8000 (voir README à la racine).

## Déploiement

Déployé via Coolify en tant que service `dashboard` dans le `docker-compose.yml` à la racine.
Voir [DEPLOY.md](../DEPLOY.md).

# Déploiement ReelTok — Railway + Vercel

## Architecture

| Service | Plateforme | Dossier | URL type |
|---------|-----------|---------|----------|
| Backend FastAPI + Playwright | [Railway](https://railway.app) | racine du repo | `https://reeltok-api.up.railway.app` |
| Dashboard Next.js | [Vercel](https://vercel.com) | `dashboard/` | `https://reeltok.vercel.app` |

---

## 1. Backend sur Railway

### Créer le projet

1. [railway.app](https://railway.app) → **New Project** → **Deploy from GitHub repo**
2. Sélectionner `IndieFear/reeltok`
3. Railway détecte le `Dockerfile` via `railway.toml`

### Variables d'environnement

Dans **Variables** du service :

| Variable | Obligatoire | Description |
|----------|-------------|-------------|
| `GEMINI_API_KEY` | oui | Génération de texte |
| `RUNWARE_API_KEY` | oui* | Images Flux (modèle par défaut) |
| `REPLICATE_API_TOKEN` | oui* | Images GPT/Grok via Replicate |
| `UPLOAD_POST_API_KEY` | oui | Publication TikTok |
| `UPLOAD_POST_USER` | oui | Compte upload-post |
| `FONT_SCALE` | non | Taille du texte overlay (défaut `1.0`) |

\* Au moins une clé image (Runware ou Replicate) selon les modèles utilisés.

### Volume persistant (recommandé)

L'automatisation et l'historique sont stockés dans `data/`.

1. Service Railway → **Volumes** → **Add Volume**
2. Monter sur `/app/data`
3. Taille : 1–5 Go selon usage

Sans volume, les données sont perdues à chaque redéploiement.

### Ressources

- **RAM** : minimum **2 Go** (Playwright + génération d'images)
- Healthcheck : `GET /health`

### Domaine public

Settings → **Networking** → **Generate Domain**

Copier l'URL (ex. `https://reeltok-production.up.railway.app`) pour Vercel.

---

## 2. Frontend sur Vercel

### Créer le projet

1. [vercel.com](https://vercel.com) → **Add New Project**
2. Importer `IndieFear/reeltok`
3. **Root Directory** : `dashboard` (important)
4. Framework : Next.js (auto-détecté)

### Variable d'environnement

| Variable | Valeur |
|----------|--------|
| `NEXT_PUBLIC_API_URL` | URL Railway du backend (sans slash final) |

Exemple : `https://reeltok-production.up.railway.app`

Redéployer après modification de cette variable.

---

## 3. Vérification

```bash
# Backend
curl https://TON-URL-RAILWAY/health
# → {"status":"ok"}

# Frontend
# Ouvrir https://ton-projet.vercel.app/editor
# Vérifier que les appels API ne sont pas bloqués (CORS déjà configuré pour *.vercel.app)
```

---

## 4. Déploiement via CLI (optionnel)

### Railway

```bash
brew install railway
cd /chemin/vers/reeltok
railway login
railway init
railway up
railway domain
```

### Vercel

```bash
npm i -g vercel
cd dashboard
vercel login
vercel --prod
# Puis configurer NEXT_PUBLIC_API_URL dans le dashboard Vercel
```

---

## Dépannage

| Problème | Cause probable | Solution |
|----------|----------------|----------|
| Build Docker timeout | Playwright + Chromium lourd | Patience (~5–10 min premier build) |
| 502 / crash au rendu | RAM insuffisante | Passer à 2 Go+ sur Railway |
| CORS error frontend | Mauvaise URL API | Vérifier `NEXT_PUBLIC_API_URL` |
| Queue automation vide après redeploy | Pas de volume | Ajouter volume `/app/data` |
| Images sans police TikTok | Chemin font | `FONT_SCALE` ou fonts dans `assets/fonts/` (inclus dans l'image Docker) |

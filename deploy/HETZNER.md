# ReelTok sur Hetzner VPS

Guide pour héberger backend + dashboard sur **un seul serveur** (plus simple que Railway + Vercel).

## Prérequis

| Ressource | Minimum recommandé |
|-----------|-------------------|
| Serveur Hetzner | **CPX11** ou **CX22** (2 vCPU, 2–4 Go RAM) |
| OS | Ubuntu 24.04 |
| Domaine | Optionnel mais recommandé (HTTPS auto via Caddy) |
| Ports ouverts | 22, 80, 443 |

---

## 1. Créer le serveur

1. [console.hetzner.cloud](https://console.hetzner.cloud) → **Add Server**
2. Ubuntu 24.04, région proche de toi
3. Type : **CPX11** (2 Go RAM) minimum — Playwright a besoin de RAM
4. SSH key : ajoute ta clé publique
5. Créer

Note l'IP du serveur.

---

## 2. DNS (si tu as un domaine)

Chez ton registrar, ajoute un enregistrement **A** :

```
reeltok.tondomaine.com  →  IP_DU_VPS
```

---

## 3. Installer Docker sur le VPS

```bash
ssh root@IP_DU_VPS

apt update && apt upgrade -y
apt install -y git ca-certificates curl

# Docker officiel
curl -fsSL https://get.docker.com | sh
```

---

## 4. Cloner et configurer

```bash
git clone https://github.com/IndieFear/reeltok.git
cd reeltok

cp .env.vps.example .env
nano .env
```

Remplis au minimum :

```env
PUBLIC_URL=https://reeltok.tondomaine.com
DOMAIN=reeltok.tondomaine.com
GEMINI_API_KEY=...
RUNWARE_API_KEY=...
REPLICATE_API_TOKEN=...
UPLOAD_POST_API_KEY=...
UPLOAD_POST_USER=...
```

> Si tu n'as pas encore de domaine, mets temporairement `PUBLIC_URL=http://IP_DU_VPS` et `DOMAIN=:80` pour tester en HTTP.

---

## 5. Lancer

```bash
docker compose up -d --build
```

Premier build : **5–15 min** (Playwright + Chromium).

Vérifie :

```bash
docker compose ps
curl http://localhost/health          # via Caddy
curl http://localhost/api/content-types
```

Ouvre `https://reeltok.tondomaine.com` dans le navigateur.

---

## 6. Autodeploy à chaque commit

Sur le VPS :

```bash
chmod +x deploy/vps-deploy.sh
```

Après chaque `git push` sur `main` :

```bash
./deploy/vps-deploy.sh
```

Ou automatise avec un **cron** ou un **webhook GitHub** (optionnel).

---

## Architecture

```
Internet
   │
   ▼
Caddy (:80 / :443, HTTPS auto)
   ├── /api/*  → backend:8000  (FastAPI + Playwright + scheduler)
   ├── /health → backend:8000
   └── /*      → dashboard:3000 (Next.js)
   
./data/  → volume persistant (queue automation, historique, carousels)
```

---

## Commandes utiles

```bash
docker compose logs -f backend      # logs API
docker compose logs -f dashboard    # logs frontend
docker compose restart backend      # redémarrer l'API
docker compose down                 # tout arrêter
```

---

## Dépannage

| Problème | Solution |
|----------|----------|
| Build lent / OOM | Passe à CPX21 (4 Go RAM) |
| HTTPS ne marche pas | Vérifie le DNS (A record → IP VPS) |
| Carousel bloque | `CAROUSEL_RENDER_CONCURRENCY=1` dans `.env` |
| Données perdues | Vérifie que `./data` est bien monté (`docker compose exec backend ls /app/data`) |

---

## Migrer depuis Railway/Vercel

1. Copie tes variables d'env Railway → `.env` sur le VPS
2. Si tu as des données sur Railway, télécharge le volume et copie dans `./data/`
3. Mets à jour le DNS vers le VPS
4. Tu peux supprimer Railway/Vercel une fois validé

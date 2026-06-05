# Déploiement ReelTok — Coolify

Déploiement via [Coolify](https://coolify.io) (Docker Compose). Coolify gère HTTPS, autodeploy GitHub et le reverse proxy.

## 1. Créer la ressource

1. Coolify → **+ New Resource** → **Public/Private Repository**
2. Repo : `IndieFear/reeltok`, branche `main`
3. **Build Pack** : `Docker Compose`
4. **Docker Compose location** : `docker-compose.yml`
5. **Base Directory** : `/` (racine)

## 2. Variables d'environnement

Dans l'onglet **Environment Variables** (voir `.env.example`) :

| Variable | Exemple | Rôle |
|----------|---------|------|
| `DASHBOARD_URL` | `https://reeltok.tondomaine.com` | CORS backend |
| `API_URL` | `https://api.reeltok.tondomaine.com` | Build frontend (`NEXT_PUBLIC_API_URL`) |
| `GEMINI_API_KEY` | `...` | Génération texte |
| `RUNWARE_API_KEY` | `...` | Images |
| `REPLICATE_API_TOKEN` | `...` | Images (optionnel) |
| `UPLOAD_POST_API_KEY` | `...` | Publication TikTok |
| `UPLOAD_POST_USER` | `...` | Compte upload-post |
| `FONT_SCALE` | `1.0` | Taille texte overlay |
| `CAROUSEL_RENDER_CONCURRENCY` | `1` | Rendu Playwright (1 slide à la fois) |
| `APP_PASSWORD` | mot de passe fort | Protection login dashboard + API |
| `AUTH_SECRET` | chaîne aléatoire 32+ car. | Signature des sessions (`openssl rand -hex 32`) |
| `AUTH_REQUIRED` | `true` | Active la page login (buildtime pour dashboard) |
| `COOKIE_DOMAIN` | `.tondomaine.com` | Optionnel — auto-détecté depuis `DASHBOARD_URL` |

> `APP_PASSWORD`, `AUTH_SECRET` et `AUTH_REQUIRED` doivent être définies. Sans `APP_PASSWORD` sur le **backend**, l'API reste ouverte.

> `API_URL` et `DASHBOARD_URL` doivent être les URLs **HTTPS finales** configurées à l'étape 3.

## Sécurité

- Page `/login` avant d'accéder au dashboard
- Toutes les routes `/api/*` (sauf login/status) exigent une session valide
- Anti-bruteforce : 5 tentatives / 15 min → blocage 30 min par IP

## 3. Domaines (2 FQDN)

Assigne un domaine **par service** dans Coolify :

| Service | FQDN | Port interne |
|---------|------|--------------|
| `backend` | `https://api.reeltok.tondomaine.com` | `8000` |
| `dashboard` | `https://reeltok.tondomaine.com` | `3000` |

**DNS** :
```
reeltok.tondomaine.com      A  →  IP_SERVEUR
api.reeltok.tondomaine.com  A  →  IP_SERVEUR
```

## 4. Deploy

1. **Deploy** manuel la première fois (build long : Playwright ~10 min)
2. Active **Auto Deploy** sur `main` → chaque `git push` redéploie

## 5. Vérification

```bash
curl https://api.reeltok.tondomaine.com/health
# → {"status":"ok"}
```

Ouvre `https://reeltok.tondomaine.com/editor` — les appels API doivent aller vers `api.reeltok.tondomaine.com`.

## Données persistantes

Le volume `reeltok-data` est monté sur `/app/data` (queue automation, historique, carousels).

## Ressources recommandées

Serveur **4 Go RAM** minimum (Coolify + Playwright + Next.js).

## Dépannage

| Problème | Solution |
|----------|----------|
| Frontend appelle `localhost:8000` | `API_URL` incorrecte → redeploy **dashboard** |
| CORS error | `DASHBOARD_URL` doit matcher l'URL du dashboard |
| Carousel bloque | `CAROUSEL_RENDER_CONCURRENCY=1`, augmenter la RAM |
| Build échoue (exit 255) | Manque de RAM — serveur 4 Go+, redeploy 2×, ou augmente timeout Coolify |
| `localhost:8000` dans le navigateur | `API_URL` absente au build → coche **Buildtime** + rebuild dashboard |

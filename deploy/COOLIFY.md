# ReelTok sur Hetzner + Coolify

Coolify gère HTTPS, autodeploy GitHub et le reverse proxy — **pas besoin de Caddy**.

## Fichier à utiliser

| Fichier | Usage |
|---------|-------|
| `docker-compose.coolify.yml` | **Coolify** (sans Caddy) |
| `docker-compose.yml` | VPS manuel avec Caddy |

---

## 1. Créer la ressource

1. Coolify → **+ New Resource** → **Public/Private Repository**
2. Repo : `IndieFear/reeltok`, branche `main`
3. **Build Pack** : `Docker Compose`
4. **Docker Compose location** : `docker-compose.coolify.yml`
5. **Base Directory** : `/` (racine)

---

## 2. Variables d'environnement

Dans l'onglet **Environment Variables**, ajoute (voir `.env.coolify.example`) :

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

> **Important** : `API_URL` et `DASHBOARD_URL` doivent être les URLs **finales HTTPS** que tu configures à l'étape 3.

---

## 3. Domaines (2 FQDN)

Après le premier deploy, assigne un domaine **par service** :

| Service Coolify | FQDN | Port interne |
|-----------------|------|--------------|
| `backend` | `https://api.reeltok.tondomaine.com` | `8000` |
| `dashboard` | `https://reeltok.tondomaine.com` | `3000` |

Coolify/Traefik route automatiquement. Pas de `ports:` dans le compose.

**DNS** chez ton registrar :
```
reeltok.tondomaine.com      A  →  IP_HETZNER
api.reeltok.tondomaine.com  A  →  IP_HETZNER
```

---

## 4. Deploy & autodeploy

1. **Deploy** manuel la première fois (build long : Playwright ~10 min)
2. Active **Auto Deploy** sur la branche `main` → chaque `git push` redéploie

Script manuel si besoin :
```bash
git push origin main   # Coolify détecte et rebuild
```

---

## 5. Vérification

```bash
curl https://api.reeltok.tondomaine.com/health
# → {"status":"ok"}

# Ouvre https://reeltok.tondomaine.com/editor
# Les appels réseau doivent aller vers api.reeltok.tondomaine.com
```

---

## Données persistantes

Le volume Docker `reeltok-data` est monté sur `/app/data` (queue automation, historique, carousels). Il survit aux redeploys Coolify.

---

## Ressources serveur

| Composant | RAM |
|-----------|-----|
| Coolify | ~512 Mo–1 Go |
| Backend + Playwright | ~1–2 Go |
| Dashboard Next.js | ~256 Mo |
| **Total recommandé** | **CPX21 (4 Go)** |

---

## Dépannage

| Problème | Solution |
|----------|----------|
| Frontend appelle `localhost:8000` | `API_URL` mal configurée → redeploy **dashboard** (variable injectée au build) |
| CORS error | `DASHBOARD_URL` doit matcher l'URL du dashboard exactement |
| Carousel bloque | `CAROUSEL_RENDER_CONCURRENCY=1`, passe à 4 Go RAM |
| Conflit port 80/443 | N'utilise **pas** `docker-compose.yml` (Caddy) — utilise `docker-compose.coolify.yml` |
| Build timeout | Augmente le timeout build dans Coolify (Settings) |

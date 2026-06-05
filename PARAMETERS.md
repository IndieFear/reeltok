# Paramètres du projet

Tous les paramètres que tu peux utiliser via variables d'environnement (`.env` ou `.venv/.env`).

---

## Variables d'environnement

À mettre dans `.env` ou `.venv/.env` (avec `export` si tu les mets en dur dans le fichier, ou sans `export` si tu utilises `python-dotenv`).

### API et services

| Variable | Utilisation | Description |
|----------|-------------|-------------|
| `GEMINI_API_KEY` | Génération des textes (Gemini) | Clé API Google Gemini. |
| `RUNWARE_API_KEY` | Génération d'images (Runware.ai) | Clé API Runware pour la génération d'images par IA. |
| `REPLICATE_API_TOKEN` | Génération d'images (Replicate) | Token Replicate pour utiliser `openai/gpt-image-2`. |
| `OPENAI_API_KEY` | Génération d'images (optionnel) | Clé OpenAI transmise à `gpt-image-2` via Replicate si tu veux payer OpenAI directement. |
| `UPLOAD_POST_API_KEY` | Publication TikTok | Clé API upload-post.com. |
| `UPLOAD_POST_USER` | Publication TikTok | Identifiant du compte configuré sur upload-post.com. |

### Overlay / rendu (polices, templates)

| Variable | Utilisation | Description |
|----------|-------------|-------------|
| `FONT_SCALE` | Taille du texte (PIL) | Facteur de taille des polices (ex. `1.2` = +20 %). Défaut : `1.0`. |
| `TIKTOK_FONT_PATH` | Police du texte | Chemin vers le fichier `.ttf` (ex. TikTok Sans). Sinon : `assets/fonts/TikTokSans-Regular.ttf`. |

---

## Lancement

Le projet fonctionne via le dashboard Next.js :

```bash
# Lancer le backend
cd backend && uvicorn main:app --reload

# Lancer le frontend
cd dashboard && npm run dev
```

Accède à http://localhost:3000 pour utiliser l'interface.

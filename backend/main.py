"""
Backend FastAPI pour ReelTok.
Expose les endpoints pour génération de contenu, rendu des slides et publication.
"""

import logging
import os
import sys
from contextlib import asynccontextmanager
from pathlib import Path

# Logging (simple, lisible en console uvicorn)
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(name)s | %(message)s",
)

# Charger les variables d'environnement
ROOT = Path(__file__).resolve().parent.parent
try:
    from dotenv import load_dotenv
    load_dotenv(ROOT / ".env")
    load_dotenv(ROOT / ".venv" / ".env")
except ImportError:
    pass

# Ajouter la racine du projet au path pour importer les modules existants
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from backend.middleware.auth import AuthMiddleware
from backend.routers import auth, content, carousel, publish, templates, images, user_images, config, automation
from backend.services.automation_scheduler import start_scheduler, stop_scheduler


@asynccontextmanager
async def lifespan(app: FastAPI):
    start_scheduler()
    yield
    await stop_scheduler()


app = FastAPI(
    title="ReelTok API",
    description="API ReelTok — génération et publication de carrousels TikTok",
    version="1.0.1",
    lifespan=lifespan,
)

_cors_origins = ["http://localhost:3000", "http://localhost:3001"]
_public_url = os.getenv("PUBLIC_URL", "").rstrip("/")
if _public_url:
    _cors_origins.append(_public_url)

app.add_middleware(AuthMiddleware)
app.add_middleware(
    CORSMiddleware,
    allow_origins=_cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth.router, prefix="/api", tags=["auth"])
app.include_router(content.router, prefix="/api", tags=["content"])
app.include_router(carousel.router, prefix="/api", tags=["carousel"])
app.include_router(publish.router, prefix="/api", tags=["publish"])
app.include_router(templates.router, prefix="/api", tags=["templates"])
app.include_router(images.router, prefix="/api", tags=["images"])
app.include_router(user_images.router, prefix="/api", tags=["user-images"])
app.include_router(config.router, prefix="/api", tags=["config"])
app.include_router(automation.router, prefix="/api", tags=["automation"])


@app.get("/health")
def health():
    return {"status": "ok"}

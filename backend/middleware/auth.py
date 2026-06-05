"""Middleware HTTP : bloque l'API si non authentifié."""

from __future__ import annotations

from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import JSONResponse

from backend.routers.auth import _is_authenticated
from backend.services.auth import auth_enabled

class AuthMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        if not auth_enabled():
            return await call_next(request)

        path = request.url.path
        if path == "/health" or path.startswith("/api/auth/"):
            return await call_next(request)

        if request.method == "OPTIONS":
            return await call_next(request)

        if _is_authenticated(request):
            return await call_next(request)

        return JSONResponse({"detail": "Non authentifié"}, status_code=401)

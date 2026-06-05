"""Connexion / déconnexion et statut d'authentification."""

from __future__ import annotations

import asyncio

from fastapi import APIRouter, HTTPException, Request, Response
from pydantic import BaseModel, Field

from backend.services.auth import (
    SESSION_COOKIE,
    SESSION_MAX_AGE_SECONDS,
    auth_enabled,
    check_login_allowed,
    clear_login_attempts,
    cookie_domain,
    cookie_secure,
    create_session_token,
    login_failure_delay,
    record_login_failure,
    verify_password,
    verify_session_token,
)

router = APIRouter()


class LoginRequest(BaseModel):
    password: str = Field(min_length=1, max_length=256)


def _client_ip(request: Request) -> str:
    forwarded = request.headers.get("x-forwarded-for", "").split(",")[0].strip()
    if forwarded:
        return forwarded
    if request.client:
        return request.client.host
    return "unknown"


def _is_authenticated(request: Request) -> bool:
    if not auth_enabled():
        return True
    token = request.cookies.get(SESSION_COOKIE)
    if not token:
        auth_header = request.headers.get("authorization", "")
        if auth_header.lower().startswith("bearer "):
            token = auth_header[7:].strip()
    return verify_session_token(token)


def _set_session_cookie(response: Response, token: str) -> None:
    domain = cookie_domain()
    response.set_cookie(
        key=SESSION_COOKIE,
        value=token,
        max_age=SESSION_MAX_AGE_SECONDS,
        httponly=True,
        secure=cookie_secure(),
        samesite="lax",
        path="/",
        domain=domain,
    )


def _clear_session_cookie(response: Response) -> None:
    domain = cookie_domain()
    response.delete_cookie(key=SESSION_COOKIE, path="/", domain=domain)


@router.get("/auth/status")
def auth_status(request: Request):
    return {
        "enabled": auth_enabled(),
        "authenticated": _is_authenticated(request),
    }


@router.post("/auth/login")
async def login(body: LoginRequest, request: Request, response: Response):
    if not auth_enabled():
        return {"ok": True, "auth": "disabled"}

    client_ip = _client_ip(request)
    allowed, retry_after = check_login_allowed(client_ip)
    if not allowed:
        raise HTTPException(
            status_code=429,
            detail=f"Trop de tentatives. Réessaie dans {retry_after // 60 + 1} min.",
            headers={"Retry-After": str(retry_after)},
        )

    if not verify_password(body.password):
        record_login_failure(client_ip)
        await asyncio.sleep(login_failure_delay())
        raise HTTPException(status_code=401, detail="Mot de passe incorrect")

    clear_login_attempts(client_ip)
    token = create_session_token()
    _set_session_cookie(response, token)
    return {"ok": True}


@router.post("/auth/logout")
def logout(response: Response):
    _clear_session_cookie(response)
    return {"ok": True}

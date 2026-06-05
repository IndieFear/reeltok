"""Authentification par mot de passe, sessions signées et anti-bruteforce."""

from __future__ import annotations

import base64
import hashlib
import hmac
import json
import os
import secrets
import time
from collections import defaultdict
from threading import Lock
from urllib.parse import urlparse

SESSION_COOKIE = "reeltok_session"
SESSION_MAX_AGE_SECONDS = 7 * 24 * 3600

MAX_LOGIN_ATTEMPTS = 5
LOGIN_WINDOW_SECONDS = 15 * 60
LOGIN_LOCKOUT_SECONDS = 30 * 60
LOGIN_FAILURE_DELAY_SECONDS = 1.0

_lock = Lock()
_attempts: dict[str, list[float]] = defaultdict(list)
_lockouts: dict[str, float] = {}


def auth_enabled() -> bool:
    return bool(os.getenv("APP_PASSWORD", "").strip())


def get_auth_secret() -> str:
    secret = os.getenv("AUTH_SECRET", "").strip()
    if secret:
        return secret
    if auth_enabled():
        # Fallback déterministe si AUTH_SECRET absent (déconseillé en prod)
        return hashlib.sha256(os.getenv("APP_PASSWORD", "").encode()).hexdigest()
    return ""


def get_app_password() -> str:
    return os.getenv("APP_PASSWORD", "").strip()


def cookie_domain_from_origin(origin: str | None) -> str | None:
    """Déduit le domaine parent depuis l'en-tête Origin (ex. dashboard → cookie partagé)."""
    if not origin:
        return None
    host = urlparse(origin).hostname
    if host and host not in {"localhost", "127.0.0.1"} and "." in host:
        parts = host.split(".")
        if len(parts) >= 2:
            return f".{'.'.join(parts[-2:])}"
    return None


def cookie_domain() -> str | None:
    explicit = os.getenv("COOKIE_DOMAIN", "").strip()
    if explicit:
        return explicit if explicit.startswith(".") else f".{explicit}"
    for key in ("PUBLIC_URL", "DASHBOARD_URL"):
        url = os.getenv(key, "").strip()
        if not url:
            continue
        host = urlparse(url).hostname
        if host and host not in {"localhost", "127.0.0.1"} and "." in host:
            parts = host.split(".")
            if len(parts) >= 2:
                return f".{'.'.join(parts[-2:])}"
    return None


def cookie_secure() -> bool:
    for key in ("PUBLIC_URL", "DASHBOARD_URL", "API_URL"):
        if os.getenv(key, "").strip().lower().startswith("https://"):
            return True
    return False


def create_session_token() -> str:
    payload = {"exp": int(time.time()) + SESSION_MAX_AGE_SECONDS}
    payload_b64 = base64.urlsafe_b64encode(json.dumps(payload, separators=(",", ":")).encode()).decode().rstrip("=")
    sig = hmac.new(get_auth_secret().encode(), payload_b64.encode(), hashlib.sha256).hexdigest()
    return f"{payload_b64}.{sig}"


def verify_session_token(token: str | None) -> bool:
    if not token or not auth_enabled():
        return not auth_enabled()
    try:
        payload_b64, sig = token.rsplit(".", 1)
        expected = hmac.new(get_auth_secret().encode(), payload_b64.encode(), hashlib.sha256).hexdigest()
        if not secrets.compare_digest(expected, sig):
            return False
        padding = "=" * (-len(payload_b64) % 4)
        payload = json.loads(base64.urlsafe_b64decode(payload_b64 + padding))
        return int(payload.get("exp", 0)) >= int(time.time())
    except (ValueError, json.JSONDecodeError, TypeError):
        return False


def check_login_allowed(client_ip: str) -> tuple[bool, int]:
    """Retourne (autorisé, secondes avant retry)."""
    now = time.time()
    with _lock:
        locked_until = _lockouts.get(client_ip)
        if locked_until and now < locked_until:
            return False, int(locked_until - now)
        if locked_until and now >= locked_until:
            _lockouts.pop(client_ip, None)
            _attempts.pop(client_ip, None)

        window_start = now - LOGIN_WINDOW_SECONDS
        recent = [t for t in _attempts.get(client_ip, []) if t >= window_start]
        _attempts[client_ip] = recent
        if len(recent) >= MAX_LOGIN_ATTEMPTS:
            _lockouts[client_ip] = now + LOGIN_LOCKOUT_SECONDS
            return False, LOGIN_LOCKOUT_SECONDS
    return True, 0


def record_login_failure(client_ip: str) -> None:
    with _lock:
        _attempts[client_ip].append(time.time())


def clear_login_attempts(client_ip: str) -> None:
    with _lock:
        _attempts.pop(client_ip, None)
        _lockouts.pop(client_ip, None)


def verify_password(password: str) -> bool:
    expected = get_app_password()
    if not expected:
        return True
    return secrets.compare_digest(password.encode(), expected.encode())


def login_failure_delay() -> float:
    return LOGIN_FAILURE_DELAY_SECONDS

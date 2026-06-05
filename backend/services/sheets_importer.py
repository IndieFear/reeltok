"""Import de sujets depuis un Google Sheet publié en CSV."""

from __future__ import annotations

import csv
import io
import re
from typing import Any
from urllib.parse import urlparse

import requests

SKIP_STATUSES = {"done", "skip", "skipped", "published", "ignore", "ignorer"}


def _normalize_header(value: str) -> str:
    return re.sub(r"\s+", "_", value.strip().lower())


def _to_public_csv_url(url: str) -> str:
    """Convertit une URL Google Sheets en export CSV si nécessaire."""
    url = url.strip()
    if not url:
        raise ValueError("URL du Google Sheet requise")

    if "output=csv" in url or "format=csv" in url:
        return url

    # Format: https://docs.google.com/spreadsheets/d/{ID}/edit...
    match = re.search(r"/spreadsheets/d/([a-zA-Z0-9-_]+)", url)
    if match:
        sheet_id = match.group(1)
        gid_match = re.search(r"[?&#]gid=(\d+)", url)
        gid = gid_match.group(1) if gid_match else "0"
        return f"https://docs.google.com/spreadsheets/d/{sheet_id}/export?format=csv&gid={gid}"

    parsed = urlparse(url)
    if parsed.scheme in {"http", "https"} and url.lower().endswith(".csv"):
        return url

    return url


def fetch_sheet_rows(csv_url: str, timeout: int = 30) -> list[dict[str, Any]]:
    """Télécharge et parse le CSV. Retourne une liste de lignes normalisées."""
    export_url = _to_public_csv_url(csv_url)
    resp = requests.get(export_url, timeout=timeout)
    resp.raise_for_status()
    text = resp.content.decode("utf-8-sig")
    reader = csv.DictReader(io.StringIO(text))
    if not reader.fieldnames:
        raise ValueError("Le CSV est vide ou sans en-têtes")

    header_map = {_normalize_header(h): h for h in reader.fieldnames if h}

    def col(*names: str) -> str | None:
        for name in names:
            key = _normalize_header(name)
            if key in header_map:
                return header_map[key]
        return None

    topic_col = col("topic", "sujet", "keyword", "mot_cle", "mot-clé", "subject")
    if not topic_col:
        raise ValueError("Colonne 'topic' ou 'sujet' introuvable dans le Sheet")

    content_type_col = col("content_type", "type", "format")
    account_col = col("account", "compte", "upload_post_user")
    status_col = col("status", "statut", "etat", "état")

    rows: list[dict[str, Any]] = []
    for row_num, raw in enumerate(reader, start=2):
        topic = (raw.get(topic_col) or "").strip()
        if not topic:
            continue

        status_val = (raw.get(status_col) or "").strip().lower() if status_col else ""
        if status_val in SKIP_STATUSES:
            continue

        rows.append(
            {
                "topic": topic,
                "content_type": (raw.get(content_type_col) or "").strip() if content_type_col else None,
                "account": (raw.get(account_col) or "").strip() if account_col else None,
                "status": status_val or None,
                "sheet_row": row_num,
            }
        )
    return rows

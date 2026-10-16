"""Search agent: tìm thông tin chính hãng qua SearXNG."""
from __future__ import annotations

import re
from typing import Any
from urllib.parse import urlparse

import requests

from backend.config import get_settings
from backend.errors import ServiceError
from backend.models import ProductData

_ABV = re.compile(r"(\d{1,2}(?:[.,]\d+)?)\s*%")
_VOL = re.compile(r"(\d+(?:[.,]\d+)?)\s*(ml|cl|l)\b", re.IGNORECASE)


def extract_abv(text: str) -> str | None:
    """Trích ABV đầu tiên hợp lý (0-100%)."""
    for m in _ABV.finditer(text):
        v = float(m.group(1).replace(",", "."))
        if 0 < v <= 100:
            return f"{m.group(1).replace(',', '.')}%"
    return None


def extract_volume(text: str) -> str | None:
    """Trích thể tích (ml/cl/l)."""
    m = _VOL.search(text)
    return f"{m.group(1).replace(',', '.')}{m.group(2).lower()}" if m else None


def _is_official(url: str, sites: tuple[str, ...]) -> bool:
    host = urlparse(url).netloc.lower()
    return any(host == s or host.endswith("." + s) for s in sites)


def _query(q: str) -> list[dict[str, Any]]:
    s = get_settings()
    try:
        r = requests.get(f"{s.searxng_url}/search", params={"q": q, "format": "json"}, timeout=30)
        r.raise_for_status()
        return list(r.json().get("results", []))
    except (requests.RequestException, ValueError) as exc:
        raise ServiceError("searxng", f"Không gọi được SearXNG tại {s.searxng_url}: {exc}") from exc


def search_product(product: ProductData) -> dict[str, Any]:
    """Tìm nguồn chính hãng; trả về {abv, volume, sources, snippets}. Không tìm thấy -> None."""
    name = " ".join(x for x in (product.brand, product.name) if x) or ""
    if not name:
        return {"abv": None, "volume": None, "sources": [], "snippets": []}
    sites = get_settings().official_sites
    results: list[dict[str, Any]] = []
    for site in sites:
        results += _query(f"site:{site} {name}")
    if not results:
        results = _query(f"{name} official")
    results.sort(key=lambda r: not _is_official(r.get("url", ""), sites))
    abv = volume = None
    snippets: list[str] = []
    for r in results[:8]:
        text = f"{r.get('title', '')}. {r.get('content', '')}"
        snippets.append(f"{text} ({r.get('url', '')})")
        if _is_official(r.get("url", ""), sites) or not (abv or volume):
            abv = abv or extract_abv(text)
            volume = volume or extract_volume(text)
    return {"abv": abv, "volume": volume,
            "sources": [r.get("url", "") for r in results[:8]], "snippets": snippets}

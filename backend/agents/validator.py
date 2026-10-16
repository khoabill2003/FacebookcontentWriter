"""Rule engine kiểm tra bài viết."""
from __future__ import annotations

import re
import unicodedata
from typing import Optional

from backend.models import Post, ProductData

RULES = ("CTA", "SLOGAN", "HASHTAG", "WARNING", "CONTACT")
_WARNING_KEYWORDS = ("uống có trách nhiệm", "uong co trach nhiem", "không lái xe", "chưa đủ 18", "dưới 18")
_NUM_UNIT = re.compile(r"(\d+(?:[.,]\d+)?)\s*(%|(?:ml|cl|lít|l)\b)", re.IGNORECASE)


def _norm(text: str) -> str:
    return unicodedata.normalize("NFC", text).lower()


def _volume_ml(text: str) -> set[str]:
    """Quy đổi thể tích về ml để so sánh."""
    out: set[str] = set()
    for num, unit in _NUM_UNIT.findall(text):
        u = unit.lower()
        if u in ("%",):
            continue
        n = float(num.replace(",", "."))
        n = n * {"ml": 1, "cl": 10, "l": 1000, "lít": 1000}[u]
        out.add(str(int(n)) if n == int(n) else str(n))
    return out


def _abv(text: str) -> set[str]:
    """Các giá trị % ABV (chuẩn hóa dạng số)."""
    return {str(float(n.replace(",", "."))).removesuffix(".0") for n, u in _NUM_UNIT.findall(text) if u == "%"}


def validate_post(
    post: Post,
    product: Optional[ProductData] = None,
    slogans: Optional[list[str]] = None,
    contact_markers: Optional[list[str]] = None,
) -> list[str]:
    """Trả về danh sách lỗi (rỗng nếu hợp lệ).

    Mã lỗi: CTA, SLOGAN, HASHTAG, WARNING, CONTACT, ABV, VOLUME.
    ABV/VOLUME: số liệu trong bài phải khớp dữ liệu nguồn; nếu nguồn là null thì bài không được chứa.
    """
    issues: list[str] = []
    text = post.full_text()

    if not post.cta.strip():
        issues.append("CTA")
    if not post.slogan.strip():
        issues.append("SLOGAN")
    elif slogans and not any(_norm(s) in _norm(post.slogan) or _norm(post.slogan) in _norm(s) for s in slogans):
        issues.append("SLOGAN")
    if not post.hashtags or not all(h.startswith("#") and len(h) > 1 for h in post.hashtags):
        issues.append("HASHTAG")
    if not any(k in _norm(post.warning) for k in _WARNING_KEYWORDS):
        issues.append("WARNING")
    if not post.contact.strip():
        issues.append("CONTACT")
    elif contact_markers and not any(m.lower() in _norm(post.contact) for m in contact_markers):
        issues.append("CONTACT")

    p = product or ProductData()
    in_abv = _abv(text)
    allowed_abv = _abv(p.abv) if p.abv else set()
    if in_abv - allowed_abv:
        issues.append("ABV")
    in_vol = _volume_ml(text)
    allowed_vol = _volume_ml(p.volume) if p.volume else set()
    if in_vol - allowed_vol:
        issues.append("VOLUME")
    return issues


def validate_posts(posts: list[Post], product: Optional[ProductData] = None, **kw) -> dict[int, list[str]]:
    """Validate nhiều bài; chỉ trả về các bài có lỗi theo chỉ số."""
    result = {i: validate_post(p, product, **kw) for i, p in enumerate(posts)}
    return {i: v for i, v in result.items() if v}

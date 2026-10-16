"""Generator: gọi Ollama sinh bài Facebook tiếng Việt."""
from __future__ import annotations

import json
import re
from typing import Any, Optional

import requests

from backend.config import get_settings
from backend.errors import ServiceError
from backend.models import Post, ProductData

OUTPUT_SPEC = (
    "Trả về DUY NHẤT một mảng JSON gồm {n} bài, mỗi bài là object với các khóa: "
    '"title","body","slogan","cta","contact","warning","hashtags" (mảng chuỗi bắt đầu bằng #). '
    "Viết tiếng Việt. Warning phải có cảnh báo uống rượu có trách nhiệm."
)


def load_system_prompt() -> str:
    """Đọc SYSTEM_PROMPT từ knowledge/brand-guide.md."""
    path = get_settings().knowledge_dir / "brand-guide.md"
    try:
        return path.read_text(encoding="utf-8")
    except OSError as exc:
        raise ServiceError("knowledge", f"Không đọc được {path}: {exc}") from exc


def build_context(product: ProductData, official: dict[str, Any], brand_context: list[str]) -> str:
    """Ghép PRODUCT DATA, OFFICIAL INFO, BRAND GUIDELINES; số liệu null bị cấm dùng."""
    rules = []
    if not product.abv:
        rules.append("KHÔNG có dữ liệu ABV: tuyệt đối không nêu nồng độ cồn.")
    if not product.volume:
        rules.append("KHÔNG có dữ liệu dung tích: tuyệt đối không nêu dung tích.")
    return (
        f"PRODUCT DATA:\n{json.dumps(product.model_dump(), ensure_ascii=False)}\n\n"
        f"OFFICIAL INFO:\n{json.dumps(official, ensure_ascii=False)}\n\n"
        f"BRAND GUIDELINES:\n" + "\n---\n".join(brand_context) + "\n\n"
        + "\n".join(rules)
    )


def parse_posts(text: str) -> list[Post]:
    """Phân tích mảng JSON bài viết từ đầu ra của model."""
    text = re.sub(r"<think>.*?</think>", "", text, flags=re.DOTALL)
    m = re.search(r"\[.*\]", text, re.DOTALL)
    if not m:
        raise ServiceError("generator", "Model không trả về mảng JSON.")
    try:
        items = json.loads(m.group(0))
        return [Post(**{k: v for k, v in it.items() if k in Post.model_fields}) for it in items]
    except (json.JSONDecodeError, TypeError, ValueError) as exc:
        raise ServiceError("generator", f"JSON bài viết không hợp lệ: {exc}") from exc


def generate_posts(
    product: ProductData,
    official: dict[str, Any],
    brand_context: list[str],
    n: int,
    feedback: Optional[dict[int, list[str]]] = None,
    previous: Optional[list[Post]] = None,
) -> list[Post]:
    """Sinh n bài; nếu có feedback thì yêu cầu sửa các mục thiếu."""
    s = get_settings()
    user = build_context(product, official, brand_context) + "\n\n" + OUTPUT_SPEC.format(n=n)
    if feedback and previous:
        user += (
            "\n\nBản trước còn lỗi (mã lỗi theo chỉ số bài): "
            + json.dumps(feedback, ensure_ascii=False)
            + "\nBản trước:\n"
            + json.dumps([p.model_dump() for p in previous], ensure_ascii=False)
            + "\nHãy sửa đủ các mục thiếu."
        )
    try:
        r = requests.post(
            f"{s.ollama_url}/api/chat",
            json={
                "model": s.generator_model,
                "stream": False,
                "messages": [{"role": "system", "content": load_system_prompt()},
                             {"role": "user", "content": user}],
            },
            timeout=s.request_timeout,
        )
        r.raise_for_status()
    except requests.RequestException as exc:
        raise ServiceError("ollama", f"Không gọi được Ollama tại {s.ollama_url}: {exc}") from exc
    return parse_posts(r.json().get("message", {}).get("content", ""))

"""Các endpoint HTTP."""
from __future__ import annotations

from typing import Any

from fastapi.concurrency import run_in_threadpool

from fastapi import APIRouter, File, Form, HTTPException, UploadFile

from backend import exporters, graph
from backend.agents import rag
from backend.errors import ServiceError

router = APIRouter()
MAX_IMAGE_BYTES = 10 * 1024 * 1024


@router.get("/health")
def health() -> dict[str, str]:
    """Kiểm tra backend sống."""
    return {"status": "ok"}


@router.post("/api/content/generate")
async def generate(image: UploadFile = File(...), num_posts: int = Form(3)) -> dict[str, Any]:
    """Nhận ảnh + số bài (3-5), trả về bài viết kèm caption/Markdown/HTML."""
    if not 3 <= num_posts <= 5:
        raise HTTPException(422, "num_posts phải từ 3 đến 5.")
    if not (image.content_type or "").startswith("image/"):
        raise HTTPException(415, "File tải lên phải là ảnh.")
    data = await image.read()
    if not data or len(data) > MAX_IMAGE_BYTES:
        raise HTTPException(413, "Ảnh rỗng hoặc vượt quá 10MB.")
    try:
        state = await run_in_threadpool(graph.run, data, num_posts)
    except ServiceError as exc:
        raise HTTPException(503, str(exc)) from exc
    posts = state["posts"]
    return {
        "product": state["product"].model_dump(),
        "official_sources": state["official"].get("sources", []),
        "validation_issues": {str(k): v for k, v in state.get("issues", {}).items()},
        "posts": [
            {**p.model_dump(), "caption": exporters.to_caption(p)} for p in posts
        ],
        "markdown": exporters.to_markdown(posts),
        "html": exporters.to_html(posts),
    }


@router.post("/api/knowledge/ingest")
def ingest() -> dict[str, int]:
    """Nạp knowledge/*.md và catalogues/*.pdf vào Qdrant."""
    try:
        return {"chunks": rag.ingest()}
    except ServiceError as exc:
        raise HTTPException(503, str(exc)) from exc

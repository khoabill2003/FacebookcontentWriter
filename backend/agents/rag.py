"""RAG: embedding bge-m3 + Qdrant; ingest knowledge/*.md và PDF catalogue."""
from __future__ import annotations

import uuid
from functools import lru_cache
from pathlib import Path
from typing import Any

from backend.config import get_settings
from backend.errors import ServiceError


@lru_cache(maxsize=1)
def _embedder() -> Any:
    from sentence_transformers import SentenceTransformer

    return SentenceTransformer(get_settings().embedding_model)


def _client() -> Any:
    from qdrant_client import QdrantClient

    return QdrantClient(url=get_settings().qdrant_url, timeout=30)


def chunk_text(text: str, size: int = 800, overlap: int = 100) -> list[str]:
    """Cắt văn bản thành các đoạn có chồng lấp."""
    text = text.strip()
    if not text:
        return []
    step = max(size - overlap, 1)
    return [text[i:i + size] for i in range(0, len(text), step)]


def _read_pdf(path: Path) -> str:
    from pypdf import PdfReader

    return "\n".join(page.extract_text() or "" for page in PdfReader(str(path)).pages)


def collect_documents() -> list[tuple[str, str]]:
    """Trả về [(nguồn, nội dung)] từ knowledge/*.md và catalogues/*.pdf."""
    s = get_settings()
    docs: list[tuple[str, str]] = []
    for p in sorted(s.knowledge_dir.glob("*.md")):
        docs.append((p.name, p.read_text(encoding="utf-8")))
    for p in sorted(s.catalogues_dir.glob("*.pdf")):
        docs.append((p.name, _read_pdf(p)))
    return docs


def ingest() -> int:
    """Nạp toàn bộ tài liệu vào Qdrant; trả về số chunk."""
    from qdrant_client.models import Distance, PointStruct, VectorParams

    s = get_settings()
    chunks = [(src, c) for src, text in collect_documents() for c in chunk_text(text)]
    if not chunks:
        return 0
    try:
        vectors = _embedder().encode([c for _, c in chunks], normalize_embeddings=True)
        client = _client()
        if client.collection_exists(s.qdrant_collection):
            client.delete_collection(s.qdrant_collection)
        client.create_collection(
            s.qdrant_collection, vectors_config=VectorParams(size=len(vectors[0]), distance=Distance.COSINE)
        )
        client.upsert(
            s.qdrant_collection,
            points=[
                PointStruct(id=str(uuid.uuid4()), vector=v.tolist(), payload={"source": src, "text": c})
                for (src, c), v in zip(chunks, vectors)
            ],
        )
    except ServiceError:
        raise
    except Exception as exc:  # noqa: BLE001 - gói lỗi kết nối Qdrant
        raise ServiceError("qdrant", f"Ingest thất bại (Qdrant {s.qdrant_url} có chạy không?): {exc}") from exc
    return len(chunks)


def retrieve(query: str, limit: int = 5) -> list[str]:
    """Truy xuất các đoạn liên quan nhất."""
    s = get_settings()
    try:
        vec = _embedder().encode([query], normalize_embeddings=True)[0].tolist()
        hits = _client().search(s.qdrant_collection, query_vector=vec, limit=limit)
    except Exception as exc:  # noqa: BLE001
        raise ServiceError("qdrant", f"Truy xuất thất bại (đã chạy ingest chưa? Qdrant {s.qdrant_url}): {exc}") from exc
    return [h.payload["text"] for h in hits if h.payload]

"""Cấu hình ứng dụng đọc từ biến môi trường."""
from __future__ import annotations

import os
from dataclasses import dataclass, field
from pathlib import Path

ROOT_DIR = Path(__file__).resolve().parent.parent


def _env(name: str, default: str) -> str:
    return os.getenv(name, default)


@dataclass(frozen=True)
class Settings:
    """Tập hợp các thiết lập (URL, tên model, đường dẫn)."""

    ollama_url: str = field(default_factory=lambda: _env("OLLAMA_URL", "http://localhost:11434"))
    qdrant_url: str = field(default_factory=lambda: _env("QDRANT_URL", "http://localhost:6333"))
    searxng_url: str = field(default_factory=lambda: _env("SEARXNG_URL", "http://localhost:8080"))
    generator_model: str = field(default_factory=lambda: _env("GENERATOR_MODEL", "qwen3:32b"))
    vision_backend: str = field(default_factory=lambda: _env("VISION_BACKEND", "ollama"))
    vision_ollama_model: str = field(default_factory=lambda: _env("VISION_OLLAMA_MODEL", "qwen2.5vl:7b"))
    vision_hf_model: str = field(default_factory=lambda: _env("VISION_HF_MODEL", "Qwen/Qwen2.5-VL-7B-Instruct"))
    embedding_model: str = field(default_factory=lambda: _env("EMBEDDING_MODEL", "BAAI/bge-m3"))
    qdrant_collection: str = field(default_factory=lambda: _env("QDRANT_COLLECTION", "ruou_thoi_dai"))
    knowledge_dir: Path = field(default_factory=lambda: Path(_env("KNOWLEDGE_DIR", str(ROOT_DIR / "knowledge"))))
    catalogues_dir: Path = field(default_factory=lambda: Path(_env("CATALOGUES_DIR", str(ROOT_DIR / "catalogues"))))
    official_sites: tuple[str, ...] = field(
        default_factory=lambda: tuple(
            s.strip() for s in _env("OFFICIAL_SITES", "suntory.com,thewhiskyexchange.com").split(",") if s.strip()
        )
    )
    request_timeout: int = field(default_factory=lambda: int(_env("REQUEST_TIMEOUT", "600")))
    max_regenerations: int = field(default_factory=lambda: int(_env("MAX_REGENERATIONS", "2")))


def get_settings() -> Settings:
    """Trả về Settings mới nhất từ môi trường."""
    return Settings()

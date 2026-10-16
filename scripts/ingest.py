"""Nạp knowledge/*.md và catalogues/*.pdf vào Qdrant.

Chạy từ gốc repo: python scripts/ingest.py
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from backend.agents import rag  # noqa: E402
from backend.errors import ServiceError  # noqa: E402

if __name__ == "__main__":
    try:
        print(f"Đã nạp {rag.ingest()} chunk.")
    except ServiceError as exc:
        sys.exit(f"Lỗi: {exc}")

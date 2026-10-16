import glob
import os
import uuid

import requests

from backend import config
from backend.agents.llm import embed


def _chunks(text, size=800):
    parts, cur = [], ""
    for para in text.split("\n\n"):
        if cur and len(cur) + len(para) > size:
            parts.append(cur.strip())
            cur = ""
        cur += para + "\n\n"
    if cur.strip():
        parts.append(cur.strip())
    return parts


def ingest(directory=None):
    """Embed all knowledge/*.md files into Qdrant. Returns chunk count."""
    base = f"{config.QDRANT_URL}/collections/{config.COLLECTION}"
    points = []
    for path in glob.glob(os.path.join(directory or config.KNOWLEDGE_DIR, "*.md")):
        with open(path, encoding="utf-8") as f:
            for chunk in _chunks(f.read()):
                points.append({
                    "id": str(uuid.uuid4()),
                    "vector": embed(chunk),
                    "payload": {"text": chunk, "source": os.path.basename(path)},
                })
    if not points:
        return 0
    requests.put(
        base,
        json={"vectors": {"size": len(points[0]["vector"]), "distance": "Cosine"}},
        timeout=30,
    )
    requests.put(f"{base}/points?wait=true", json={"points": points}, timeout=120).raise_for_status()
    return len(points)


def retrieve(query, limit=5):
    r = requests.post(
        f"{config.QDRANT_URL}/collections/{config.COLLECTION}/points/search",
        json={"vector": embed(query), "limit": limit, "with_payload": True},
        timeout=30,
    )
    r.raise_for_status()
    return [h["payload"]["text"] for h in r.json()["result"]]

import os

OLLAMA_URL = os.getenv("OLLAMA_URL", "http://localhost:11434")
SEARXNG_URL = os.getenv("SEARXNG_URL", "http://localhost:8080")
QDRANT_URL = os.getenv("QDRANT_URL", "http://localhost:6333")
LLM_MODEL = os.getenv("LLM_MODEL", "qwen3:32b")
VISION_MODEL = os.getenv("VISION_MODEL", "qwen2.5vl:7b")
EMBED_MODEL = os.getenv("EMBED_MODEL", "bge-m3")
COLLECTION = os.getenv("QDRANT_COLLECTION", "ruou_thoi_dai")
KNOWLEDGE_DIR = os.getenv(
    "KNOWLEDGE_DIR",
    os.path.join(os.path.dirname(os.path.dirname(__file__)), "knowledge"),
)

# Rượu Thời Đại AI Content Factory (local, Agentic RAG)

Pipeline: Vision (Qwen2.5-VL) → Search (SearXNG) → RAG (Qdrant + bge-m3) → Generator (Qwen3 32B) → Validator (regenerates missing sections).

```
docker compose up -d
docker compose exec ollama sh -c "ollama pull qwen3:32b && ollama pull qwen2.5vl:7b && ollama pull bge-m3"
curl -X POST localhost:8000/api/ingest      # index knowledge/*.md
# open http://localhost:8000 (upload UI) or http://localhost:3000 (OpenWebUI)
```
SearXNG needs `json` enabled under `search.formats` in its settings.yml. Edit `knowledge/` with real slogan/contact. Tests: `pytest tests`.

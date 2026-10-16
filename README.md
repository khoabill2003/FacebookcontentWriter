# AI Content Factory – Rượu Thời Đại

Ứng dụng chạy **hoàn toàn local**, kiến trúc **Agentic RAG**: upload ảnh chai rượu → nhận diện → tìm nguồn chính hãng → đọc catalogue/brand guideline → sinh 3–5 bài Facebook → validate → xuất caption / Markdown / HTML.

## Kiến trúc

| Thành phần | Công nghệ |
|---|---|
| Frontend | Next.js (App Router, TypeScript) |
| Backend | FastAPI + LangGraph |
| LLM | Ollama (`qwen3:32b`, cấu hình được) |
| Vision | Qwen2.5-VL (Ollama `qwen2.5vl` hoặc transformers) |
| Search | SearXNG (không cần API key) |
| Vector DB | Qdrant + embedding `BAAI/bge-m3` |

## Sơ đồ luồng

```
Ảnh → [Vision] → [Search chính hãng] → [RAG: brand/slogan/contact/catalogue]
        → [Generator] → [Validator] ──thiếu mục──► Generator (tối đa 2 lần regenerate)
                              │ đạt
                              ▼
                  Caption (txt) / Markdown / HTML
```

Validator kiểm tra: CTA, SLOGAN, HASHTAG, WARNING (uống rượu có trách nhiệm), CONTACT, và ABV/dung tích phải khớp dữ liệu nguồn. **Không bịa số liệu**: nếu không tìm thấy ABV/dung tích thì để `null` và bài viết không được nêu số đó.

## Hướng dẫn chạy

1. Chuẩn bị cấu hình:
   ```bash
   cp .env.example .env     # đổi SEARXNG_SECRET
   ```
2. Điền nội dung thật vào `knowledge/brand-guide.md`, `slogan.md`, `contact.md` (thay các `{{...}}`); thả PDF vào `catalogues/`.
3. Khởi động dịch vụ:
   ```bash
   docker compose up -d
   ```
4. Tải model:
   ```bash
   ./scripts/pull_models.sh      # qwen3:32b + qwen2.5vl:7b
   ```
5. Nạp tri thức vào Qdrant (một trong hai cách):
   ```bash
   curl -X POST http://localhost:8000/api/knowledge/ingest
   # hoặc chạy local: pip install -r backend/requirements.txt && python scripts/ingest.py
   ```
6. Mở UI: http://localhost:3001 (OpenWebUI: http://localhost:3000, backend: http://localhost:8000/docs).

### API

- `GET /health`
- `POST /api/content/generate` (multipart: `image`, `num_posts` 3–5)
- `POST /api/knowledge/ingest`

Khi Ollama/Qdrant/SearXNG không chạy, API trả `503` kèm thông báo dịch vụ nào lỗi.

### Test

```bash
pip install pytest pydantic fastapi
python -m pytest
```

## Yêu cầu phần cứng

- `qwen3:32b` (Q4): ~24GB VRAM (hoặc ≥32GB RAM, chậm hơn). Có thể đổi `GENERATOR_MODEL` sang model nhỏ hơn (ví dụ `qwen3:8b`).
- Vision 7B: ~8GB VRAM. Embedding bge-m3: ~2GB.
- Khuyến nghị: GPU NVIDIA 24GB, RAM 32GB, ổ đĩa trống 60GB.

## Roadmap – tự động hóa với n8n

Google Drive (ảnh mới) → gọi `/api/content/generate` → lưu Notion → duyệt → đăng Facebook.

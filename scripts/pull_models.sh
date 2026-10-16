#!/usr/bin/env bash
# Tải model cho Ollama (container tên "ollama" trong docker compose).
set -euo pipefail
GENERATOR_MODEL="${GENERATOR_MODEL:-qwen3:32b}"
VISION_OLLAMA_MODEL="${VISION_OLLAMA_MODEL:-qwen2.5vl:7b}"
docker compose exec ollama ollama pull "$GENERATOR_MODEL"
docker compose exec ollama ollama pull "$VISION_OLLAMA_MODEL"

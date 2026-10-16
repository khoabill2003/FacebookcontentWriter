"""Vision agent: nhận diện chai rượu từ ảnh."""
from __future__ import annotations

import base64
import json
import re
from functools import lru_cache
from io import BytesIO
from typing import Any

import requests

from backend.config import get_settings
from backend.errors import ServiceError
from backend.models import ProductData

VISION_PROMPT = (
    "Identify the alcohol bottle in the image. Return ONLY a JSON object with keys: "
    '"name" (product name), "brand", "abv" (e.g. "43%"), "volume" (e.g. "700ml"). '
    "Use null for any value not clearly visible on the label. Do not guess."
)


def parse_vision_json(text: str) -> ProductData:
    """Trích JSON đầu tiên trong văn bản trả về của model."""
    m = re.search(r"\{.*\}", text, re.DOTALL)
    if not m:
        raise ServiceError("vision", "Model không trả về JSON.")
    try:
        data: dict[str, Any] = json.loads(m.group(0))
    except json.JSONDecodeError as exc:
        raise ServiceError("vision", f"JSON không hợp lệ: {exc}") from exc
    clean = {k: (str(data[k]).strip() or None) if data.get(k) is not None else None
             for k in ("name", "brand", "abv", "volume")}
    return ProductData(**clean)


def _ollama(image: bytes) -> str:
    s = get_settings()
    try:
        r = requests.post(
            f"{s.ollama_url}/api/chat",
            json={
                "model": s.vision_ollama_model,
                "stream": False,
                "messages": [{"role": "user", "content": VISION_PROMPT,
                              "images": [base64.b64encode(image).decode()]}],
            },
            timeout=s.request_timeout,
        )
        r.raise_for_status()
    except requests.RequestException as exc:
        raise ServiceError("ollama", f"Không gọi được Ollama tại {s.ollama_url}: {exc}") from exc
    return r.json().get("message", {}).get("content", "")


@lru_cache(maxsize=1)
def _load_hf() -> tuple[Any, Any]:
    """Lazy load Qwen2.5-VL qua transformers."""
    try:
        from transformers import AutoModelForVision2Seq, AutoProcessor
    except ImportError as exc:
        raise ServiceError("vision", "Chưa cài transformers/torch cho VISION_BACKEND=transformers.") from exc
    name = get_settings().vision_hf_model
    return AutoProcessor.from_pretrained(name), AutoModelForVision2Seq.from_pretrained(name, device_map="auto")


def _transformers(image: bytes) -> str:
    from PIL import Image

    processor, model = _load_hf()
    img = Image.open(BytesIO(image)).convert("RGB")
    messages = [{"role": "user", "content": [{"type": "image"}, {"type": "text", "text": VISION_PROMPT}]}]
    prompt = processor.apply_chat_template(messages, add_generation_prompt=True)
    inputs = processor(text=[prompt], images=[img], return_tensors="pt").to(model.device)
    out = model.generate(**inputs, max_new_tokens=256)
    return processor.batch_decode(out[:, inputs["input_ids"].shape[1]:], skip_special_tokens=True)[0]


def identify_product(image: bytes) -> ProductData:
    """Nhận diện sản phẩm từ bytes ảnh."""
    backend = get_settings().vision_backend
    text = _transformers(image) if backend == "transformers" else _ollama(image)
    return parse_vision_json(text)

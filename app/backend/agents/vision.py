import base64
import json

from backend import config
from backend.agents.llm import chat

PROMPT = (
    "Identify the bottle in the image. Return ONLY JSON with keys: "
    "product_name, brand, abv, volume. Use null when unknown."
)


def identify_product(image_bytes):
    img = base64.b64encode(image_bytes).decode()
    raw = chat(PROMPT, model=config.VISION_MODEL, images=[img], as_json=True)
    return json.loads(raw)

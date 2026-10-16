import json
import os

from backend import config
from backend.agents import generator, rag, search, validator, vision


def _known():
    known = {}
    for key in ("slogan", "contact"):
        path = os.path.join(config.KNOWLEDGE_DIR, f"{key}.md")
        if os.path.exists(path):
            lines = [l.strip("-* #").strip() for l in open(path, encoding="utf-8") if l.strip() and not l.startswith("#")]
            known[key] = lines[0] if lines else ""
    return known


def run(image_bytes=None, product_name=None, n=3, max_retries=2):
    product = vision.identify_product(image_bytes) if image_bytes else {"product_name": product_name}
    name = product.get("product_name") or product_name
    official = search.search_product(name)
    brand = rag.retrieve(f"brand guideline slogan CTA liên hệ {name}")
    known = _known()
    posts = generator.generate(product, official, brand, n)
    results = []
    for post in posts:
        missing = validator.validate(post, known)
        tries = 0
        while missing and tries < max_retries:
            post = generator.generate(product, official, brand, 1, missing)[0]
            missing = validator.validate(post, known)
            tries += 1
        results.append({"text": post, "missing": missing})
    return {"product": product, "official": official, "posts": results}

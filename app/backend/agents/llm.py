import requests

from backend import config


def chat(prompt, system="", model=None, images=None, as_json=False):
    message = {"role": "user", "content": prompt}
    if images:
        message["images"] = images
    messages = ([{"role": "system", "content": system}] if system else []) + [message]
    payload = {"model": model or config.LLM_MODEL, "messages": messages, "stream": False}
    if as_json:
        payload["format"] = "json"
    r = requests.post(f"{config.OLLAMA_URL}/api/chat", json=payload, timeout=600)
    r.raise_for_status()
    return r.json()["message"]["content"]


def embed(text):
    r = requests.post(
        f"{config.OLLAMA_URL}/api/embeddings",
        json={"model": config.EMBED_MODEL, "prompt": text},
        timeout=120,
    )
    r.raise_for_status()
    return r.json()["embedding"]

import requests

from backend import config


def search_product(product, site="suntory.com", limit=5):
    query = f"site:{site} {product}" if site else product
    r = requests.get(
        f"{config.SEARXNG_URL}/search",
        params={"q": query, "format": "json"},
        timeout=30,
    )
    r.raise_for_status()
    results = r.json().get("results", [])[:limit]
    return [
        {"title": x.get("title"), "url": x.get("url"), "content": x.get("content")}
        for x in results
    ]

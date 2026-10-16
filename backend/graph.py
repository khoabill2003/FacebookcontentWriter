"""LangGraph orchestrator: vision -> search -> rag -> generator -> validator (regenerate tối đa N lần)."""
from __future__ import annotations

import re
from functools import lru_cache
from typing import Any, TypedDict

from langgraph.graph import END, StateGraph

from backend.agents import generator, rag, search, validator, vision
from backend.config import get_settings
from backend.models import Post, ProductData


class State(TypedDict, total=False):
    """Trạng thái chạy qua đồ thị."""

    image: bytes
    n_posts: int
    product: ProductData
    official: dict[str, Any]
    brand_context: list[str]
    posts: list[Post]
    issues: dict[int, list[str]]
    attempts: int


def _vision(state: State) -> State:
    return {"product": vision.identify_product(state["image"])}


def _search(state: State) -> State:
    official = search.search_product(state["product"])
    p = state["product"]
    # Dữ liệu chính hãng ưu tiên; không tìm thấy thì giữ giá trị từ nhãn (có thể null).
    merged = p.model_copy(update={"abv": official["abv"] or p.abv, "volume": official["volume"] or p.volume})
    return {"official": official, "product": merged}


def _rag(state: State) -> State:
    p = state["product"]
    q = f"Brand guideline, slogan, CTA, liên hệ, {p.brand or ''} {p.name or ''}"
    return {"brand_context": rag.retrieve(q)}


def _generate(state: State) -> State:
    attempts = state.get("attempts", 0)
    posts = generator.generate_posts(
        state["product"], state["official"], state["brand_context"], state["n_posts"],
        feedback=state.get("issues") or None, previous=state.get("posts"),
    )
    return {"posts": posts, "attempts": attempts + 1}


def _lines(name: str) -> list[str]:
    path = get_settings().knowledge_dir / name
    if not path.exists():
        return []
    return [re.sub(r"^[\s>*\-]+", "", ln).strip() for ln in path.read_text(encoding="utf-8").splitlines()
            if ln.strip() and not ln.lstrip().startswith(("#", "<!--"))]


def _validate(state: State) -> State:
    slogans = [s for s in _lines("slogan.md") if "{{" not in s] or None
    return {"issues": validator.validate_posts(state["posts"], state["product"], slogans=slogans)}


def _route(state: State) -> str:
    if state.get("issues") and state.get("attempts", 0) <= get_settings().max_regenerations:
        return "generate"
    return END


@lru_cache(maxsize=1)
def build_graph() -> Any:
    """Biên dịch đồ thị agent."""
    g = StateGraph(State)
    for name, fn in (("vision", _vision), ("search", _search), ("rag", _rag),
                     ("generate", _generate), ("validate", _validate)):
        g.add_node(name, fn)
    g.set_entry_point("vision")
    g.add_edge("vision", "search")
    g.add_edge("search", "rag")
    g.add_edge("rag", "generate")
    g.add_edge("generate", "validate")
    g.add_conditional_edges("validate", _route, {"generate": "generate", END: END})
    return g.compile()


def run(image: bytes, n_posts: int) -> State:
    """Chạy toàn bộ pipeline."""
    return build_graph().invoke({"image": image, "n_posts": n_posts, "attempts": 0})

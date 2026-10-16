"""Xuất bài viết ra caption (txt), Markdown và HTML."""
from __future__ import annotations

import html

from backend.models import Post


def to_caption(post: Post) -> str:
    """Caption Facebook dạng văn bản thuần."""
    return post.full_text()


def to_markdown(posts: list[Post]) -> str:
    """Markdown cho nhiều bài."""
    out: list[str] = []
    for i, p in enumerate(posts, 1):
        lines = [f"## Bài {i}: {p.title}", "", p.body, ""]
        if p.slogan:
            lines += [f"> {p.slogan}", ""]
        if p.cta:
            lines += [f"**{p.cta}**", ""]
        if p.contact:
            lines += [p.contact, ""]
        if p.warning:
            lines += [f"*{p.warning}*", ""]
        if p.hashtags:
            lines += [" ".join(p.hashtags), ""]
        out.append("\n".join(lines))
    return "\n---\n\n".join(out)


def _p(text: str) -> str:
    return html.escape(text).replace("\n", "<br>")


def to_html(posts: list[Post]) -> str:
    """HTML đầy đủ (đã escape) cho nhiều bài."""
    arts: list[str] = []
    for p in posts:
        parts = [f"<h2>{html.escape(p.title)}</h2>", f"<p>{_p(p.body)}</p>"]
        if p.slogan:
            parts.append(f"<blockquote>{_p(p.slogan)}</blockquote>")
        if p.cta:
            parts.append(f"<p><strong>{_p(p.cta)}</strong></p>")
        if p.contact:
            parts.append(f"<p>{_p(p.contact)}</p>")
        if p.warning:
            parts.append(f"<p><em>{_p(p.warning)}</em></p>")
        if p.hashtags:
            parts.append(f"<p>{html.escape(' '.join(p.hashtags))}</p>")
        arts.append("<article>\n" + "\n".join(parts) + "\n</article>")
    return (
        '<!DOCTYPE html>\n<html lang="vi">\n<head><meta charset="utf-8">'
        "<title>Rượu Thời Đại</title></head>\n<body>\n" + "\n".join(arts) + "\n</body>\n</html>\n"
    )

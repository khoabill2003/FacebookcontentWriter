from backend import exporters
from backend.models import Post

POST = Post(title="Tiêu đề <b>", body="Thân bài", slogan="Slogan", cta="Liên hệ ngay",
            contact="Hotline: 0900", warning="Uống có trách nhiệm.", hashtags=["#ruou"])


def test_caption_contains_all_parts():
    t = exporters.to_caption(POST)
    for part in ("Tiêu đề", "Thân bài", "Slogan", "Liên hệ ngay", "Hotline", "#ruou"):
        assert part in t


def test_markdown_multiple_posts():
    md = exporters.to_markdown([POST, POST])
    assert "## Bài 1" in md and "## Bài 2" in md and "---" in md


def test_html_escapes():
    h = exporters.to_html([POST])
    assert "&lt;b&gt;" in h and "<b>" not in h and "<article>" in h

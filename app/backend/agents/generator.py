import json

from backend.agents.llm import chat

SYSTEM_PROMPT = """Bạn là copywriter của Rượu Thời Đại.
Viết bài Facebook tiếng Việt theo BRAND GUIDELINES. Chỉ dùng dữ liệu trong
PRODUCT DATA / OFFICIAL INFO, tuyệt đối không bịa số liệu.
Bài viết phải có: slogan, CTA, thông tin liên hệ, cảnh báo uống có trách nhiệm, hashtag."""


def build_context(product, official, brand_context):
    return (
        f"PRODUCT DATA:\n{json.dumps(product, ensure_ascii=False)}\n\n"
        f"OFFICIAL INFO:\n{json.dumps(official, ensure_ascii=False)}\n\n"
        f"BRAND GUIDELINES:\n" + "\n---\n".join(brand_context)
    )


def generate(product, official, brand_context, n=3, missing=None):
    prompt = build_context(product, official, brand_context) + f"\n\nViết {n} bài Facebook khác nhau, ngăn cách bằng dòng '====='."
    if missing:
        prompt += f"\nBắt buộc bổ sung các mục còn thiếu: {', '.join(missing)}."
    return [p.strip() for p in chat(prompt, system=SYSTEM_PROMPT).split("=====") if p.strip()]

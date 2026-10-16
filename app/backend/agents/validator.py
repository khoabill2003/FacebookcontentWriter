import re

RULES = {
    "CTA": lambda t, k: bool(re.search(r"liên hệ|inbox|đặt hàng|ghé|gọi", t, re.I)),
    "SLOGAN": lambda t, k: bool(k.get("slogan")) and k["slogan"].lower() in t.lower(),
    "HASHTAG": lambda t, k: bool(re.search(r"#\w+", t)),
    "WARNING": lambda t, k: bool(re.search(r"uống có trách nhiệm|không lái xe|dưới 18", t, re.I)),
    "CONTACT": lambda t, k: bool(k.get("contact")) and k["contact"].lower() in t.lower(),
}


def validate(text, known=None):
    """Return list of failed rule names. `known` holds slogan/contact strings."""
    known = known or {}
    return [name for name, check in RULES.items() if not check(text, known)]

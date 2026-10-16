import os, sys
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))
from backend.agents.validator import validate

K = {"slogan": "Tinh hoa", "contact": "0909"}


def test_complete_post_passes():
    t = "Tinh hoa. Liên hệ 0909. Uống có trách nhiệm #ruou"
    assert validate(t, K) == []


def test_missing_rules_reported():
    assert set(validate("Xin chào", K)) == {"CTA", "SLOGAN", "HASHTAG", "WARNING", "CONTACT"}

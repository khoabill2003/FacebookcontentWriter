from backend.agents.validator import validate_post
from backend.models import Post, ProductData

GOOD = Post(title="T", body="Rượu 43% dung tích 700ml", slogan="Hài hòa", cta="Đặt ngay",
            contact="Hotline 0900", warning="Uống có trách nhiệm, không lái xe.", hashtags=["#a"])
PRODUCT = ProductData(name="X", abv="43%", volume="700ml")


def test_valid_post():
    assert validate_post(GOOD, PRODUCT) == []


def test_missing_sections():
    issues = validate_post(Post(body="x"), ProductData())
    assert {"CTA", "SLOGAN", "HASHTAG", "WARNING", "CONTACT"} <= set(issues)


def test_abv_mismatch():
    assert "ABV" in validate_post(GOOD, ProductData(abv="40%", volume="700ml"))


def test_null_data_must_not_appear():
    issues = validate_post(GOOD, ProductData())
    assert "ABV" in issues and "VOLUME" in issues


def test_volume_unit_conversion():
    assert "VOLUME" not in validate_post(GOOD, ProductData(abv="43%", volume="0.7l"))


def test_slogan_must_match_list():
    assert "SLOGAN" in validate_post(GOOD, PRODUCT, slogans=["Khác hẳn"])


def test_search_extractors_and_parsers():
    from backend.agents.generator import parse_posts
    from backend.agents.search import extract_abv, extract_volume
    from backend.agents.vision import parse_vision_json

    assert extract_abv("ABV 43% vol") == "43%" and extract_abv("none") is None
    assert extract_volume("Bottle 700 ml") == "700ml" and extract_volume("none") is None
    assert parse_vision_json('x {"name": "A", "abv": null} y').abv is None
    assert parse_posts('<think>.</think>[{"title": "T", "extra": 1}]')[0].title == "T"

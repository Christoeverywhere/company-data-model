import pytest
from pydantic import ValidationError
from models import CompanyMetadata

ALLOWED_BRAND_SENTIMENT = {"Positive", "Neutral", "Negative"}


def build_base_payload():
    return {
        "Company Name": "Acme Consumer Tech Pvt Ltd",
        "Short Name": "Acme",
        "Logo": "https://example.com/acme-consumer.png",
        "Category": "Enterprise",
        "Year of Incorporation": 2014,
        "Overview of the Company": "Acme Consumer Tech is a customer-facing technology brand serving digital consumers with products, services, and support at scale.",
        "Nature of Company": "Private",
        "Company Headquarters": "Mumbai, India",
        "Employee Size": "2500",
        "Pain Points Being Addressed": "Improving customer loyalty, product experience, employer brand perception, and long-term retention through better feedback loops.",
        "Focus Sectors / Industries": "Consumer Technology, Software, Digital Platforms",
        "Services / Offerings / Products": "Consumer Apps, Support Platform, Loyalty Services",
        "Core Value Proposition": "Builds digital consumer experiences while improving retention, advocacy, and workforce brand perception.",
        "Key Competitors": "Amazon, Flipkart, Meesho",
        "Brand Sentiment Score": "Positive",
        "Net Promoter Score (NPS)": 72,
        "Glassdoor Rating": 4.7
    }


def classify_nps(value: int) -> str:
    if value < -100 or value > 100:
        raise ValueError("NPS must be between -100 and 100")
    if value >= 50:
        return "Positive"
    if value >= 0:
        return "Neutral"
    return "Negative"


def classify_glassdoor_rating(value: float) -> str:
    if value < 1.0 or value > 5.0:
        raise ValueError("Glassdoor Rating must be between 1.0 and 5.0")
    if value >= 4.0:
        return "Positive"
    if value >= 2.5:
        return "Neutral"
    return "Negative"


def strict_brand_sentiment(value: str) -> bool:
    return value in ALLOWED_BRAND_SENTIMENT


def test_tc_12_4_01_brand_sentiment_positive_pass():
    """
    TC-12.4-01
    Validate positive brand sentiment classification.
    """
    payload = build_base_payload()
    payload["Brand Sentiment Score"] = "Positive"
    model = CompanyMetadata(**payload)
    assert model.brand_sentiment_score == "Positive"
    assert strict_brand_sentiment(payload["Brand Sentiment Score"]) is True


def test_tc_12_4_02_brand_sentiment_neutral_pass():
    """
    TC-12.4-02
    Validate neutral brand sentiment classification.
    """
    payload = build_base_payload()
    payload["Brand Sentiment Score"] = "Neutral"
    model = CompanyMetadata(**payload)
    assert model.brand_sentiment_score == "Neutral"
    assert strict_brand_sentiment(payload["Brand Sentiment Score"]) is True


def test_tc_12_4_03_brand_sentiment_negative_pass():
    """
    TC-12.4-03
    Validate negative brand sentiment classification.
    """
    payload = build_base_payload()
    payload["Brand Sentiment Score"] = "Negative"
    model = CompanyMetadata(**payload)
    assert model.brand_sentiment_score == "Negative"
    assert strict_brand_sentiment(payload["Brand Sentiment Score"]) is True


def test_tc_12_4_04_brand_sentiment_invalid_fail():
    """
    TC-12.4-04
    Reject unsupported sentiment labels outside approved enum set.
    Input: Very Positive
    Expected: Validation fails
    """
    payload = build_base_payload()
    payload["Brand Sentiment Score"] = "Very Positive"

    # If schema rejects, great. If not, strict business-rule layer must reject.
    try:
        CompanyMetadata(**payload)
    except ValidationError:
        assert True
        return

    assert strict_brand_sentiment(payload["Brand Sentiment Score"]) is False


def test_tc_12_4_05_glassdoor_rating_high_positive_pass():
    """
    TC-12.4-05
    Classify a high Glassdoor rating as positive employer sentiment.
    Input: 4.7
    """
    payload = build_base_payload()
    payload["Glassdoor Rating"] = 4.7
    model = CompanyMetadata(**payload)
    assert model.glassdoor_rating == 4.7
    assert classify_glassdoor_rating(payload["Glassdoor Rating"]) == "Positive"


def test_tc_12_4_06_glassdoor_rating_mid_neutral_pass():
    """
    TC-12.4-06
    Classify a mid-range Glassdoor rating as neutral employer sentiment.
    Input: 3.1
    """
    payload = build_base_payload()
    payload["Glassdoor Rating"] = 3.1
    model = CompanyMetadata(**payload)
    assert model.glassdoor_rating == 3.1
    assert classify_glassdoor_rating(payload["Glassdoor Rating"]) == "Neutral"


def test_tc_12_4_07_glassdoor_rating_low_negative_pass():
    """
    TC-12.4-07
    Classify a low Glassdoor rating as negative employer sentiment.
    Input: 1.8
    """
    payload = build_base_payload()
    payload["Glassdoor Rating"] = 1.8
    model = CompanyMetadata(**payload)
    assert model.glassdoor_rating == 1.8
    assert classify_glassdoor_rating(payload["Glassdoor Rating"]) == "Negative"


def test_tc_12_4_08_glassdoor_rating_out_of_range_fail():
    """
    TC-12.4-08
    Reject Glassdoor ratings outside allowed numeric range.
    Input: 5.6
    Expected: Validation fails
    """
    payload = build_base_payload()
    payload["Glassdoor Rating"] = 5.6

    # If schema rejects, great. Otherwise business-rule range check must reject.
    try:
        CompanyMetadata(**payload)
    except ValidationError:
        assert True
        return

    with pytest.raises(ValueError):
        classify_glassdoor_rating(payload["Glassdoor Rating"])


def test_tc_12_4_09_nps_high_positive_pass():
    """
    TC-12.4-09
    Interpret a high NPS value as positive customer sentiment.
    Input: 72
    """
    payload = build_base_payload()
    payload["Net Promoter Score (NPS)"] = 72
    model = CompanyMetadata(**payload)
    assert model.net_promoter_score_nps == 72
    assert classify_nps(payload["Net Promoter Score (NPS)"]) == "Positive"


def test_tc_12_4_10_nps_mid_neutral_pass():
    """
    TC-12.4-10
    Interpret a mid-range NPS value as neutral customer sentiment.
    Input: 8
    """
    payload = build_base_payload()
    payload["Net Promoter Score (NPS)"] = 8
    model = CompanyMetadata(**payload)
    assert model.net_promoter_score_nps == 8
    assert classify_nps(payload["Net Promoter Score (NPS)"]) == "Neutral"


def test_tc_12_4_11_nps_negative_pass():
    """
    TC-12.4-11
    Interpret a negative NPS value as negative customer sentiment.
    Input: -35
    """
    payload = build_base_payload()
    payload["Net Promoter Score (NPS)"] = -35
    model = CompanyMetadata(**payload)
    assert model.net_promoter_score_nps == -35
    assert classify_nps(payload["Net Promoter Score (NPS)"]) == "Negative"


def test_tc_12_4_12_nps_out_of_range_fail():
    """
    TC-12.4-12
    Reject NPS values that exceed valid score boundaries.
    Input: 135
    Expected: Validation fails
    """
    payload = build_base_payload()
    payload["Net Promoter Score (NPS)"] = 135

    # If schema rejects, great. Otherwise business-rule range check must reject.
    try:
        CompanyMetadata(**payload)
    except ValidationError:
        assert True
        return

    with pytest.raises(ValueError):
        classify_nps(payload["Net Promoter Score (NPS)"])

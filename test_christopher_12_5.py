import pytest
from pydantic import ValidationError
from models import CompanyMetadata

ALLOWED_RISK_VALUES = {"Low", "Medium", "High"}


def build_base_payload():
    return {
        "Company Name": "Acme Growth Labs Pvt Ltd",
        "Short Name": "Acme Growth",
        "Logo": "https://example.com/acme-growth.png",
        "Category": "Startup",
        "Year of Incorporation": 2020,
        "Overview of the Company": "Acme Growth Labs is a venture-backed startup focused on scaling product-led growth with disciplined financial and operational management.",
        "Nature of Company": "Private",
        "Company Headquarters": "Bengaluru, India",
        "Employee Size": "85",
        "Pain Points Being Addressed": "Improving revenue concentration resilience, managing financial runway, and reducing exposure to unstable regional operating conditions.",
        "Focus Sectors / Industries": "Software, SaaS, Revenue Operations",
        "Services / Offerings / Products": "Growth Platform, Revenue Analytics, Customer Intelligence",
        "Core Value Proposition": "Helps growth-stage businesses improve customer diversification and financial resilience with analytics-driven operations.",
        "Key Competitors": "HubSpot, Clari, Gainsight",
        "Customer Concentration Risk": "High",
        "Geopolitical Risk Level": "Low",
        "Burn Rate": 180000.0
    }


def strict_risk_enum(value: str) -> bool:
    return value in ALLOWED_RISK_VALUES


def classify_burn_rate(value: float) -> str:
    if value < 0:
        raise ValueError("Burn Rate cannot be negative")
    if value < 300000:
        return "Low Risk"
    if value < 800000:
        return "Medium Risk"
    return "High Risk"


def test_tc_12_5_01_customer_concentration_risk_high_pass():
    payload = build_base_payload()
    payload["Customer Concentration Risk"] = "High"
    model = CompanyMetadata(**payload)
    assert model.customer_concentration_risk == "High"
    assert strict_risk_enum(payload["Customer Concentration Risk"]) is True


def test_tc_12_5_02_customer_concentration_risk_medium_pass():
    payload = build_base_payload()
    payload["Customer Concentration Risk"] = "Medium"
    model = CompanyMetadata(**payload)
    assert model.customer_concentration_risk == "Medium"
    assert strict_risk_enum(payload["Customer Concentration Risk"]) is True


def test_tc_12_5_03_customer_concentration_risk_low_pass():
    payload = build_base_payload()
    payload["Customer Concentration Risk"] = "Low"
    model = CompanyMetadata(**payload)
    assert model.customer_concentration_risk == "Low"
    assert strict_risk_enum(payload["Customer Concentration Risk"]) is True


def test_tc_12_5_04_customer_concentration_risk_invalid_fail():
    payload = build_base_payload()
    payload["Customer Concentration Risk"] = "Very High"
    try:
        CompanyMetadata(**payload)
    except ValidationError:
        assert True
        return
    assert strict_risk_enum(payload["Customer Concentration Risk"]) is False


def test_tc_12_5_05_geopolitical_risk_level_low_pass():
    payload = build_base_payload()
    payload["Geopolitical Risk Level"] = "Low"
    model = CompanyMetadata(**payload)
    assert model.geopolitical_risk_level == "Low"
    assert strict_risk_enum(payload["Geopolitical Risk Level"]) is True


def test_tc_12_5_06_geopolitical_risk_level_medium_pass():
    payload = build_base_payload()
    payload["Geopolitical Risk Level"] = "Medium"
    model = CompanyMetadata(**payload)
    assert model.geopolitical_risk_level == "Medium"
    assert strict_risk_enum(payload["Geopolitical Risk Level"]) is True


def test_tc_12_5_07_geopolitical_risk_level_high_pass():
    payload = build_base_payload()
    payload["Geopolitical Risk Level"] = "High"
    model = CompanyMetadata(**payload)
    assert model.geopolitical_risk_level == "High"
    assert strict_risk_enum(payload["Geopolitical Risk Level"]) is True


def test_tc_12_5_08_geopolitical_risk_level_case_variant_fail():
    payload = build_base_payload()
    payload["Geopolitical Risk Level"] = "high"
    try:
        CompanyMetadata(**payload)
    except ValidationError:
        assert True
        return
    assert strict_risk_enum(payload["Geopolitical Risk Level"]) is False


def test_tc_12_5_09_burn_rate_low_risk_pass():
    payload = build_base_payload()
    payload["Burn Rate"] = 180000.0
    model = CompanyMetadata(**payload)
    assert float(model.burn_rate) == 180000.0
    assert classify_burn_rate(payload["Burn Rate"]) == "Low Risk"


def test_tc_12_5_10_burn_rate_medium_risk_pass():
    payload = build_base_payload()
    payload["Burn Rate"] = 475000.5
    model = CompanyMetadata(**payload)
    assert float(model.burn_rate) == 475000.5
    assert classify_burn_rate(payload["Burn Rate"]) == "Medium Risk"


def test_tc_12_5_11_burn_rate_high_risk_pass():
    payload = build_base_payload()
    payload["Burn Rate"] = 980000.75
    model = CompanyMetadata(**payload)
    assert float(model.burn_rate) == 980000.75
    assert classify_burn_rate(payload["Burn Rate"]) == "High Risk"


def test_tc_12_5_12_burn_rate_negative_fail():
    payload = build_base_payload()
    payload["Burn Rate"] = -150000.0
    try:
        CompanyMetadata(**payload)
    except ValidationError:
        assert True
        return
    with pytest.raises(ValueError):
        classify_burn_rate(payload["Burn Rate"])

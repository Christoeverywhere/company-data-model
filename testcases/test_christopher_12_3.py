import pytest
from pydantic import ValidationError
from models import CompanyMetadata

ALLOWED_NATURE_VALUES = {"Private", "Public", "Subsidiary", "Partnership", "Non-Profit", "Govt"}


def build_base_payload():
    return {
        "Company Name": "Acme Holdings Pvt Ltd",
        "Short Name": "Acme Holdings",
        "Logo": "https://example.com/acme-holdings.png",
        "Category": "Enterprise",
        "Year of Incorporation": 2012,
        "Overview of the Company": "Acme Holdings is a diversified enterprise operating across multiple business segments with structured governance and long-term strategic investments.",
        "Nature of Company": "Private",
        "Company Headquarters": "Chennai, India",
        "Employee Size": "1200",
        "Pain Points Being Addressed": "Improving operational efficiency, governance visibility, and cross-portfolio performance across multiple business units.",
        "Focus Sectors / Industries": "Holding Companies, Diversified Business Services, Enterprise Operations",
        "Services / Offerings / Products": "Business Operations, Shared Services, Strategic Investments",
        "Core Value Proposition": "Provides governance, operational support, and long-term strategic capital allocation across multiple businesses.",
        "Key Competitors": "Berkshire Hathaway, Tata Sons, SoftBank Group"
    }


def strict_nature_of_company(value: str | None) -> bool:
    if value is None:
        return False
    return value in ALLOWED_NATURE_VALUES


def test_tc_12_3_01_nature_of_company_private_pass():
    """
    TC-12.3-01
    Verify that a privately held company is correctly classified as Private.
    """
    payload = build_base_payload()
    payload["Nature of Company"] = "Private"
    model = CompanyMetadata(**payload)
    assert model.nature_of_company == "Private"
    assert strict_nature_of_company(payload["Nature of Company"]) is True


def test_tc_12_3_02_nature_of_company_public_pass():
    """
    TC-12.3-02
    Verify that a publicly listed company is correctly classified as Public.
    """
    payload = build_base_payload()
    payload["Nature of Company"] = "Public"
    model = CompanyMetadata(**payload)
    assert model.nature_of_company == "Public"
    assert strict_nature_of_company(payload["Nature of Company"]) is True


def test_tc_12_3_03_nature_of_company_subsidiary_pass():
    """
    TC-12.3-03
    Verify that a company under a parent organization is correctly classified as Subsidiary.
    """
    payload = build_base_payload()
    payload["Nature of Company"] = "Subsidiary"
    model = CompanyMetadata(**payload)
    assert model.nature_of_company == "Subsidiary"
    assert strict_nature_of_company(payload["Nature of Company"]) is True


def test_tc_12_3_04_nature_of_company_invalid_value_fail():
    """
    TC-12.3-04
    Reject invalid ownership classifications outside approved enum values.
    Input: Privately Owned
    Expected: Validation fails
    """
    payload = build_base_payload()
    payload["Nature of Company"] = "Privately Owned"
    with pytest.raises(ValidationError):
        CompanyMetadata(**payload)


def test_tc_12_3_05_nature_of_company_null_fail():
    """
    TC-12.3-05
    Reject null or missing values when ownership classification is mandatory.
    Input: NULL
    Expected: Validation fails due to NotNull constraint
    """
    payload = build_base_payload()
    payload["Nature of Company"] = None
    with pytest.raises(ValidationError):
        CompanyMetadata(**payload)


def test_tc_12_3_06_nature_of_company_case_variant_fail():
    """
    TC-12.3-06
    Reject case-variant or non-standardized values when strict enum matching is enforced.
    Input: private
    Expected: Validation fails unless case-insensitive normalization is explicitly enabled
    """
    payload = build_base_payload()
    payload["Nature of Company"] = "private"
    with pytest.raises(ValidationError):
        CompanyMetadata(**payload)

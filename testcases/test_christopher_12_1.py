import re
import pytest
from pydantic import ValidationError
from models import CompanyMetadata

CATEGORY_REGEX = r"^(Startup|MSME|SMB|Enterprise|Investor|VC|Conglomerate)$"
EMPLOYEE_SIZE_REGEX = r"^(\d+|\d+-\d+)$"
FUNDING_ROUND_REGEX = r"^\d{4}-\d{2}-\d{2}\s-\s\$[\d,]+(?:\.\d{2})?\s(?:Pre-Seed|Seed|Series A|Series B|Series C|Series D|Series E|Bridge|Debt)\sRound$"
INVESTORS_REGEX = r"^[A-Za-z0-9&./\- ]+(,\s*[A-Za-z0-9&./\- ]+)*$"


def build_base_payload():
    return {
        "Company Name": "Acme Ventures Pvt Ltd",
        "Short Name": "Acme Ventures",
        "Logo": "https://example.com/acme.png",
        "Category": "Startup",
        "Year of Incorporation": 2021,
        "Overview of the Company": "Acme Ventures is an early-stage venture-backed company building workflow automation software for growing digital businesses across multiple industries.",
        "Nature of Company": "Private",
        "Company Headquarters": "Bengaluru, India",
        "Employee Size": "18",
        "Pain Points Being Addressed": "Reducing manual operational overhead, improving automation efficiency, and simplifying digital workflows for startups and SMBs.",
        "Focus Sectors / Industries": "SaaS, Workflow Automation, Enterprise Software",
        "Services / Offerings / Products": "Automation Platform, API Integrations, Analytics",
        "Core Value Proposition": "Provides lightweight, scalable automation software for fast-growing businesses with minimal implementation overhead.",
        "Key Competitors": "Zapier, Make, Workato",
        "Recent Funding Rounds": "2024-03-15 - $3,500,000 Seed Round",
        "Key Investors / Backers": "Limited Partners, Family Offices, Institutional Funds"
    }


def employee_size_value(value: str) -> int | tuple[int, int]:
    value = str(value).strip()
    if "-" in value:
        a, b = value.split("-", 1)
        return int(a), int(b)
    return int(value)


def employee_size_consistent_with_category(category: str, employee_size: str) -> bool:
    parsed = employee_size_value(employee_size)
    if isinstance(parsed, tuple):
        low, high = parsed
        size = (low + high) / 2
    else:
        size = parsed

    if category == "Startup":
        return 1 <= size <= 100
    if category == "SMB":
        return 100 <= size <= 999
    if category in {"Investor", "VC"}:
        return size >= 1
    return True


def funding_supports_startup(category: str, funding_text: str) -> bool:
    if category != "Startup":
        return True
    if not re.fullmatch(FUNDING_ROUND_REGEX, funding_text):
        return False
    early_stage_terms = ["Pre-Seed", "Seed", "Series A"]
    return any(term in funding_text for term in early_stage_terms)


def investors_valid_for_investor_category(category: str, investors_text: str) -> bool:
    if category not in {"Investor", "VC"}:
        return True
    if not re.fullmatch(INVESTORS_REGEX, investors_text):
        return False
    keywords = ["Limited Partners", "Family Offices", "Institutional Funds", "LPs", "Fund of Funds"]
    return any(k.lower() in investors_text.lower() for k in keywords)


def test_12_1_1_category_startup_pass():
    """
    12.1.1
    Validate that an early-stage company with venture-backed funding is correctly classified under 'Startup'.
    """
    payload = build_base_payload()
    payload["Category"] = "Startup"
    model = CompanyMetadata(**payload)
    assert model.category == "Startup"
    assert re.fullmatch(CATEGORY_REGEX, payload["Category"]) is not None


def test_12_1_2_category_smb_pass():
    """
    12.1.2
    Validate that a mid-sized operating business with a moderate workforce is correctly categorized as 'SMB'.
    """
    payload = build_base_payload()
    payload["Category"] = "SMB"
    payload["Employee Size"] = "650"
    model = CompanyMetadata(**payload)
    assert model.category == "SMB"
    assert re.fullmatch(CATEGORY_REGEX, payload["Category"]) is not None


def test_12_1_3_category_investor_pass():
    """
    12.1.3
    Validate that a company functioning as a capital allocator / investment firm is categorized as 'Investor'.
    """
    payload = build_base_payload()
    payload["Category"] = "Investor"
    model = CompanyMetadata(**payload)
    assert model.category == "Investor"
    assert re.fullmatch(CATEGORY_REGEX, payload["Category"]) is not None


def test_12_1_4_category_invalid_unicorn_fail():
    """
    12.1.4
    Negative Test: Ensure category outside approved taxonomy is rejected.
    Input: Unicorn
    Expected: FAIL
    """
    payload = build_base_payload()
    payload["Category"] = "Unicorn"
    with pytest.raises(ValidationError):
        CompanyMetadata(**payload)


def test_12_1_5_employee_size_consistent_with_startup_pass():
    """
    12.1.5
    Validate consistency between employee count and a company classified as 'Startup'.
    Input: 18
    Expected: PASS
    """
    payload = build_base_payload()
    payload["Category"] = "Startup"
    payload["Employee Size"] = "18"
    model = CompanyMetadata(**payload)
    assert re.fullmatch(EMPLOYEE_SIZE_REGEX, payload["Employee Size"]) is not None
    assert employee_size_consistent_with_category(payload["Category"], payload["Employee Size"]) is True


def test_12_1_6_employee_size_consistent_with_smb_pass():
    """
    12.1.6
    Validate consistency between employee count and a company classified as 'SMB'.
    Input: 650
    Expected: PASS
    """
    payload = build_base_payload()
    payload["Category"] = "SMB"
    payload["Employee Size"] = "650"
    model = CompanyMetadata(**payload)
    assert re.fullmatch(EMPLOYEE_SIZE_REGEX, payload["Employee Size"]) is not None
    assert employee_size_consistent_with_category(payload["Category"], payload["Employee Size"]) is True


def test_12_1_7_recent_funding_rounds_support_startup_pass():
    """
    12.1.7
    Verify that a company categorized as 'Startup' includes recent early-stage funding details.
    Input: 2024-03-15 - $3,500,000 Seed Round
    Expected: PASS
    """
    payload = build_base_payload()
    payload["Category"] = "Startup"
    payload["Recent Funding Rounds"] = "2024-03-15 - $3,500,000 Seed Round"
    model = CompanyMetadata(**payload)
    assert model.recent_funding_rounds == "2024-03-15 - $3,500,000 Seed Round"
    assert funding_supports_startup(payload["Category"], payload["Recent Funding Rounds"]) is True


def test_12_1_8_key_investors_backers_for_investor_pass():
    """
    12.1.8
    Validate that companies categorized as 'Investor' or 'VC' include relevant institutional backers.
    Input: Limited Partners, Family Offices, Institutional Funds
    Expected: PASS
    """
    payload = build_base_payload()
    payload["Category"] = "Investor"
    payload["Key Investors / Backers"] = "Limited Partners, Family Offices, Institutional Funds"
    model = CompanyMetadata(**payload)
    assert model.key_investors_backers == "Limited Partners, Family Offices, Institutional Funds"
    assert investors_valid_for_investor_category(payload["Category"], payload["Key Investors / Backers"]) is True

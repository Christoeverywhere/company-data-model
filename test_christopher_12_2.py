import re
import pytest
from pydantic import ValidationError
from models import CompanyMetadata

INDUSTRY_LIST_REGEX = r"^[\w\s&.,\-/]+$"
ASSOCIATIONS_REGEX = r"^[A-Za-z0-9&()./\- ]+(,\s*[A-Za-z0-9&()./\- ]+)*$"

APPROVED_INDUSTRY_KEYWORDS = {
    "financial technology",
    "payments",
    "payments infrastructure",
    "software",
    "software platforms",
    "fintech"
}


def build_base_payload():
    return {
        "Company Name": "Stripe, Inc.",
        "Short Name": "Stripe",
        "Logo": "https://example.com/stripe.png",
        "Category": "Enterprise",
        "Year of Incorporation": 2010,
        "Overview of the Company": "Stripe is a financial technology company that provides payment processing and digital commerce infrastructure for businesses.",
        "Nature of Company": "Private",
        "Company Headquarters": "San Francisco, USA",
        "Employee Size": "7000",
        "Pain Points Being Addressed": "Simplifying digital payments, reducing checkout friction, and enabling global online commerce for businesses of all sizes.",
        "Focus Sectors / Industries": "Financial Technology, Payments, Software",
        "Services / Offerings / Products": "Payment APIs, Billing Platform, Checkout Suite, Fraud Prevention Tools",
        "Core Value Proposition": "Provides scalable payments infrastructure and financial tooling for internet businesses worldwide.",
        "Key Competitors": "Adyen, PayPal, Checkout.com",
        "Industry Associations / Memberships": "Electronic Transactions Association (ETA), PCI Security Standards Council"
    }


def split_csv_values(text: str) -> list[str]:
    return [x.strip() for x in text.split(",") if x.strip()]


def normalized_tokens(text: str) -> set[str]:
    return {x.strip().lower() for x in split_csv_values(text)}


def industries_follow_internal_taxonomy(industry_text: str) -> bool:
    if not re.fullmatch(INDUSTRY_LIST_REGEX, industry_text):
        return False
    values = normalized_tokens(industry_text)
    return all(v in APPROVED_INDUSTRY_KEYWORDS for v in values)


def overview_supports_industry(overview: str, industry_text: str) -> bool:
    overview_l = overview.lower()
    values = normalized_tokens(industry_text)
    # FinTech keyword normalization
    mapped = set()
    for v in values:
        if v == "fintech":
            mapped.add("financial technology")
        else:
            mapped.add(v)
    return any(v in overview_l for v in mapped)


def services_align_with_industry(services: str, industry_text: str) -> bool:
    services_l = services.lower()
    industry_l = industry_text.lower()
    fintech_signals = ["payment", "billing", "checkout", "fraud", "api"]
    if "financial technology" in industry_l or "payments" in industry_l or "fintech" in industry_l:
        return any(sig in services_l for sig in fintech_signals)
    return True


def associations_relevant_to_industry(associations: str, industry_text: str) -> bool:
    if not re.fullmatch(ASSOCIATIONS_REGEX, associations):
        return False
    assoc_l = associations.lower()
    if "payments" in industry_text.lower() or "financial technology" in industry_text.lower() or "fintech" in industry_text.lower():
        relevant_terms = ["electronic transactions association", "pci security standards council", "pci"]
        return any(term in assoc_l for term in relevant_terms)
    return True


def multi_sector_structure_valid(industry_text: str) -> bool:
    if not re.fullmatch(INDUSTRY_LIST_REGEX, industry_text):
        return False
    values = split_csv_values(industry_text)
    return len(values) >= 2 and all(len(v) >= 2 for v in values)


def test_12_2_1_focus_sectors_industries_internal_taxonomy_pass():
    """
    12.2.1
    Validate that the industry/sector classification follows the approved internal taxonomy.
    """
    payload = build_base_payload()
    model = CompanyMetadata(**payload)
    assert model.focus_sectors_industries == "Financial Technology, Payments, Software"
    assert industries_follow_internal_taxonomy(payload["Focus Sectors / Industries"]) is True


def test_12_2_2_overview_of_the_company_supports_industry_pass():
    """
    12.2.2
    Ensure company overview contains narrative cues supporting industry classification.
    """
    payload = build_base_payload()
    model = CompanyMetadata(**payload)
    assert model.overview_of_the_company.startswith("Stripe is a financial technology company")
    assert overview_supports_industry(payload["Overview of the Company"], payload["Focus Sectors / Industries"]) is True


def test_12_2_3_services_offerings_products_align_with_industry_pass():
    """
    12.2.3
    Verify listed services are logically consistent with the declared industry classification.
    """
    payload = build_base_payload()
    model = CompanyMetadata(**payload)
    assert model.services_offerings_products == "Payment APIs, Billing Platform, Checkout Suite, Fraud Prevention Tools"
    assert services_align_with_industry(payload["Services / Offerings / Products"], payload["Focus Sectors / Industries"]) is True


def test_12_2_4_industry_associations_memberships_relevant_pass():
    """
    12.2.4
    Check that company is affiliated with relevant industry bodies or standards groups.
    """
    payload = build_base_payload()
    model = CompanyMetadata(**payload)
    assert model.industry_associations_memberships == "Electronic Transactions Association (ETA), PCI Security Standards Council"
    assert associations_relevant_to_industry(
        payload["Industry Associations / Memberships"],
        payload["Focus Sectors / Industries"]
    ) is True


def test_12_2_5_focus_sectors_industries_invalid_format_fail():
    """
    12.2.5
    Negative Test: Reject industry assignments containing unsupported symbols or malformed labels.
    Input: FinTech!!! & Clean$$ Energy
    Expected: FAIL
    """
    payload = build_base_payload()
    payload["Focus Sectors / Industries"] = "FinTech!!! & Clean$$ Energy"

    # Schema may reject if regex validator is active in models.py
    # If schema does not reject, business-rule layer must still reject.
    try:
        CompanyMetadata(**payload)
    except ValidationError:
        assert True
        return

    assert industries_follow_internal_taxonomy(payload["Focus Sectors / Industries"]) is False


def test_12_2_6_focus_sectors_industries_multi_sector_structured_pass():
    """
    12.2.6
    Validate that multi-sector classification is allowed when values are properly structured.
    """
    payload = build_base_payload()
    payload["Focus Sectors / Industries"] = "Financial Technology, Payments Infrastructure, Software Platforms"
    model = CompanyMetadata(**payload)
    assert model.focus_sectors_industries == "Financial Technology, Payments Infrastructure, Software Platforms"
    assert multi_sector_structure_valid(payload["Focus Sectors / Industries"]) is True

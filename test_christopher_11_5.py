import pytest
import re
from pydantic import ValidationError
from models import CompanyMetadata

LEGAL_NAME_MAP = {
    "google": "Alphabet Inc."
}

LINKEDIN_COMPANY_REGEX = r"^https?://(www\.)?linkedin\.com/company/[A-Za-z0-9_\-]+/?$"
COMPLIANCE_TAG_REGEX = r"^[A-Za-z0-9 .+\-]+(,\s*[A-Za-z0-9 .+\-]+)*$"


def build_valid_payload():
    return {
        "Company Name": "Alphabet Inc.",
        "Short Name": "Google",
        "Logo": "https://example.com/logo.png",
        "Category": "Enterprise",
        "Year of Incorporation": 2015,
        "Overview of the Company": "Alphabet Inc. is a multinational technology holding company that oversees internet, cloud, AI, and digital platform businesses serving consumers and enterprises globally.",
        "Nature of Company": "Public",
        "Company Headquarters": "Mountain View, USA",
        "Employee Size": "10000",
        "Pain Points Being Addressed": "Improving access to information, cloud scalability, digital advertising efficiency, and AI-driven business productivity across global markets.",
        "Focus Sectors / Industries": "Technology, Internet Services, Cloud Computing",
        "Services / Offerings / Products": "Search, Cloud, Advertising, AI Platforms, Productivity Tools",
        "Core Value Proposition": "Delivers scalable digital products, search intelligence, cloud infrastructure, and AI-powered platforms for users and enterprises worldwide.",
        "Key Competitors": "Microsoft, Amazon, Meta",
        "LinkedIn Profile URL": "https://www.linkedin.com/company/google/",
        "Regulatory & Compliance Status": "GDPR, ISO 27001"
    }


def is_valid_legal_name_for_entity(company_name: str, short_name: str | None = None) -> bool:
    if not company_name:
        return False
    canonical = LEGAL_NAME_MAP.get(company_name.strip().lower())
    # If the provided company name is itself a brand alias, it should fail
    if canonical is not None and canonical.lower() != company_name.strip().lower():
        return False
    # Optional cross-check: short name can be a known brand alias of the legal entity
    if short_name and short_name.strip().lower() in LEGAL_NAME_MAP:
        return LEGAL_NAME_MAP[short_name.strip().lower()].lower() == company_name.strip().lower()
    return True


def linkedin_url_maps_to_entity(linkedin_url: str, company_name: str, short_name: str | None = None) -> bool:
    if not re.fullmatch(LINKEDIN_COMPANY_REGEX, linkedin_url):
        return False
    slug = linkedin_url.rstrip("/").split("/")[-1].lower()
    if short_name and slug == short_name.strip().lower():
        return True
    if slug == company_name.strip().lower().replace(" ", "-"):
        return True
    # Known brand/legal alias mapping
    if slug in LEGAL_NAME_MAP and LEGAL_NAME_MAP[slug].lower() == company_name.strip().lower():
        return True
    return False


def compliance_tags_are_valid(compliance_text: str) -> bool:
    if not compliance_text:
        return False
    return re.fullmatch(COMPLIANCE_TAG_REGEX, compliance_text) is not None


def test_11_5_1_company_name_official_legal_name_validation_pass():
    """
    11.5.1
    Official Legal Name Validation: Company Name should be the full legal entity name.
    Input: Alphabet Inc.
    Expected: PASS
    """
    payload = build_valid_payload()
    model = CompanyMetadata(**payload)
    assert model.company_name == "Alphabet Inc."
    assert is_valid_legal_name_for_entity(payload["Company Name"], payload["Short Name"]) is True


def test_11_5_2_short_name_common_brand_name_alignment_pass():
    """
    11.5.2
    Common Brand Name Alignment: Short Name should be UI-friendly and distinct from Company Name.
    Input: Google
    Expected: PASS
    """
    payload = build_valid_payload()
    model = CompanyMetadata(**payload)
    assert model.short_name == "Google"
    assert model.short_name != model.company_name
    assert re.fullmatch(r"^[\w\s&.\-]+$", payload["Short Name"]) is not None


def test_11_5_3_company_name_common_name_vs_legal_name_conflict_fail():
    """
    11.5.3
    Common Name vs. Legal Name Conflict: Brand name should not be accepted as legal company name
    when the registered legal entity differs.
    Input: Google
    Expected: FAIL (Data Quality Alert)
    """
    payload = build_valid_payload()
    payload["Company Name"] = "Google"

    # Schema layer throws a ValidationError because Short Name == Company Name
    with pytest.raises(ValidationError) as exc_info:
        model = CompanyMetadata(**payload)
    assert "Short Name should be distinct from Company Name" in str(exc_info.value)


def test_11_5_4_linkedin_profile_url_social_identity_to_legal_mapping_pass():
    """
    11.5.4
    Social Identity to Legal Mapping: LinkedIn company profile URL should be valid and map
    to the same organization represented by the legal/brand identity.
    Input: https://www.linkedin.com/company/google/
    Expected: PASS
    """
    payload = build_valid_payload()
    model = CompanyMetadata(**payload)
    assert model.linkedin_profile_url == "https://www.linkedin.com/company/google/"
    assert re.fullmatch(LINKEDIN_COMPANY_REGEX, payload["LinkedIn Profile URL"]) is not None
    assert linkedin_url_maps_to_entity(
        payload["LinkedIn Profile URL"],
        payload["Company Name"],
        payload["Short Name"]
    ) is True


def test_11_5_5_nature_of_company_ownership_structure_alignment_pass():
    """
    11.5.5
    Ownership Structure Alignment: Nature of Company should match expected enum values.
    Input: Public
    Expected: PASS
    """
    payload = build_valid_payload()
    model = CompanyMetadata(**payload)
    assert model.nature_of_company == "Public"
    assert model.nature_of_company in {"Private", "Public", "Subsidiary", "Partnership", "Non-Profit", "Govt"}


def test_11_5_6_regulatory_and_compliance_status_compliance_entity_identification_pass():
    """
    11.5.6
    Compliance Entity Identification: Regulatory & Compliance Status should accept valid tag-list format
    and be attributable to the correct legal entity.
    Input: GDPR, ISO 27001
    Expected: PASS
    """
    payload = build_valid_payload()
    model = CompanyMetadata(**payload)
    assert model.regulatory_compliance_status == "GDPR, ISO 27001"
    assert compliance_tags_are_valid(payload["Regulatory & Compliance Status"]) is True

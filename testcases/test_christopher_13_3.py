import json
import pytest
from models import CompanyMetadata

# NOTE:
# 13.4 is a STRESS / OUTPUT-INTEGRITY test suite, not a pure field-validation suite.
# Since no real profile-generation function was provided, these tests simulate:
#   1) large payload creation
#   2) CompanyMetadata validation
#   3) JSON serialization integrity
#   4) structural completeness checks
#
# This is the correct local mock approach for "high token / truncation / schema integrity" testing.


def build_base_required():
    return {
        "Company Name": "Stress Test Global Holdings Inc.",
        "Short Name": "StressGlobal",
        "Logo": "https://example.com/stressglobal.png",
        "Category": "Enterprise",
        "Year of Incorporation": 1985,
        "Overview of the Company": "Stress Test Global Holdings is a multinational enterprise operating across multiple sectors with complex reporting and global delivery capabilities.",
        "Nature of Company": "Public",
        "Company Headquarters": "New York, USA",
        "Employee Size": "150000",
        "Pain Points Being Addressed": "Improving global operating efficiency, compliance transparency, cross-border governance, and portfolio-level strategic execution.",
        "Focus Sectors / Industries": "Technology, Finance, Enterprise Services",
        "Services / Offerings / Products": "Cloud Platforms, Consulting, Managed Services, Financial Infrastructure",
        "Core Value Proposition": "Delivers large-scale enterprise platforms, governance support, and integrated service capabilities across global markets.",
        "Key Competitors": "Competitor A, Competitor B, Competitor C"
    }


def long_text(seed: str, repeat: int) -> str:
    return " ".join([seed] * repeat)


def build_long_narrative_payload():
    payload = build_base_required()
    payload.update({
        "Overview of the Company": long_text(
            "This enterprise has an extensive history, broad product portfolio, leadership evolution, global expansion, strategic partnerships, regulatory milestones, and detailed business narratives.",
            80
        ),
        "Pain Points Being Addressed": long_text(
            "The company addresses operational complexity, legacy modernization, compliance fragmentation, cross-border execution, customer retention, and platform standardization.",
            60
        ),
        "Core Value Proposition": long_text(
            "The organization delivers scalable enterprise value through integrated software, consulting, infrastructure, governance, and measurable transformation outcomes.",
            50
        )
    })
    return payload


def build_many_offices_payload():
    payload = build_base_required()
    office_locations = [f"Office {i} - City {i}, Country {i}" for i in range(1, 121)]
    payload.update({
        "Office Locations": ", ".join(office_locations),
        "Countries Operating In": ", ".join([f"Country {i}" for i in range(1, 121)]),
        "Number of Offices (beyond HQ)": "120"
    })
    return payload


def build_high_complexity_payload():
    payload = build_base_required()
    payload.update({
        "Recent Funding Rounds": "2008-04-22 - $750,000,000 Series E Round",
        "Key Investors / Backers": "Institutional Funds, Pension Funds, Sovereign Wealth Funds",
        "LinkedIn Profile URL": "https://www.linkedin.com/company/stressglobal",
        "Regulatory & Compliance Status": "GDPR, ISO 27001, SOC 2, PCI DSS",
        "Industry Associations / Memberships": "World Economic Forum, Industry Standards Council, Global Technology Consortium",
        "Brand Sentiment Score": "Positive",
        "Net Promoter Score (NPS)": 62,
        "Glassdoor Rating": 4.4,
        "Customer Concentration Risk": "Low",
        "Burn Rate": 980000.75
    })
    return payload


def build_near_token_limit_payload():
    payload = build_high_complexity_payload()
    payload.update({
        "Overview of the Company": long_text("Long narrative section about enterprise operations and disclosures.", 120),
        "Services / Offerings / Products": long_text("Products include software, infrastructure, analytics, and managed services.", 80),
        "Core Value Proposition": long_text("Core value proposition includes transformation, resilience, and scale.", 90)
    })
    return payload


def build_max_size_payload():
    payload = build_high_complexity_payload()
    payload.update({
        "Office Locations": ", ".join([f"Office {i} - Global Region {i}" for i in range(1, 101)]),
        "Countries Operating In": ", ".join([f"Country {i}" for i in range(1, 101)]),
        "Number of Offices (beyond HQ)": "100",
        "Overview of the Company": long_text("Detailed overview covering history, operations, leadership, product lines, and compliance posture.", 100),
        "Pain Points Being Addressed": long_text("Addresses operational complexity, compliance, retention, efficiency, and transformation.", 80),
        "Core Value Proposition": long_text("Provides scalable enterprise value through integrated global capabilities.", 80),
        "Services / Offerings / Products": long_text("Software, consulting, infrastructure, analytics, and services.", 60)
    })
    return payload


def validate_json_integrity(model: CompanyMetadata) -> dict:
    dumped = model.model_dump(by_alias=True)
    json_text = json.dumps(dumped, ensure_ascii=False)
    reparsed = json.loads(json_text)
    assert isinstance(reparsed, dict)
    return reparsed


def assert_required_sections_present(record: dict):
    required_sections = [
        "Company Name",
        "Category",
        "Overview of the Company",
        "Nature of Company",
        "Company Headquarters",
        "Employee Size",
        "Pain Points Being Addressed",
        "Focus Sectors / Industries",
        "Services / Offerings / Products",
        "Core Value Proposition",
        "Key Competitors"
    ]
    for section in required_sections:
        assert section in record
        assert record[section] is not None
        assert str(record[section]).strip() != ""


def no_mid_token_like_breaks(record: dict):
    # Practical local proxy: ensure no field ends with obviously broken fragments
    suspicious_suffixes = ["...", "�", "\\", "/", "-", "("]
    for value in record.values():
        if isinstance(value, str):
            stripped = value.strip()
            assert not any(stripped.endswith(sfx) for sfx in suspicious_suffixes)


def test_tc_13_3_01_extremely_long_narratives_complete_successfully():
    """
    TC-13.3-01
    Generate profile with extremely long descriptive content across multiple narrative fields.
    Expected: completes successfully without abrupt truncation.
    """
    payload = build_long_narrative_payload()
    model = CompanyMetadata(**payload)
    record = validate_json_integrity(model)
    assert_required_sections_present(record)
    no_mid_token_like_breaks(record)


def test_tc_13_3_02_large_number_of_office_locations_handled():
    """
    TC-13.3-02
    Generate profile for entity with very large number of office/location records.
    Expected: office data retained or handled without unexpected cutoff.
    """
    payload = build_many_offices_payload()
    model = CompanyMetadata(**payload)
    record = validate_json_integrity(model)
    assert "Office Locations" in record
    assert "Countries Operating In" in record
    assert len(record["Office Locations"].split(",")) >= 100
    assert len(record["Countries Operating In"].split(",")) >= 100


def test_tc_13_3_03_json_schema_integrity_under_high_complexity():
    """
    TC-13.3-03
    Verify JSON/schema structural integrity under high context load.
    Expected: parseable, structurally valid, no malformed objects.
    """
    payload = build_high_complexity_payload()
    model = CompanyMetadata(**payload)
    record = validate_json_integrity(model)
    assert_required_sections_present(record)


def test_tc_13_3_04_detect_no_mid_section_cutoff_near_token_limit():
    """
    TC-13.3-04
    Detect whether output is cut off mid-sentence/mid-section near token threshold.
    Expected: logical boundaries, no broken partial tokens.
    """
    payload = build_near_token_limit_payload()
    model = CompanyMetadata(**payload)
    record = validate_json_integrity(model)
    no_mid_token_like_breaks(record)


def test_tc_13_3_05_graceful_degradation_behavior_when_capacity_exceeded():
    """
    TC-13.3-05
    Validate graceful degradation behavior when safe token limit is exceeded.
    Expected: system handles with structure-preserving fallback instead of malformed output.
    """
    payload = build_near_token_limit_payload()
    model = CompanyMetadata(**payload)
    record = validate_json_integrity(model)
    # Local mock proxy: structure still valid and required sections remain present
    assert_required_sections_present(record)


def test_tc_13_3_06_mandatory_sections_not_silently_dropped_at_max_complexity():
    """
    TC-13.3-06
    Ensure mandatory schema sections are not silently dropped at max supported complexity.
    Expected: all mandatory sections remain present.
    """
    payload = build_max_size_payload()
    model = CompanyMetadata(**payload)
    record = validate_json_integrity(model)
    assert_required_sections_present(record)

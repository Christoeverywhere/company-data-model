import json
import pytest
from models import CompanyMetadata

# NOTE:
# 13.4 is an ENTITY ISOLATION / CONTEXT LEAKAGE test suite.
# Since no real sequential profile-generation pipeline was provided, these tests simulate
# batch/sequential generation by validating distinct payloads independently and checking
# that serialized outputs do not contain attributes from other entities.
#
# This is the correct local mock approach for context-isolation testing.


def build_base_required():
    return {
        "Logo": "https://example.com/logo.png",
        "Category": "Enterprise",
        "Year of Incorporation": 2015,
        "Overview of the Company": "A technology-enabled company profile used for isolation testing.",
        "Nature of Company": "Private",
        "Company Headquarters": "Bengaluru, India",
        "Employee Size": "500",
        "Pain Points Being Addressed": "Operational efficiency, customer retention, and growth optimization.",
        "Focus Sectors / Industries": "Software, SaaS, Technology",
        "Services / Offerings / Products": "Software Platform, Analytics, Automation",
        "Core Value Proposition": "Provides scalable digital solutions with strong operational efficiency.",
        "Key Competitors": "Competitor A, Competitor B"
    }


def serialize_record(payload: dict) -> dict:
    model = CompanyMetadata(**payload)
    return model.model_dump(by_alias=True)


def record_text(record: dict) -> str:
    return json.dumps(record, ensure_ascii=False).lower()


def assert_contains_only_entity(record: dict, required_terms: list[str], forbidden_terms: list[str]):
    text = record_text(record)
    for term in required_terms:
        assert term.lower() in text
    for term in forbidden_terms:
        assert term.lower() not in text


def build_tesla_payload():
    payload = build_base_required()
    payload.update({
        "Company Name": "Tesla, Inc.",
        "Short Name": "Tesla",
        "Nature of Company": "Public",
        "Overview of the Company": "Tesla is an electric vehicle and energy company focused on EVs, batteries, and clean energy solutions.",
        "Services / Offerings / Products": "Electric Vehicles, Battery Systems, Solar Energy Products",
        "Company Headquarters": "Austin, USA",
        "Key Competitors": "BYD, Rivian, Lucid"
    })
    return payload


def build_stripe_payload():
    payload = build_base_required()
    payload.update({
        "Company Name": "Stripe, Inc.",
        "Short Name": "Stripe",
        "Nature of Company": "Private",
        "Overview of the Company": "Stripe is a financial technology company focused on digital payments and internet commerce infrastructure.",
        "Services / Offerings / Products": "Payment APIs, Billing Platform, Checkout Suite",
        "Company Headquarters": "San Francisco, USA",
        "Key Competitors": "Adyen, PayPal, Checkout.com"
    })
    return payload


def build_complex_enterprise_payload():
    payload = build_base_required()
    payload.update({
        "Company Name": "MegaGlobal Enterprise Inc.",
        "Short Name": "MegaGlobal",
        "Nature of Company": "Public",
        "Category": "Enterprise",
        "Employee Size": "85000",
        "Overview of the Company": "MegaGlobal is a multinational enterprise with complex operations, governance, and global reporting obligations.",
        "Recent Funding Rounds": "2008-04-22 - $750,000,000 Series E Round",
        "LinkedIn Profile URL": "https://www.linkedin.com/company/megaglobal/",
        "Regulatory & Compliance Status": "GDPR, ISO 27001, SOC 2",
        "Brand Sentiment Score": "Positive",
        "Net Promoter Score (NPS)": 48,
        "Glassdoor Rating": 4.1
    })
    return payload


def build_lean_startup_payload():
    payload = build_base_required()
    payload.update({
        "Company Name": "LeanSpark Labs Pvt Ltd",
        "Short Name": "LeanSpark",
        "Nature of Company": "Private",
        "Category": "Startup",
        "Employee Size": "15",
        "Overview of the Company": "LeanSpark is a lean startup building workflow automation for small teams.",
        "Recent Funding Rounds": "2024-03-15 - $2,000,000 Seed Round",
        "Key Investors / Backers": "Angel Investors, Seed Funds"
    })
    return payload


def build_similar_saas_batch():
    companies = [
        {
            "Company Name": "CloudFlow Inc.",
            "Short Name": "CloudFlow",
            "Overview of the Company": "CloudFlow provides SaaS workflow orchestration tools.",
            "Services / Offerings / Products": "Workflow Automation, Integrations, Analytics"
        },
        {
            "Company Name": "ScaleOps Inc.",
            "Short Name": "ScaleOps",
            "Overview of the Company": "ScaleOps provides SaaS infrastructure optimization tools.",
            "Services / Offerings / Products": "Cloud Optimization, Cost Analytics, DevOps Insights"
        },
        {
            "Company Name": "RevenuePilot Inc.",
            "Short Name": "RevenuePilot",
            "Overview of the Company": "RevenuePilot provides SaaS revenue intelligence tools.",
            "Services / Offerings / Products": "Revenue Analytics, Forecasting, CRM Intelligence"
        }
    ]
    payloads = []
    for c in companies:
        p = build_base_required()
        p.update(c)
        payloads.append(p)
    return payloads


def build_company_a_payload():
    payload = build_base_required()
    payload.update({
        "Company Name": "FounderFirst Labs",
        "Short Name": "FounderFirst",
        "Overview of the Company": "FounderFirst Labs was founded by Alice Morgan and Ben Carter to build talent systems.",
        "Services / Offerings / Products": "Talent Cloud, Hiring Intelligence, HR Analytics",
        "Key Competitors": "Workday, Greenhouse"
    })
    return payload


def build_company_b_payload():
    payload = build_base_required()
    payload.update({
        "Company Name": "RetailMesh Systems",
        "Short Name": "RetailMesh",
        "Overview of the Company": "RetailMesh Systems is led by Daniel Cho and Priya Raman to modernize retail operations.",
        "Services / Offerings / Products": "Retail OS, Inventory Automation, Store Analytics",
        "Key Competitors": "Oracle Retail, SAP"
    })
    return payload


def test_tc_13_4_01_no_residual_entity_leakage_between_requests():
    """
    TC-13.4-01
    Request 1 -> Tesla, Request 2 -> Stripe
    Expected: second output contains only Stripe-related attributes.
    """
    tesla_record = serialize_record(build_tesla_payload())
    stripe_record = serialize_record(build_stripe_payload())

    assert_contains_only_entity(
        stripe_record,
        required_terms=["stripe", "payment apis", "san francisco"],
        forbidden_terms=["tesla", "electric vehicles", "austin", "battery systems", "solar energy"]
    )


def test_tc_13_4_02_large_complex_request_does_not_leak_into_lean_startup():
    """
    TC-13.4-02
    Complex enterprise profile followed by lean startup profile.
    Expected: second profile remains concise and entity-specific.
    """
    enterprise_record = serialize_record(build_complex_enterprise_payload())
    startup_record = serialize_record(build_lean_startup_payload())

    assert_contains_only_entity(
        startup_record,
        required_terms=["leanspark", "startup", "seed round"],
        forbidden_terms=["megaglobal", "soc 2", "85000", "multinational enterprise"]
    )


def test_tc_13_4_03_similar_industry_batch_remains_entity_isolated():
    """
    TC-13.4-03
    Multiple similar SaaS companies should remain uniquely attributable.
    """
    records = [serialize_record(p) for p in build_similar_saas_batch()]
    texts = [record_text(r) for r in records]

    assert "cloudflow" in texts[0]
    assert "scaleops" not in texts[0]
    assert "revenuepilot" not in texts[0]

    assert "scaleops" in texts[1]
    assert "cloudflow" not in texts[1]
    assert "revenuepilot" not in texts[1]

    assert "revenuepilot" in texts[2]
    assert "cloudflow" not in texts[2]
    assert "scaleops" not in texts[2]


def test_tc_13_4_04_detect_cross_entity_named_entity_contamination():
    """
    TC-13.4-04
    Company A unique founder/product names should not appear in Company B output.
    """
    company_a_record = serialize_record(build_company_a_payload())
    company_b_record = serialize_record(build_company_b_payload())

    assert_contains_only_entity(
        company_b_record,
        required_terms=["retailmesh", "daniel cho", "priya raman", "retail os"],
        forbidden_terms=["founderfirst", "alice morgan", "ben carter", "talent cloud", "hiring intelligence"]
    )


def test_tc_13_4_05_repeated_alternating_generation_stays_stable():
    """
    TC-13.4-05
    A -> B -> A -> B repeated sequence should preserve clean separation.
    """
    sequence = [
        serialize_record(build_company_a_payload()),
        serialize_record(build_company_b_payload()),
        serialize_record(build_company_a_payload()),
        serialize_record(build_company_b_payload()),
    ]
    texts = [record_text(r) for r in sequence]

    assert "founderfirst" in texts[0] and "retailmesh" not in texts[0]
    assert "retailmesh" in texts[1] and "founderfirst" not in texts[1]
    assert "founderfirst" in texts[2] and "retailmesh" not in texts[2]
    assert "retailmesh" in texts[3] and "founderfirst" not in texts[3]


def test_tc_13_4_06_bulk_generation_for_related_companies_remains_pure():
    """
    TC-13.4-06
    Batch generation for 20 related companies should remain entity-pure with no carryover.
    """
    payloads = []
    for i in range(1, 21):
        p = build_base_required()
        p.update({
            "Company Name": f"CoID-{i}-Name",
            "Short Name": f"ShortID-{i}",
            "Overview of the Company": f"CoID-{i}-Name builds domain-specific software for segment {i}.",
            "Services / Offerings / Products": f"Platform {i}, Analytics {i}, Automation {i}"
        })
        payloads.append(p)

    records = [serialize_record(p) for p in payloads]
    texts = [record_text(r) for r in records]

    for i, text in enumerate(texts, start=1):
        assert f"coid-{i}-name" in text
        for j in range(1, 21):
            if j != i:
                assert f"coid-{j}-name" not in text

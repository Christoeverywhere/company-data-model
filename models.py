from __future__ import annotations
from typing import Optional, Any
from pydantic import BaseModel, Field, field_validator, model_validator, ConfigDict
from datetime import datetime
import re

CURRENT_YEAR = datetime.now().year

CATEGORY_ENUM = {"Startup", "MSME", "SMB", "Enterprise", "Investor", "VC", "Conglomerate"}
NATURE_ENUM = {"Private", "Public", "Subsidiary", "Partnership", "Non-Profit", "Govt"}
SENTIMENT_ENUM = {"Positive", "Neutral", "Negative"}
RISK_ENUM = {"Low", "Medium", "High"}

LINKEDIN_REGEX = re.compile(r"^https?://(www\.)?linkedin\.com/company/[A-Za-z0-9\-_]+/?$")
COMPANY_NAME_REGEX = re.compile(r"^[\w\s&.,\-()'’]{2,255}$", re.UNICODE)
SHORT_NAME_REGEX = re.compile(r"^[\w\s&.\-]{2,100}$", re.UNICODE)
EMPLOYEE_SIZE_REGEX = re.compile(r"^(\d+|\d+-\d+)$")
FUNDING_ROUND_REGEX = re.compile(
    r"^\d{4}-\d{2}-\d{2}\s-\s\$[\d,]+(?:\.\d{2})?\s(?:Pre-Seed|Seed|Series A|Series B|Series C|Series D|Series E|Bridge|Debt)\sRound$"
)
COMPLIANCE_REGEX = re.compile(r"^[A-Za-z0-9&()./\- ]+(,\s*[A-Za-z0-9&()./\- ]+)*$")
GENERIC_LIST_REGEX = re.compile(r"^[\w\s&.,/!?;:()\-]{2,50000}$", re.UNICODE)


class CompanyMetadata(BaseModel):
    model_config = ConfigDict(populate_by_name=True, extra="allow")

    company_name: str = Field(alias="Company Name", min_length=2, max_length=255)
    short_name: Optional[str] = Field(default=None, alias="Short Name", min_length=2, max_length=100)
    logo: str = Field(alias="Logo", min_length=10, max_length=2048)
    category: str = Field(alias="Category", min_length=2, max_length=50)
    year_of_incorporation: int = Field(alias="Year of Incorporation")
    overview_of_the_company: str = Field(alias="Overview of the Company", min_length=20, max_length=20000)
    nature_of_company: str = Field(alias="Nature of Company", min_length=3, max_length=50)
    company_headquarters: str = Field(alias="Company Headquarters", min_length=3, max_length=255)
    countries_operating_in: Optional[str] = Field(default=None, alias="Countries Operating In", min_length=3, max_length=20000)
    number_of_offices_beyond_hq: Optional[int] = Field(default=None, alias="Number of Offices (beyond HQ)")
    office_locations: Optional[str] = Field(default=None, alias="Office Locations", min_length=3, max_length=50000)
    employee_size: str = Field(alias="Employee Size", min_length=1, max_length=20)
    hiring_velocity: Optional[str] = Field(default=None, alias="Hiring Velocity")
    employee_turnover: Optional[str] = Field(default=None, alias="Employee Turnover")
    average_retention_tenure: Optional[str] = Field(default=None, alias="Average Retention Tenure")
    pain_points_being_addressed: str = Field(alias="Pain Points Being Addressed", min_length=10, max_length=20000)
    focus_sectors_industries: str = Field(alias="Focus Sectors / Industries", min_length=3, max_length=5000)
    services_offerings_products: str = Field(alias="Services / Offerings / Products", min_length=3, max_length=20000)
    top_customers_by_client_segments: Optional[str] = Field(default=None, alias="Top Customers by Client Segments")
    core_value_proposition: str = Field(alias="Core Value Proposition", min_length=10, max_length=20000)
    vision: Optional[str] = Field(default=None, alias="Vision")
    mission: Optional[str] = Field(default=None, alias="Mission")
    values: Optional[str] = Field(default=None, alias="Values")
    key_competitors: str = Field(alias="Key Competitors", min_length=3, max_length=5000)

    recent_funding_rounds: Optional[str] = Field(default=None, alias="Recent Funding Rounds")
    key_investors_backers: Optional[str] = Field(default=None, alias="Key Investors / Backers")
    linkedin_profile_url: Optional[str] = Field(default=None, alias="LinkedIn Profile URL")
    regulatory_compliance_status: Optional[str] = Field(default=None, alias="Regulatory & Compliance Status")
    industry_associations_memberships: Optional[str] = Field(default=None, alias="Industry Associations / Memberships")
    brand_sentiment_score: Optional[str] = Field(default=None, alias="Brand Sentiment Score")
    net_promoter_score_nps: Optional[int] = Field(default=None, alias="Net Promoter Score (NPS)")
    glassdoor_rating: Optional[float] = Field(default=None, alias="Glassdoor Rating")
    customer_concentration_risk: Optional[str] = Field(default=None, alias="Customer Concentration Risk")
    burn_rate: Optional[float] = Field(default=None, alias="Burn Rate")
    geopolitical_risk_level: Optional[str] = Field(default=None, alias="Geopolitical Risk Level")

    @field_validator("company_name")
    @classmethod
    def validate_company_name(cls, v: str) -> str:
        if not COMPANY_NAME_REGEX.fullmatch(v):
            raise ValueError("Invalid Company Name format")
        return v

    @field_validator("short_name")
    @classmethod
    def validate_short_name(cls, v: Optional[str]) -> Optional[str]:
        if v is None:
            return v
        if not SHORT_NAME_REGEX.fullmatch(v):
            raise ValueError("Invalid Short Name format")
        return v

    @field_validator("category")
    @classmethod
    def validate_category(cls, v: str) -> str:
        if v not in CATEGORY_ENUM:
            raise ValueError(f"Category must be one of {sorted(CATEGORY_ENUM)}")
        return v

    @field_validator("nature_of_company")
    @classmethod
    def validate_nature_of_company(cls, v: str) -> str:
        if v not in NATURE_ENUM:
            raise ValueError(f"Nature of Company must be one of {sorted(NATURE_ENUM)}")
        return v

    @field_validator("year_of_incorporation")
    @classmethod
    def validate_year_of_incorporation(cls, v: int) -> int:
        if v < 1800 or v > CURRENT_YEAR:
            raise ValueError("Year of Incorporation must be between 1800 and current year")
        return v

    @field_validator("employee_size")
    @classmethod
    def validate_employee_size(cls, v: str) -> str:
        if not EMPLOYEE_SIZE_REGEX.fullmatch(str(v).strip()):
            raise ValueError("Employee Size must be an integer or range like 10-50")
        return str(v).strip()

    @field_validator("focus_sectors_industries", "services_offerings_products", "key_competitors")
    @classmethod
    def validate_generic_lists(cls, v: str) -> str:
        if not GENERIC_LIST_REGEX.fullmatch(v):
            raise ValueError("Invalid list/text format")
        return v

    @field_validator("recent_funding_rounds")
    @classmethod
    def validate_recent_funding_rounds(cls, v: Optional[str]) -> Optional[str]:
        if v is None:
            return v
        if not FUNDING_ROUND_REGEX.fullmatch(v):
            raise ValueError("Invalid Recent Funding Rounds format")
        return v

    @field_validator("key_investors_backers", "regulatory_compliance_status", "industry_associations_memberships")
    @classmethod
    def validate_comma_lists(cls, v: Optional[str]) -> Optional[str]:
        if v is None:
            return v
        if not COMPLIANCE_REGEX.fullmatch(v):
            raise ValueError("Invalid comma-separated list format")
        return v

    @field_validator("linkedin_profile_url")
    @classmethod
    def validate_linkedin_profile_url(cls, v: Optional[str]) -> Optional[str]:
        if v is None:
            return v
        if not LINKEDIN_REGEX.fullmatch(v):
            raise ValueError("Invalid LinkedIn Profile URL")
        return v

    @field_validator("brand_sentiment_score")
    @classmethod
    def validate_brand_sentiment_score(cls, v: Optional[str]) -> Optional[str]:
        if v is None:
            return v
        if v not in SENTIMENT_ENUM:
            raise ValueError(f"Brand Sentiment Score must be one of {sorted(SENTIMENT_ENUM)}")
        return v

    @field_validator("net_promoter_score_nps")
    @classmethod
    def validate_nps(cls, v: Optional[int]) -> Optional[int]:
        if v is None:
            return v
        if v < -100 or v > 100:
            raise ValueError("Net Promoter Score (NPS) must be between -100 and 100")
        return v

    @field_validator("glassdoor_rating")
    @classmethod
    def validate_glassdoor_rating(cls, v: Optional[float]) -> Optional[float]:
        if v is None:
            return v
        if v < 1.0 or v > 5.0:
            raise ValueError("Glassdoor Rating must be between 1.0 and 5.0")
        return v

    @field_validator("customer_concentration_risk")
    @classmethod
    def validate_customer_concentration_risk(cls, v: Optional[str]) -> Optional[str]:
        if v is None:
            return v
        if v not in RISK_ENUM:
            raise ValueError(f"Customer Concentration Risk must be one of {sorted(RISK_ENUM)}")
        return v

    @field_validator("burn_rate")
    @classmethod
    def validate_burn_rate(cls, v: Optional[float]) -> Optional[float]:
        return v

    @model_validator(mode="after")
    def cross_field_validations(self):
        if self.short_name is not None and self.company_name is not None:
            if self.short_name.strip().lower() == self.company_name.strip().lower():
                raise ValueError("Short Name should be distinct from Company Name when both are present")

        if self.number_of_offices_beyond_hq is not None and self.office_locations is None:
            raise ValueError("Number of Offices (beyond HQ) must be null when Office Locations is null")

        if self.office_locations is not None and self.countries_operating_in is None:
            raise ValueError("Office Locations should be null when Countries Operating In is null")

        return self

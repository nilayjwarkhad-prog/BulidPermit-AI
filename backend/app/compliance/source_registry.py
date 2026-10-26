from typing import List, Dict, Any

# Explicitly labeled sample rulesets for testing and development.
# These are clearly marked as NON-REGULATORY EXAMPLE RULESETS.

SUPPORTED_JURISDICTIONS: List[Dict[str, Any]] = [
    {
        "id": "US-CA-GENERIC",
        "name": "California State Model Guidelines (Sample)",
        "country": "United States",
        "state_region": "California",
        "city": "All Municipalities",
        "authority_name": "California Building Standards Commission (Sample)",
        "is_supported": True,
        "is_sample_ruleset": True,
        "notes": "NON-REGULATORY EXAMPLE RULESET for development and testing. Covers standard CRC residential additions and ADUs."
    },
    {
        "id": "US-CA-LOSANGELES",
        "name": "City of Los Angeles (Sample Guidelines)",
        "country": "United States",
        "state_region": "California",
        "city": "Los Angeles",
        "authority_name": "LADBS (Los Angeles Dept of Building & Safety)",
        "is_supported": True,
        "is_sample_ruleset": True,
        "notes": "NON-REGULATORY EXAMPLE RULESET based on public LADBS residential checklist."
    },
    {
        "id": "US-TX-AUSTIN",
        "name": "City of Austin (Sample Guidelines)",
        "country": "United States",
        "state_region": "Texas",
        "city": "Austin",
        "authority_name": "Austin Development Services Dept",
        "is_supported": True,
        "is_sample_ruleset": True,
        "notes": "NON-REGULATORY EXAMPLE RULESET for single family residential additions."
    },
    {
        "id": "EU-DE-BERLIN",
        "name": "Berlin Bauaufsicht (Sample Guidelines)",
        "country": "Germany",
        "state_region": "Berlin",
        "city": "Berlin",
        "authority_name": "Bauaufsichtsamt Berlin",
        "is_supported": True,
        "is_sample_ruleset": True,
        "notes": "NON-REGULATORY EXAMPLE RULESET for German Bauantrag pre-submission checks."
    },
    {
        "id": "GENERAL-CHECK",
        "name": "General Pre-Check (Unsupported Jurisdiction Fallback)",
        "country": "Universal",
        "state_region": "General",
        "city": "General",
        "authority_name": "General Permitting Framework",
        "is_supported": False,
        "is_sample_ruleset": True,
        "notes": "Standard document completeness checks. Local zoning rules are not evaluated."
    }
]

SAMPLE_RULES: List[Dict[str, Any]] = [
    {
        "rule_code": "CRC-R301-SETBACK-FRONT",
        "jurisdiction_id": "US-CA-GENERIC",
        "category": "Zoning & Setbacks",
        "title": "Front Yard Setback Minimum",
        "description": "Front setback on residential parcel must be at least 20 feet unless legally non-conforming or specific overlay applies.",
        "source_url": "https://www.dgs.ca.gov/BSC (Sample reference)",
        "effective_date": "2024-01-01",
        "severity": "warning",
        "human_review_required": True,
        "required_fields": ["setback_front"],
        "validation_logic": {"field": "setback_front", "min_feet": 20.0}
    },
    {
        "rule_code": "CRC-R301-SETBACK-SIDE",
        "jurisdiction_id": "US-CA-GENERIC",
        "category": "Zoning & Setbacks",
        "title": "Side Yard Setback Minimum",
        "description": "Side yard setback must be at least 5 feet for residential structures up to 2 stories.",
        "source_url": "https://www.dgs.ca.gov/BSC (Sample reference)",
        "effective_date": "2024-01-01",
        "severity": "warning",
        "human_review_required": True,
        "required_fields": ["setback_side"],
        "validation_logic": {"field": "setback_side", "min_feet": 5.0}
    },
    {
        "rule_code": "LADBS-DOC-SITEPLAN-NORTH",
        "jurisdiction_id": "US-CA-GENERIC",
        "category": "Site Requirements",
        "title": "Site Plan North Arrow Requirement",
        "description": "Site plan must indicate True North or Project North orientation.",
        "source_url": "https://www.ladbs.org (Sample reference)",
        "effective_date": "2024-01-01",
        "severity": "critical",
        "human_review_required": False,
        "required_fields": ["has_north_arrow"],
        "validation_logic": {"field": "has_north_arrow", "must_be": True}
    },
    {
        "rule_code": "LADBS-DOC-SCALE-NOTE",
        "jurisdiction_id": "US-CA-GENERIC",
        "category": "Architectural Drawings",
        "title": "Architectural Drawing Scale Annotation",
        "description": "All plan drawings must include explicit scale annotation (e.g. 1/4\" = 1'-0\" or bar scale).",
        "source_url": "https://www.ladbs.org (Sample reference)",
        "effective_date": "2024-01-01",
        "severity": "warning",
        "human_review_required": False,
        "required_fields": ["scale_annotation"],
        "validation_logic": {"field": "scale_annotation", "must_exist": True}
    },
    {
        "rule_code": "LADBS-FORM-SIGNATURE",
        "jurisdiction_id": "US-CA-GENERIC",
        "category": "Application Completeness",
        "title": "Applicant Declaration & Signature",
        "description": "Permit application form must feature applicant or authorized agent signature.",
        "source_url": "https://www.ladbs.org (Sample reference)",
        "effective_date": "2024-01-01",
        "severity": "critical",
        "human_review_required": True,
        "required_fields": ["applicant_name"],
        "validation_logic": {"field": "applicant_name", "must_exist": True}
    }
]

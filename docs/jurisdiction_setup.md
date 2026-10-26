# BuildPermit AI — Jurisdiction Setup & Ruleset Guide

## 1. Regulatory Integrity Principle
Building regulations are legally binding municipal enactments that vary between cities, counties, and building departments. 

To maintain regulatory integrity:
- **Never Fabricate Rules**: Rules must not be invented or populated with fictional building codes presented as official.
- **Explicit Sample Labeling**: Non-verified test rulesets are prominently designated as `[Non-Regulatory Dev Example]`.
- **Unsupported Jurisdiction Notice**: When a user selects a location without a verified ruleset, the platform explicitly displays a **"General Checks Only"** badge and skips local zoning evaluations.

## 2. Registering a New Jurisdiction

Jurisdictions are configured in `backend/app/compliance/source_registry.py` or stored in the `jurisdictions` database table:

```python
{
    "id": "US-CA-SANJOSE",
    "name": "City of San José Residential Guidelines (Sample)",
    "country": "United States",
    "state_region": "California",
    "city": "San José",
    "authority_name": "San José Building Division",
    "is_supported": True,
    "is_sample_ruleset": True,
    "notes": "NON-REGULATORY EXAMPLE RULESET based on single family addition checklist."
}
```

## 3. Defining Structured Rules

Each rule requires:
1. `rule_code`: Stable unique identifier (e.g. `CRC-R301-SETBACK-FRONT`).
2. `category`: Zoning & Setbacks, Site Requirements, Architectural Drawings, Structural & Life Safety, or Application Completeness.
3. `source_url`: Official government source publication or municipal municipal code reference.
4. `effective_date`: Date the building standard took effect.
5. `validation_logic`: Machine-evaluable conditions (e.g. `min_feet: 20.0`).
6. `severity`: `critical`, `warning`, or `info`.
7. `human_review_required`: Boolean flag indicating whether licensed professional verification is required.

import pytest
from app.compliance.cross_document_checks import run_cross_document_checks
from app.compliance.rule_engine import evaluate_jurisdiction_rules, parse_distance_feet
from app.compliance.checklist_engine import evaluate_checklist

def test_cross_document_checks_plain_language():
    """Verify that findings are written in understandable homeowner/builder language."""
    project = {
        "address": "124 Elm Street, Springfield, CA 90210",
        "project_type": "Residential Addition"
    }
    documents = [
        {
            "id": "doc-1",
            "filename": "Permit_App.pdf",
            "category": "Permit Application",
            "page_count": 1,
            "extracted_fields": {
                "property_address": "124 Elm Street, Springfield, CA 90210",
                "stated_building_area": 1850.0
            }
        },
        {
            "id": "doc-2",
            "filename": "Inconsistent_Plan.pdf",
            "category": "Structural Plans",
            "page_count": 1,
            "extracted_fields": {
                "property_address": "142 Elm Street, Springfield, CA 90210",
                "stated_building_area": 2400.0
            }
        },
        {
            "id": "doc-3",
            "filename": "Site_Plan.pdf",
            "category": "Site Plan",
            "page_count": 1,
            "extracted_fields": {}  # missing north arrow and scale
        }
    ]

    findings = run_cross_document_checks(project, documents)
    assert len(findings) >= 3

    for f in findings:
        # Title must be clear, human readable, and not start with internal codes
        assert not f["title"].startswith("CROSS-DOC")
        assert not f["title"].startswith("DOC-")
        assert len(f["title"]) > 10

        # Explanation must explain why it matters to the permit review
        assert len(f["explanation"]) > 30

        # Must have concrete next steps
        assert "recommended_action" in f
        assert len(f["recommended_action"]) > 20
        # Check that recommended action tells the user what to ask or check
        assert any(word in f["recommended_action"].lower() for word in ["ask", "check", "ensure", "verify", "upload", "confirm", "update"])

def test_setback_rules_plain_language():
    """Verify setback violations explain the requirement and zoning buffer in simple terms."""
    project = {"project_type": "Residential Addition"}
    documents = [
        {
            "id": "doc-1",
            "filename": "Site_Plan.pdf",
            "category": "Site Plan",
            "extracted_fields": {
                "setback_front": "12'-0\""
            }
        }
    ]
    findings = evaluate_jurisdiction_rules(project, documents, "US-CA-GENERIC")
    assert len(findings) == 1
    
    sb_find = findings[0]
    # Check title is plain language
    assert "Front Yard Setback" in sb_find["title"]
    assert "12.0 ft vs 20.0 ft" in sb_find["title"] or "12" in sb_find["title"]
    # Check explanation explains planning/zoning impact
    assert "property line" in sb_find["explanation"].lower()
    # Check recommended action advises on shifting or variance
    assert "variance" in sb_find["recommended_action"].lower() or "drafter" in sb_find["recommended_action"].lower()

def test_parse_distance_feet_resilience():
    """Verify distance parser handles diverse architectural dimension formats."""
    assert parse_distance_feet("15'-6\"") == 15.0
    assert parse_distance_feet("20 ft") == 20.0
    assert parse_distance_feet("25.5") == 25.5
    assert parse_distance_feet(30) == 30.0
    assert parse_distance_feet(None) == 0.0
    assert parse_distance_feet("N/A") == 0.0
    assert parse_distance_feet("") == 0.0

def test_neutral_wording_no_unsupported_rejection_claims():
    """Verify that findings never make unsupported claims like 'city will reject plans'."""
    project = {
        "address": "124 Elm Street, Springfield, CA 90210",
        "project_type": "Residential Addition"
    }
    documents = [
        {
            "id": "doc-1",
            "filename": "Permit_App.pdf",
            "category": "Permit Application",
            "page_count": 1,
            "extracted_fields": {
                "property_address": "124 Elm Street, Springfield, CA 90210"
            }
        },
        {
            "id": "doc-2",
            "filename": "Inconsistent_Plan.pdf",
            "category": "Structural Plans",
            "page_count": 1,
            "extracted_fields": {
                "property_address": "142 Elm Street, Springfield, CA 90210"
            }
        }
    ]
    findings = run_cross_document_checks(project, documents)
    assert len(findings) > 0
    for f in findings:
        exp_lower = f["explanation"].lower()
        assert "will reject" not in exp_lower
        assert "rejection" not in exp_lower
        # Check rule references distinguish sample guidance
        if f["category"] in ("Missing Document", "Missing Field"):
            assert "Sample Guidance" in f.get("rule_reference", "")
            # Missing document is warning, not critical
            assert f["severity"] == "warning"


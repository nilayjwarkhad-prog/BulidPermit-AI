import pytest
from app.compliance.checklist_engine import evaluate_checklist, STANDARD_CHECKLIST_TEMPLATE

def test_checklist_template_structure():
    """Verify all template items have valid metadata and plain-language descriptions."""
    assert len(STANDARD_CHECKLIST_TEMPLATE) >= 10
    for item in STANDARD_CHECKLIST_TEMPLATE:
        assert item["requirement_code"].startswith("CHK-")
        assert len(item["title"]) > 5
        assert len(item["description"]) > 20
        assert len(item["category"]) > 3
        assert "why_it_matters" in item
        assert "how_to_fix" in item

def test_evaluate_checklist_empty_submittal():
    """Engine should handle completely empty document packages gracefully."""
    project = {
        "address": "742 Evergreen Terrace, Springfield, CA",
        "project_type": "Residential Addition"
    }
    results = evaluate_checklist(project, [], [])
    
    assert len(results) > 0
    # Mandatory items should be marked missing with helpful instructions
    missing_items = [r for r in results if r["status"] == "missing"]
    assert len(missing_items) > 0
    for item in missing_items:
        assert item["notes"] is not None and len(item["notes"]) > 10
        # No unhandled technical terms in user-facing notes
        assert "CROSS-DOC" not in item["notes"]
        assert "None" not in item["title"]

def test_evaluate_checklist_complete_package():
    """Verify that a fully compliant submittal gets complete statuses and evidence links."""
    project = {
        "address": "124 Elm Street, Springfield, CA",
        "project_type": "Residential Addition"
    }
    documents = [
        {
            "id": "doc-app",
            "filename": "City_Permit_Application.pdf",
            "category": "Permit Application",
            "page_count": 2,
            "extracted_fields": {
                "applicant_name": "Alex Builder",
                "property_address": "124 Elm Street, Springfield, CA"
            }
        },
        {
            "id": "doc-site",
            "filename": "Civil_Site_Plan.pdf",
            "category": "Site Plan",
            "page_count": 1,
            "extracted_fields": {
                "setback_front": "25'-0\"",
                "setback_side": "10'-0\"",
                "has_north_arrow": True,
                "scale_annotation": "1/4\" = 1'-0\""
            }
        },
        {
            "id": "doc-floor",
            "filename": "Architectural_Floor_Plan.pdf",
            "category": "Floor Plan",
            "page_count": 3,
            "extracted_fields": {
                "identified_rooms": ["Living Room", "Master Bedroom", "Bathroom"],
                "stated_building_area": 1850.0
            }
        },
        {
            "id": "doc-elev",
            "filename": "Exterior_Elevations.pdf",
            "category": "Elevation Drawing",
            "page_count": 2,
            "extracted_fields": {}
        },
        {
            "id": "doc-struct",
            "filename": "Structural_Framing.pdf",
            "category": "Structural Plans",
            "page_count": 4,
            "extracted_fields": {
                "has_professional_stamp": True
            }
        }
    ]

    results = evaluate_checklist(project, documents, [])
    
    status_map = {r["requirement_code"]: r for r in results}
    
    # Address match should be complete
    assert status_map["CHK-ADDR-MATCH"]["status"] == "complete"
    assert "124 Elm Street" in status_map["CHK-ADDR-MATCH"]["notes"]
    assert status_map["CHK-ADDR-MATCH"]["evidence_document_name"] == "City_Permit_Application.pdf"

    # Site plan should be complete
    assert status_map["CHK-SITE-PLAN"]["status"] == "complete"
    assert status_map["CHK-NORTH-ARROW"]["status"] == "complete"

    # Floor plan should be complete
    assert status_map["CHK-FLOOR-PLAN"]["status"] == "complete"
    assert "Living Room" in status_map["CHK-FLOOR-PLAN"]["notes"]

    # Elevation and Structural should be complete
    assert status_map["CHK-ELEVATION"]["status"] == "complete"
    assert status_map["CHK-STRUCT-PLAN"]["status"] == "complete"

def test_evaluate_checklist_reflects_address_conflict():
    """When an address conflict finding exists, checklist should flag CHK-ADDR-MATCH."""
    project = {
        "address": "124 Elm Street, Springfield, CA",
        "project_type": "Residential Addition"
    }
    documents = [
        {
            "id": "doc-app",
            "filename": "Permit_App.pdf",
            "category": "Permit Application",
            "extracted_fields": {"property_address": "124 Elm Street"}
        },
        {
            "id": "doc-site",
            "filename": "Wrong_Address_Plan.pdf",
            "category": "Site Plan",
            "extracted_fields": {"property_address": "142 Elm Street"}
        }
    ]
    findings = [
        {
            "rule_code": "CROSS-DOC-ADDR-MISMATCH",
            "title": "Property Address Does Not Match Between Documents",
            "document_id": "doc-site",
            "document_name": "Wrong_Address_Plan.pdf",
            "page_number": 1
        }
    ]

    results = evaluate_checklist(project, documents, findings)
    addr_item = next(r for r in results if r["requirement_code"] == "CHK-ADDR-MATCH")
    
    assert addr_item["status"] == "needs_verification"
    assert "Address conflict detected" in addr_item["notes"]
    assert "Wrong_Address_Plan.pdf" in addr_item["notes"]

def test_evaluate_checklist_reflects_area_conflict():
    """When an area mismatch finding exists, checklist should flag CHK-FLOOR-PLAN."""
    project = {
        "address": "124 Elm Street",
        "project_type": "Residential Addition"
    }
    documents = [
        {
            "id": "doc-fp",
            "filename": "Floor_Plan.pdf",
            "category": "Floor Plan",
            "extracted_fields": {"stated_building_area": 1850.0}
        }
    ]
    findings = [
        {
            "rule_code": "CROSS-DOC-AREA-MISMATCH",
            "title": "Square Footage Conflict Between Plan Sheets",
            "document_id": "doc-fp",
            "document_name": "Floor_Plan.pdf"
        }
    ]

    results = evaluate_checklist(project, documents, findings)
    fp_item = next(r for r in results if r["requirement_code"] == "CHK-FLOOR-PLAN")
    
    assert fp_item["status"] == "needs_verification"
    assert "square footage conflicts" in fp_item["notes"].lower()

def test_evaluate_checklist_project_type_customization():
    """Verify that project types mark non-applicable items appropriately."""
    remodel_project = {
        "address": "55 Maple Ave",
        "project_type": "Renovation / Remodel"
    }
    results = evaluate_checklist(remodel_project, [], [])
    status_map = {r["requirement_code"]: r for r in results}

    # Site plan and elevations are not typically required for interior remodels
    assert status_map["CHK-SITE-PLAN"]["status"] == "not_applicable"
    assert status_map["CHK-ELEVATION"]["status"] == "not_applicable"
    assert "not required" in status_map["CHK-SITE-PLAN"]["notes"].lower()

    # But floor plan and application are required
    assert status_map["CHK-FLOOR-PLAN"]["status"] == "missing"
    assert status_map["CHK-APP-FORM"]["status"] == "missing"

def test_evaluate_checklist_resilience_to_malformed_inputs():
    """Engine must not crash under null fields or corrupted inputs."""
    project = {}
    corrupted_docs = [
        {"id": "d1"},  # missing filename, category, extracted_fields
        {"id": "d2", "filename": None, "category": None, "extracted_fields": None},
        {"id": "d3", "filename": "test.pdf", "category": 12345, "extracted_fields": {"setback_front": None}}
    ]
    corrupted_findings = [
        {"rule_code": None},
        {}
    ]
    results = evaluate_checklist(project, corrupted_docs, corrupted_findings)
    assert len(results) == len(STANDARD_CHECKLIST_TEMPLATE)
    for r in results:
        assert isinstance(r["title"], str)
        assert isinstance(r["notes"], str)
        assert r["status"] in ("complete", "missing", "needs_verification", "not_applicable")

import os
from app.compliance.cross_document_checks import run_cross_document_checks, normalize_address
from app.compliance.rule_engine import evaluate_jurisdiction_rules, parse_distance_feet
from app.compliance.checklist_engine import evaluate_checklist
from app.reports.pdf_generator import generate_pdf_report

def test_address_normalization():
    assert normalize_address("124 Elm Street, Springfield, CA") == normalize_address("124 Elm St., Springfield CA")
    assert normalize_address("500 Ocean Avenue") == normalize_address("500 Ocean Ave")

def test_cross_document_checks_detects_inconsistency():
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
                "property_address": "142 Elm Street, Springfield, CA 90210",  # Typo: 142 vs 124
                "stated_building_area": 2400.0  # Conflicting area: 2400 vs 1850
            }
        }
    ]

    findings = run_cross_document_checks(project, documents)
    rule_codes = [f["rule_code"] for f in findings]
    
    assert "CROSS-DOC-ADDR-MISMATCH" in rule_codes
    assert "CROSS-DOC-AREA-MISMATCH" in rule_codes

def test_rule_engine_evaluates_setbacks():
    project = {"project_type": "Residential Addition"}
    # Sub-standard setback (12 ft vs required 20 ft)
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
    assert any("SETBACK-FRONT" in f["rule_code"] for f in findings)

def test_pdf_report_generation(tmp_path):
    report_file = os.path.join(tmp_path, "test_report.pdf")
    project = {
        "name": "Test Residence Addition",
        "address": "124 Elm Street",
        "city": "Springfield",
        "state_region": "CA",
        "project_type": "Residential Addition",
        "jurisdiction_id": "US-CA-GENERIC"
    }
    docs = [{"filename": "Permit_App.pdf", "category": "Permit Application", "page_count": 1}]
    findings = [{"title": "Address Inconsistency", "explanation": "Detail", "severity": "critical", "status": "open"}]
    checklist = [{"category": "Site", "title": "Site Plan", "description": "Req", "status": "complete"}]

    res = generate_pdf_report(report_file, project, docs, findings, checklist, "BPAI-TEST-001")
    assert res is True
    assert os.path.exists(report_file)
    assert os.path.getsize(report_file) > 1000

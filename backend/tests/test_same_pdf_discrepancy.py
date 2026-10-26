import io
import pytest
from reportlab.pdfgen import canvas

from app.document_processing.pdf_loader import extract_document_content
from app.document_processing.field_extractor import extract_fields_from_document
from app.compliance.cross_document_checks import run_cross_document_checks, normalize_address


def create_synthetic_multipage_pdf(file_path: str, pages_content: list) -> str:
    """Helper to create deterministic multi-page PDF with exact text lines."""
    c = canvas.Canvas(file_path)
    for text_block in pages_content:
        for idx, line in enumerate(text_block.split("\n")):
            c.drawString(72, 750 - (idx * 20), line)
        c.showPage()
    c.save()
    return file_path


# ==============================================================================
# 1. Conflicting addresses on pages 2 and 4 of one PDF
# ==============================================================================
def test_same_pdf_conflicting_addresses_pages_2_and_4(tmp_path):
    pdf_path = str(tmp_path / "address_conflict.pdf")
    pages = [
        "Page 1 - Cover Sheet\nProject: Residential Addition",
        "Page 2 - Project Summary\nProject Address: 124 Example Lane, Sampletown, ZZ 00000\nDeclared proposed addition area: 420 square feet",
        "Page 3 - Sheet A-101\nProject Address: 124 Example Lane, Sampletown, ZZ 00000\nProposed Addition Area: 420 square feet",
        "Page 4 - Sheet A-102\nProject Address: 142 Example Lane, Sampletown, ZZ 00000\nDeclared proposed addition area: 420 square feet",
        "Page 5 - General Notes\nEnd of Drawing Set"
    ]
    create_synthetic_multipage_pdf(pdf_path, pages)

    content = extract_document_content(pdf_path)
    fields = extract_fields_from_document("Other Supporting Document", content["full_text"], content["pages"])

    # Verify per-page extraction
    assert len(fields["_page_fields"]) == 5
    assert fields["_page_fields"][1]["property_address"] == "124 Example Lane, Sampletown, ZZ 00000"
    assert fields["_page_fields"][2]["property_address"] == "124 Example Lane, Sampletown, ZZ 00000"
    assert fields["_page_fields"][3]["property_address"] == "142 Example Lane, Sampletown, ZZ 00000"

    project = {
        "address": "124 Example Lane, Sampletown, ZZ 00000",
        "project_type": "Residential Addition"
    }
    documents = [{
        "id": "doc-addr-test",
        "filename": "address_conflict.pdf",
        "category": "Other Supporting Document",
        "page_count": 5,
        "pages_data": content["pages"],
        "extracted_fields": fields
    }]

    findings = run_cross_document_checks(project, documents)
    addr_findings = [f for f in findings if f["rule_code"] == "CROSS-DOC-ADDR-MISMATCH"]

    assert len(addr_findings) == 1
    f = addr_findings[0]
    assert f["category"] == "Inconsistency"
    assert f["severity"] == "critical"
    assert f["document_id"] == "doc-addr-test"
    assert f["document_name"] == "address_conflict.pdf"
    assert f["page_number"] in (2, 4)
    # Explanation cites both pages
    assert "Page 2" in f["explanation"] or "Pages 2, 3" in f["explanation"]
    assert "Page 4" in f["explanation"]
    # Evidence cites both addresses
    assert "124 Example Lane" in f["evidence_text"]
    assert "142 Example Lane" in f["evidence_text"]


# ==============================================================================
# 2. Conflicting areas on pages 3 and 4 of one PDF
# ==============================================================================
def test_same_pdf_conflicting_areas_pages_3_and_4(tmp_path):
    pdf_path = str(tmp_path / "area_conflict.pdf")
    pages = [
        "Page 1 - Cover Sheet\nProject: Residential Addition",
        "Page 2 - Project Summary\nProject Address: 124 Example Lane, Sampletown, ZZ 00000\nDeclared proposed addition area: 420 square feet",
        "Page 3 - Sheet A-101\nProject Address: 124 Example Lane, Sampletown, ZZ 00000\nProposed Addition Area: 420 square feet",
        "Page 4 - Sheet A-102\nProject Address: 124 Example Lane, Sampletown, ZZ 00000\nDeclared proposed addition area: 480 square feet",
        "Page 5 - General Notes\nEnd of Drawing Set"
    ]
    create_synthetic_multipage_pdf(pdf_path, pages)

    content = extract_document_content(pdf_path)
    fields = extract_fields_from_document("Other Supporting Document", content["full_text"], content["pages"])

    # Verify per-page extraction
    assert fields["_page_fields"][1]["addition_area"] == 420.0
    assert fields["_page_fields"][2]["addition_area"] == 420.0
    assert fields["_page_fields"][3]["addition_area"] == 480.0

    project = {
        "address": "124 Example Lane, Sampletown, ZZ 00000",
        "project_type": "Residential Addition"
    }
    documents = [{
        "id": "doc-area-test",
        "filename": "area_conflict.pdf",
        "category": "Other Supporting Document",
        "page_count": 5,
        "pages_data": content["pages"],
        "extracted_fields": fields
    }]

    findings = run_cross_document_checks(project, documents)
    area_findings = [f for f in findings if f["rule_code"] == "CROSS-DOC-AREA-MISMATCH"]

    assert len(area_findings) == 1
    f = area_findings[0]
    assert f["category"] == "Inconsistency"
    assert f["severity"] == "warning"
    assert f["document_id"] == "doc-area-test"
    assert f["document_name"] == "area_conflict.pdf"
    assert f["page_number"] in (2, 3, 4)
    assert "420 sq ft" in f["evidence_text"]
    assert "480 sq ft" in f["evidence_text"]
    assert "12.5%" in f["explanation"] or "difference" in f["explanation"]


# ==============================================================================
# 3. Both address and area conflicts simultaneously in synthetic package
# ==============================================================================
def test_same_pdf_both_address_and_area_conflicts(tmp_path):
    """Matches the exact user test scenario with BP Synthetic Test 002."""
    pdf_path = str(tmp_path / "buildpermit_synthetic_test_package.pdf")
    pages = [
        "SYNTHETIC TEST DOCUMENT\nFictional project address: 124 Example Lane, Sampletown, ZZ 00000\nProject type: Residential addition",
        "Page 2 - Project Summary\nProject Address: 124 Example Lane, Sampletown, ZZ 00000\nDeclared proposed addition area: 420 square feet",
        "Page 3 - Sheet A-101\nProject Address: 124 Example Lane, Sampletown, ZZ 00000\nProposed Addition Area: 420 square feet",
        "Page 4 - Deliberate Test Discrepancy\nProject Address: 142 Example Lane, Sampletown, ZZ 00000\nDeclared proposed addition area: 480 square feet",
        "Page 5 - Test Checklist Context\nEnd of package"
    ]
    create_synthetic_multipage_pdf(pdf_path, pages)

    content = extract_document_content(pdf_path)
    fields = extract_fields_from_document("Other Supporting Document", content["full_text"], content["pages"])

    project = {
        "address": "124 Example Lane, Sampletown, ZZ 00000",
        "project_type": "Residential Addition"
    }
    documents = [{
        "id": "doc-syn-pkg",
        "filename": "buildpermit_synthetic_test_package.pdf",
        "category": "Other Supporting Document",
        "page_count": 5,
        "pages_data": content["pages"],
        "extracted_fields": fields
    }]

    findings = run_cross_document_checks(project, documents)

    addr_findings = [f for f in findings if f["rule_code"] == "CROSS-DOC-ADDR-MISMATCH"]
    area_findings = [f for f in findings if f["rule_code"] == "CROSS-DOC-AREA-MISMATCH"]
    missing_findings = [f for f in findings if f["category"] == "Missing Document"]

    # Both conflicts detected
    assert len(addr_findings) == 1
    assert len(area_findings) == 1
    # Missing document findings remain separate and present
    assert len(missing_findings) >= 2

    # Address finding details
    af = addr_findings[0]
    assert "124 Example Lane" in af["evidence_text"]
    assert "142 Example Lane" in af["evidence_text"]
    assert "Page 4" in af["evidence_text"]
    assert af["document_name"] == "buildpermit_synthetic_test_package.pdf"

    # Area finding details
    arf = area_findings[0]
    assert "420 sq ft" in arf["evidence_text"]
    assert "480 sq ft" in arf["evidence_text"]
    assert "Page 4" in arf["evidence_text"]
    assert arf["document_name"] == "buildpermit_synthetic_test_package.pdf"


# ==============================================================================
# 4. Consistent values across all pages produce no discrepancy findings
# ==============================================================================
def test_same_pdf_consistent_values_produce_no_discrepancy(tmp_path):
    pdf_path = str(tmp_path / "consistent_package.pdf")
    pages = [
        "Page 1 - Cover Sheet\nProject: Residential Addition",
        "Page 2 - Project Summary\nProject Address: 124 Example Lane, Sampletown, ZZ 00000\nDeclared proposed addition area: 420 square feet",
        "Page 3 - Sheet A-101\nProject Address: 124 Example Lane, Sampletown, ZZ 00000\nProposed Addition Area: 420 square feet",
        "Page 4 - Sheet A-102\nProject Address: 124 Example Lane\nDeclared proposed addition area: 425 square feet",  # 1.1% difference <= 5%
        "Page 5 - General Notes"
    ]
    create_synthetic_multipage_pdf(pdf_path, pages)

    content = extract_document_content(pdf_path)
    fields = extract_fields_from_document("Other Supporting Document", content["full_text"], content["pages"])

    project = {
        "address": "124 Example Lane, Sampletown, ZZ 00000",
        "project_type": "Residential Addition"
    }
    documents = [{
        "id": "doc-consistent",
        "filename": "consistent_package.pdf",
        "category": "Other Supporting Document",
        "page_count": 5,
        "pages_data": content["pages"],
        "extracted_fields": fields
    }]

    findings = run_cross_document_checks(project, documents)
    addr_findings = [f for f in findings if f["rule_code"] == "CROSS-DOC-ADDR-MISMATCH"]
    area_findings = [f for f in findings if f["rule_code"] == "CROSS-DOC-AREA-MISMATCH"]

    assert len(addr_findings) == 0
    assert len(area_findings) == 0


# ==============================================================================
# 5. The same conflict across two separate PDFs
# ==============================================================================
def test_cross_pdf_address_and_area_conflicts(tmp_path):
    pdf1_path = str(tmp_path / "Doc1_Summary.pdf")
    pages1 = [
        "Sheet 1 - Application Summary\nProject Address: 124 Example Lane, Sampletown, ZZ 00000\nProposed Addition Area: 420 square feet"
    ]
    create_synthetic_multipage_pdf(pdf1_path, pages1)

    pdf2_path = str(tmp_path / "Doc2_Drawings.pdf")
    pages2 = [
        "Sheet 1 - Cover Sheet",
        "Sheet 2 - Floor Plan\nProject Address: 142 Example Lane, Sampletown, ZZ 00000\nDeclared proposed addition area: 480 square feet"
    ]
    create_synthetic_multipage_pdf(pdf2_path, pages2)

    c1 = extract_document_content(pdf1_path)
    f1 = extract_fields_from_document("Permit Application", c1["full_text"], c1["pages"])

    c2 = extract_document_content(pdf2_path)
    f2 = extract_fields_from_document("Floor Plan", c2["full_text"], c2["pages"])

    project = {
        "address": "124 Example Lane, Sampletown, ZZ 00000",
        "project_type": "Residential Addition"
    }
    documents = [
        {
            "id": "doc-1",
            "filename": "Doc1_Summary.pdf",
            "category": "Permit Application",
            "page_count": 1,
            "pages_data": c1["pages"],
            "extracted_fields": f1
        },
        {
            "id": "doc-2",
            "filename": "Doc2_Drawings.pdf",
            "category": "Floor Plan",
            "page_count": 2,
            "pages_data": c2["pages"],
            "extracted_fields": f2
        }
    ]

    findings = run_cross_document_checks(project, documents)
    addr_findings = [f for f in findings if f["rule_code"] == "CROSS-DOC-ADDR-MISMATCH"]
    area_findings = [f for f in findings if f["rule_code"] == "CROSS-DOC-AREA-MISMATCH"]

    assert len(addr_findings) >= 1
    assert len(area_findings) == 1

    af = addr_findings[0]
    assert "Doc2_Drawings.pdf" in af["document_name"] or "Doc1_Summary.pdf" in af["document_name"]
    assert "142 Example Lane" in af["evidence_text"] or "142 Example Lane" in af["explanation"]

    arf = area_findings[0]
    assert "Doc1_Summary.pdf" in arf["evidence_text"]
    assert "Doc2_Drawings.pdf" in arf["evidence_text"]
    assert "420 sq ft" in arf["evidence_text"]
    assert "480 sq ft" in arf["evidence_text"]


# ==============================================================================
# 6. Duplicate prevention when multiple pages share the same conflicting value
# ==============================================================================
def test_duplicate_prevention_on_multiple_pages(tmp_path):
    pdf_path = str(tmp_path / "multi_repeats.pdf")
    pages = [
        "Page 1 - Summary\nProject Address: 124 Example Lane\nProposed Addition Area: 420 square feet",
        "Page 2 - Sheet A-1\nProject Address: 124 Example Lane\nProposed Addition Area: 420 square feet",
        "Page 3 - Sheet A-2\nProject Address: 124 Example Lane\nProposed Addition Area: 420 square feet",
        "Page 4 - Sheet A-3\nProject Address: 142 Example Lane\nProposed Addition Area: 480 square feet",
        "Page 5 - Sheet A-4\nProject Address: 142 Example Lane\nProposed Addition Area: 480 square feet"
    ]
    create_synthetic_multipage_pdf(pdf_path, pages)

    content = extract_document_content(pdf_path)
    fields = extract_fields_from_document("Other Supporting Document", content["full_text"], content["pages"])

    project = {
        "address": "124 Example Lane",
        "project_type": "Residential Addition"
    }
    documents = [{
        "id": "doc-dup-test",
        "filename": "multi_repeats.pdf",
        "category": "Other Supporting Document",
        "page_count": 5,
        "pages_data": content["pages"],
        "extracted_fields": fields
    }]

    findings = run_cross_document_checks(project, documents)
    addr_findings = [f for f in findings if f["rule_code"] == "CROSS-DOC-ADDR-MISMATCH"]
    area_findings = [f for f in findings if f["rule_code"] == "CROSS-DOC-AREA-MISMATCH"]

    # Exactly 1 finding for address conflict, exactly 1 finding for area conflict
    assert len(addr_findings) == 1
    assert len(area_findings) == 1


# ==============================================================================
# 7. Ambiguous and non-conflicting extractions do not produce false positives
# ==============================================================================
def test_ambiguous_and_non_conflicting_extractions(tmp_path):
    pdf_path = str(tmp_path / "non_conflicting.pdf")
    pages = [
        # Page 1: Living area 2,400 sq ft (main house)
        "Page 1 - Existing House Data\nProject Address: 124 Example Lane, Sampletown, ZZ 00000\nTotal Living Area: 2,400 sq ft",
        # Page 2: Proposed addition area 420 sq ft (addition scope)
        "Page 2 - Proposed Scope\nProject Address: 124 Example Lane\nProposed Addition Area: 420 sq ft",
        # Page 3: General mention without contradictory street address
        "Page 3 - General Notes\nSite Location: Sampletown, ZZ"
    ]
    create_synthetic_multipage_pdf(pdf_path, pages)

    content = extract_document_content(pdf_path)
    fields = extract_fields_from_document("Other Supporting Document", content["full_text"], content["pages"])

    project = {
        "address": "124 Example Lane, Sampletown, ZZ 00000",
        "project_type": "Residential Addition"
    }
    documents = [{
        "id": "doc-no-false-pos",
        "filename": "non_conflicting.pdf",
        "category": "Other Supporting Document",
        "page_count": 3,
        "pages_data": content["pages"],
        "extracted_fields": fields
    }]

    findings = run_cross_document_checks(project, documents)
    addr_findings = [f for f in findings if f["rule_code"] == "CROSS-DOC-ADDR-MISMATCH"]
    area_findings = [f for f in findings if f["rule_code"] == "CROSS-DOC-AREA-MISMATCH"]

    assert len(addr_findings) == 0
    assert len(area_findings) == 0


# ==============================================================================
# 8. Full Pipeline & Findings API Integration Test
# ==============================================================================
@pytest.mark.asyncio
async def test_same_pdf_full_pipeline_persistence_and_findings_api(client, auth_headers, db_session, tmp_path):
    """
    End-to-end test verifying that uploaded PDF with same-document conflicts
    persists findings in DB and returns them via GET /api/v1/projects/{id}/findings.
    """
    from app.models.analysis import AnalysisJob
    from app.services.analysis_service import execute_project_analysis

    # 1. Create project
    create_res = client.post("/api/v1/projects", json={
        "name": "Same-PDF Conflict Residence",
        "description": "Integration test for same-PDF discrepancy persistence",
        "country": "United States",
        "state_region": "California",
        "city": "Sampletown",
        "address": "124 Example Lane, Sampletown, ZZ 00000",
        "project_type": "Residential Addition",
        "building_type": "Single Family Residence",
        "num_floors": 1,
        "area": 1850.0,
        "area_unit": "sq_ft",
        "stage": "Pre-Submission Preparation",
        "jurisdiction_id": "US-CA-GENERIC"
    }, headers=auth_headers)
    assert create_res.status_code == 201
    proj_id = create_res.json()["id"]

    # 2. Create synthetic multipage PDF with conflicts
    pdf_path = str(tmp_path / "buildpermit_synthetic_test_package.pdf")
    pages = [
        "SYNTHETIC TEST DOCUMENT\nFictional project address: 124 Example Lane, Sampletown, ZZ 00000\nProject type: Residential addition",
        "Page 2 - Project Summary\nProject Address: 124 Example Lane, Sampletown, ZZ 00000\nDeclared proposed addition area: 420 square feet",
        "Page 3 - Sheet A-101\nProject Address: 124 Example Lane, Sampletown, ZZ 00000\nProposed Addition Area: 420 square feet",
        "Page 4 - Deliberate Test Discrepancy\nProject Address: 142 Example Lane, Sampletown, ZZ 00000\nDeclared proposed addition area: 480 square feet",
        "Page 5 - Test Checklist Context\nEnd of package"
    ]
    create_synthetic_multipage_pdf(pdf_path, pages)

    # 3. Upload document via API
    with open(pdf_path, "rb") as f:
        upload_res = client.post(
            f"/api/v1/projects/{proj_id}/documents",
            files={"file": ("buildpermit_synthetic_test_package.pdf", f, "application/pdf")},
            data={"category": "Floor Plan"},
            headers=auth_headers
        )
    assert upload_res.status_code == 201
    doc_id = upload_res.json()["id"]

    # 4. Execute analysis pipeline
    job = AnalysisJob(
        project_id=proj_id,
        status="pending",
        current_step="Starting",
        total_steps=9,
        progress_percentage=0.0
    )
    db_session.add(job)
    db_session.commit()
    db_session.refresh(job)

    await execute_project_analysis(job.id, db_session)

    db_session.refresh(job)
    assert job.status == "completed"

    # 5. Query Findings API endpoint
    findings_res = client.get(f"/api/v1/projects/{proj_id}/findings", headers=auth_headers)
    assert findings_res.status_code == 200
    findings = findings_res.json()

    # Verify both inconsistency findings are returned with accurate page and evidence
    addr_findings = [f for f in findings if f["rule_code"] == "CROSS-DOC-ADDR-MISMATCH"]
    area_findings = [f for f in findings if f["rule_code"] == "CROSS-DOC-AREA-MISMATCH"]

    assert len(addr_findings) == 1
    af = addr_findings[0]
    assert af["category"] == "Inconsistency"
    assert af["severity"] == "critical"
    assert af["document_id"] == doc_id
    assert af["document_name"] == "buildpermit_synthetic_test_package.pdf"
    assert af["page_number"] == 4
    assert "124 Example Lane" in af["evidence_text"]
    assert "142 Example Lane" in af["evidence_text"]

    assert len(area_findings) == 1
    rf = area_findings[0]
    assert rf["category"] == "Inconsistency"
    assert rf["severity"] == "warning"
    assert rf["document_id"] == doc_id
    assert rf["document_name"] == "buildpermit_synthetic_test_package.pdf"
    assert "420 sq ft" in rf["evidence_text"]
    assert "480 sq ft" in rf["evidence_text"]


import os
import pytest
from pypdf import PdfWriter
from reportlab.pdfgen import canvas

from app.document_processing.pdf_loader import (
    extract_document_content,
    EncryptedPDFError,
    CorruptPDFError
)
from app.document_processing.field_extractor import extract_fields_from_document
from app.document_processing.evidence_locator import (
    locate_evidence_in_pages,
    locate_all_evidence_in_pages
)
from app.compliance.cross_document_checks import run_cross_document_checks
from app.compliance.checklist_engine import evaluate_checklist
from app.compliance.rule_engine import evaluate_jurisdiction_rules
from app.document_processing.ocr_processor import ocr_processor

def create_synthetic_pdf(file_path: str, pages_content: list) -> str:
    """Creates a deterministic multi-page PDF with exact text on 1-indexed pages."""
    c = canvas.Canvas(file_path)
    for text_block in pages_content:
        for idx, line in enumerate(text_block.split("\n")):
            c.drawString(72, 750 - (idx * 20), line)
        c.showPage()
    c.save()
    return file_path

# ==============================================================================
# 1. An address appearing on page 3 of a multi-page PDF
# ==============================================================================
def test_address_appearing_on_page_3_of_multipage_pdf(tmp_path):
    """Verify that an address on sheet page 3 is traced back to page 3, not defaulting to page 1."""
    pdf_path = str(tmp_path / "multi_page_plan.pdf")
    pages = [
        "Sheet T-1: Cover Sheet\nProject: Residential Alteration\nArchitect: John Doe",
        "Sheet G-1: General Notes and Building Code Summary",
        "Sheet A-1: Site Plan\nPROJECT ADDRESS:\n999 Oak Street\nSpringfield, CA 90210\nFront Setback: 22'-0\"",
        "Sheet A-2: Structural Framing Details"
    ]
    create_synthetic_pdf(pdf_path, pages)

    content = extract_document_content(pdf_path)
    assert content["page_count"] == 4
    pages_data = content["pages"]
    
    # Verify extraction locates address on page 3
    fields = extract_fields_from_document("Site Plan", content["full_text"], pages_data)
    assert fields["property_address"] is not None
    assert fields["_field_pages"].get("property_address") == 3

    # Run cross-document check against project registered at 124 Elm Street
    project = {
        "address": "124 Elm Street, Springfield, CA 90210",
        "project_type": "Residential Addition"
    }
    documents = [{
        "id": "doc-multi-123",
        "filename": "multi_page_plan.pdf",
        "category": "Site Plan",
        "page_count": 4,
        "pages_data": pages_data,
        "extracted_fields": fields
    }]

    findings = run_cross_document_checks(project, documents)
    addr_findings = [f for f in findings if f["rule_code"] == "CROSS-DOC-ADDR-MISMATCH"]
    assert len(addr_findings) == 1
    
    finding = addr_findings[0]
    # Page must be 3, preserving document ID and document name
    assert finding["page_number"] == 3
    assert finding["document_id"] == "doc-multi-123"
    assert finding["document_name"] == "multi_page_plan.pdf"
    assert "Page 3" in finding["explanation"]
    assert "Page 3" in finding["recommended_action"]
    assert "Page 3" in finding["evidence_text"]

# ==============================================================================
# 2. An area value appearing on a later page
# ==============================================================================
def test_area_value_appearing_on_later_page(tmp_path):
    """Verify that square footage appearing on page 4 of a drawing set is correctly cited."""
    pdf_path = str(tmp_path / "architectural_set.pdf")
    pages = [
        "Sheet Cover: Index of Drawings",
        "Sheet Demolition: Existing Walls to be Removed",
        "Sheet Foundation: Concrete Footing Details",
        "Sheet A-4: Proposed Floor Plan\nTOTAL LIVING AREA: 2,850 SQ FT\nKitchen, Bath, Bedroom",
        "Sheet Roof: Truss Layout"
    ]
    create_synthetic_pdf(pdf_path, pages)

    content = extract_document_content(pdf_path)
    assert content["page_count"] == 5
    fields = extract_fields_from_document("Floor Plan", content["full_text"], content["pages"])
    assert fields["stated_building_area"] == 2850.0
    assert fields["_field_pages"].get("stated_building_area") == 4

    project = {
        "address": "124 Elm Street, Springfield, CA 90210",
        "project_type": "Residential Addition"
    }
    documents = [
        {
            "id": "doc-app-form",
            "filename": "Application_Form.pdf",
            "category": "Permit Application",
            "page_count": 1,
            "pages_data": [{"page_number": 1, "text": "Permit Application - Total Area: 1,850 SQ FT", "word_count": 10}],
            "extracted_fields": {
                "property_address": "124 Elm Street, Springfield, CA 90210",
                "stated_building_area": 1850.0,
                "_field_pages": {"stated_building_area": 1}
            }
        },
        {
            "id": "doc-drawings-456",
            "filename": "architectural_set.pdf",
            "category": "Floor Plan",
            "page_count": 5,
            "pages_data": content["pages"],
            "extracted_fields": fields
        }
    ]

    findings = run_cross_document_checks(project, documents)
    area_findings = [f for f in findings if f["rule_code"] == "CROSS-DOC-AREA-MISMATCH"]
    assert len(area_findings) == 1
    
    finding = area_findings[0]
    assert "Page 4" in finding["explanation"]
    assert "Page 4" in finding["evidence_text"]
    assert finding["document_id"] == "doc-app-form"

# ==============================================================================
# 3. Repeated values on multiple pages
# ==============================================================================
def test_repeated_values_on_multiple_pages(tmp_path):
    """Verify that values appearing on multiple pages are tracked across all pages."""
    pdf_path = str(tmp_path / "repeated_address.pdf")
    pages = [
        "Sheet T-1: Title Block\nPROJECT ADDRESS: 999 Oak Street, Springfield, CA 90210",
        "Sheet G-1: General Specifications",
        "Sheet S-1: Site Plan\nJOB ADDRESS: 999 Oak Street, Springfield, CA 90210\nFront Setback: 25 ft",
        "Sheet A-1: Floor Plan"
    ]
    create_synthetic_pdf(pdf_path, pages)

    content = extract_document_content(pdf_path)
    all_locs = locate_all_evidence_in_pages(content["pages"], "999 Oak Street, Springfield, CA 90210")
    assert len(all_locs) == 2
    matched_pages = [m["page_number"] for m in all_locs]
    assert matched_pages == [1, 3]

    fields = extract_fields_from_document("Site Plan", content["full_text"], content["pages"])
    assert fields["_field_all_pages"]["property_address"] == [1, 3]

    project = {
        "address": "124 Elm Street, Springfield, CA 90210",
        "project_type": "Residential Addition"
    }
    documents = [{
        "id": "doc-repeated",
        "filename": "repeated_address.pdf",
        "category": "Site Plan",
        "page_count": 4,
        "pages_data": content["pages"],
        "extracted_fields": fields
    }]

    findings = run_cross_document_checks(project, documents)
    addr_find = next(f for f in findings if f["rule_code"] == "CROSS-DOC-ADDR-MISMATCH")
    assert "Pages 1, 3" in addr_find["explanation"]
    assert "Pages 1, 3" in addr_find["recommended_action"]
    assert addr_find["page_number"] == 1

# ==============================================================================
# 4. Evidence that cannot be located confidently
# ==============================================================================
def test_evidence_that_cannot_be_located_confidently():
    """Verify that unlocated evidence is explicitly marked uncertain with page_number None (never invented)."""
    # Simulate a document where address text was extracted from noisy notes,
    # but the pages_data contains no recognizable match for the address.
    project = {
        "address": "124 Elm Street, Springfield, CA 90210",
        "project_type": "Residential Addition"
    }
    documents = [{
        "id": "doc-uncertain",
        "filename": "Unclear_Scan.pdf",
        "category": "Architectural Plans",
        "page_count": 3,
        "pages_data": [
            {"page_number": 1, "text": "Unrelated mechanical notes and specs", "word_count": 10},
            {"page_number": 2, "text": "Electrical circuit schedule", "word_count": 15},
            {"page_number": 3, "text": "Plumbing riser diagram", "word_count": 12}
        ],
        "extracted_fields": {
            "property_address": "555 Mystery Lane, Springfield, CA 90210",
            "_field_pages": {"property_address": None},
            "_field_all_pages": {"property_address": []}
        }
    }]

    findings = run_cross_document_checks(project, documents)
    addr_find = next(f for f in findings if f["rule_code"] == "CROSS-DOC-ADDR-MISMATCH")
    
    # Must NOT invent page 1
    assert addr_find["page_number"] is None
    assert "uncertain" in addr_find["explanation"].lower()
    assert "(Page uncertain)" in addr_find["evidence_text"]
    assert addr_find["confidence"] == 0.65
    assert addr_find["human_review_required"] is True

# ==============================================================================
# 5. A password-protected PDF
# ==============================================================================
def test_password_protected_pdf(tmp_path):
    """Verify that an encrypted PDF raises an EncryptedPDFError with a clear, safe message."""
    pdf_path = str(tmp_path / "locked_blueprint.pdf")
    writer = PdfWriter()
    writer.add_blank_page(width=612, height=792)
    writer.encrypt("top_secret_pass")
    with open(pdf_path, "wb") as f:
        writer.write(f)

    with pytest.raises(EncryptedPDFError) as excinfo:
        extract_document_content(pdf_path, mime_type="application/pdf")

    assert "password-protected or encrypted" in str(excinfo.value).lower()
    assert "unencrypted pdf" in str(excinfo.value).lower()

# ==============================================================================
# 6. An ordinary corrupt PDF, ensuring its error remains distinct
# ==============================================================================
def test_ordinary_corrupt_pdf_remains_distinct(tmp_path):
    """Verify that damaged/corrupt PDFs raise CorruptPDFError and are not mislabeled as encrypted."""
    corrupt_pdf_path = str(tmp_path / "broken_file.pdf")
    with open(corrupt_pdf_path, "wb") as f:
        f.write(b"%PDF-1.4\nCorrupted header junk without valid xref or objects\n%%EOF")

    with pytest.raises(CorruptPDFError) as excinfo:
        extract_document_content(corrupt_pdf_path, mime_type="application/pdf")

    err_str = str(excinfo.value).lower()
    assert "corrupt or unreadable" in err_str
    # Must NOT mislabel as password-protected
    assert "password" not in err_str
    assert "encrypted" not in err_str

# ==============================================================================
# Additional regression checks for multiline blocks, checklists, and sample rules
# ==============================================================================
def test_multiline_title_block_address_split_across_lines():
    """Verify values split across lines are matched and extracted properly."""
    text_p1 = "Cover sheet - General Notes"
    text_p2 = "SHEET A-1: ARCHITECTURAL SITE PLAN\nPROJECT ADDRESS:\n124 ELM STREET\nSPRINGFIELD, CA 90210\nFRONT SETBACK: 15'-0\""
    pages_data = [
        {"page_number": 1, "text": text_p1},
        {"page_number": 2, "text": text_p2}
    ]
    full_text = f"{text_p1}\n\n{text_p2}"
    fields = extract_fields_from_document("Site Plan", full_text, pages_data=pages_data)
    
    assert fields["property_address"] is not None
    assert "\n" not in fields["property_address"]
    assert fields["_field_pages"].get("property_address") == 2

def test_checklist_engine_dynamic_evidence_page():
    """Verify checklist cites real evidence sheet page and handles unlocated fields."""
    project = {"address": "124 Elm Street, Springfield, CA 90210", "project_type": "Residential Addition"}
    documents = [{
        "id": "doc-plans",
        "filename": "Drawing_Set.pdf",
        "category": "Site Plan",
        "page_count": 4,
        "pages_data": [
            {"page_number": 1, "text": "Cover Sheet"},
            {"page_number": 2, "text": "Site Plan - North Arrow - Setback: 20 ft"}
        ],
        "extracted_fields": {
            "property_address": "124 Elm Street, Springfield, CA 90210",
            "setback_front": "20 ft",
            "has_north_arrow": True,
            "_field_pages": {"property_address": 1, "setback_front": 2, "has_north_arrow": 2}
        }
    }]
    items = evaluate_checklist(project, documents, findings_data=[])
    sp_item = next(i for i in items if i["requirement_code"] == "CHK-SITE-PLAN")
    assert sp_item["evidence_page_number"] == 2
    assert "Sheet Page 2" in sp_item["notes"]

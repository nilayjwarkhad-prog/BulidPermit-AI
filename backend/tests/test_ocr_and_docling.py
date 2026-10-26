import os
import tempfile
from PIL import Image, ImageDraw
from app.document_processing.ocr_processor import ocr_processor
from app.document_processing.docling_processor import docling_processor
from app.document_processing.pdf_loader import extract_document_content

def test_docling_graceful_fallback():
    # Docling processor is_available should be a boolean
    assert isinstance(docling_processor.is_available(), bool)
    # Processing on non-existent or dummy file should return None or result without crashing
    res = docling_processor.process_document("non_existent_file.pdf")
    assert res is None

def test_ocr_processor_with_blueprint_image():
    # Create a temporary blueprint image
    with tempfile.NamedTemporaryFile(suffix=".png", delete=False) as tmp:
        tmp_path = tmp.name

    try:
        img = Image.new("RGB", (600, 400), color="#1E3A8A")
        draw = ImageDraw.Draw(img)
        draw.text((20, 20), "SITE PLAN - LOT 42", fill="#FFFFFF")
        img.save(tmp_path, "PNG")

        ocr_res = ocr_processor.process_scanned_image(tmp_path)
        assert isinstance(ocr_res, dict)
        assert "engine" in ocr_res or "error" in ocr_res

        # If pytesseract is not installed on system, fallback should return dimensions and notice
        if not ocr_processor.is_available():
            assert ocr_res["engine"] == "image_metadata_fallback"
            assert ocr_res["dimensions"]["width"] == 600
            assert ocr_res["dimensions"]["height"] == 400
            assert "blueprint" in ocr_res["notice"].lower()
    finally:
        if os.path.exists(tmp_path):
            os.remove(tmp_path)

def test_extract_document_content_image():
    with tempfile.NamedTemporaryFile(suffix=".png", delete=False) as tmp:
        tmp_path = tmp.name

    try:
        img = Image.new("RGB", (800, 600), color="#FFFFFF")
        img.save(tmp_path, "PNG")

        content = extract_document_content(tmp_path, mime_type="image/png")
        assert content["page_count"] == 1
        assert content["is_scanned"] is True
        assert len(content["pages"]) == 1
        assert content["pages"][0]["dimensions"]["width"] == 800
        assert content["pages"][0]["dimensions"]["height"] == 600
    finally:
        if os.path.exists(tmp_path):
            os.remove(tmp_path)

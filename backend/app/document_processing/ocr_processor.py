import os
from typing import Dict, Any, Optional
from PIL import Image
from app.core.logging import log_info, log_warning

HAVE_PYTESSERACT = False
try:
    import pytesseract
    # Test if tesseract binary is accessible
    pytesseract.get_tesseract_version()
    HAVE_PYTESSERACT = True
except (ImportError, Exception):
    HAVE_PYTESSERACT = False

class OCRProcessor:
    def __init__(self):
        self.available = HAVE_PYTESSERACT

    def is_available(self) -> bool:
        return self.available

    def process_scanned_image(self, image_path: str) -> Dict[str, Any]:
        """
        Extracts text from scanned plan sheets or drawing images.
        Falls back gracefully with diagnostic metadata if OCR binary is not installed.
        """
        if not os.path.exists(image_path):
            return {"text": "", "word_count": 0, "ocr_success": False, "error": "Image file not found"}

        if self.available:
            try:
                log_info(f"Running OCR on {image_path}...")
                with Image.open(image_path) as img:
                    text = pytesseract.image_to_string(img)
                words = text.split()
                return {
                    "text": text,
                    "word_count": len(words),
                    "ocr_success": True,
                    "engine": "pytesseract"
                }
            except Exception as e:
                log_warning(f"pytesseract extraction failed on {image_path}: {e}")

        # Graceful fallback: inspect image dimensions and flag as scanned blueprint
        try:
            with Image.open(image_path) as img:
                w, h = img.size
                format_name = img.format
            return {
                "text": "",
                "word_count": 0,
                "ocr_success": False,
                "engine": "image_metadata_fallback",
                "notice": "Scanned or vector blueprint image detected. Visual plan review recommended.",
                "dimensions": {"width": w, "height": h, "format": format_name}
            }
        except Exception as e:
            return {
                "text": "",
                "word_count": 0,
                "ocr_success": False,
                "error": str(e)
            }

ocr_processor = OCRProcessor()

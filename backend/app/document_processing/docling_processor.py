import os
from typing import Dict, Any, Optional
from app.core.logging import log_info, log_warning

# Try importing docling
HAVE_DOCLING = False
try:
    from docling.document_converter import DocumentConverter
    HAVE_DOCLING = True
except (ImportError, Exception) as e:
    log_info(f"Docling library not installed or initialized ({e}). Using PyMuPDF/pypdf primary extraction pipeline.")

class DoclingProcessor:
    def __init__(self):
        self.available = HAVE_DOCLING
        self._converter = None
        if self.available:
            try:
                self._converter = DocumentConverter()
            except Exception as e:
                log_warning(f"Failed to instantiate DocumentConverter: {e}")
                self.available = False

    def is_available(self) -> bool:
        return self.available

    def process_document(self, file_path: str) -> Optional[Dict[str, Any]]:
        """
        Parses document using Docling layout analysis when available.
        Returns extracted markdown, structured tables, and layout blocks.
        """
        if not self.available or not self._converter:
            return None

        try:
            log_info(f"Processing {file_path} with Docling...")
            result = self._converter.convert(file_path)
            doc_dict = result.document.export_to_dict()
            markdown_content = result.document.export_to_markdown()

            return {
                "engine": "docling",
                "markdown": markdown_content,
                "tables": [t for t in doc_dict.get("tables", [])],
                "headings": [h for h in doc_dict.get("texts", []) if h.get("label") in ("heading", "title")],
                "raw_metadata": doc_dict.get("metadata", {})
            }
        except Exception as e:
            log_warning(f"Docling extraction failed for {file_path}: {e}")
            return None

docling_processor = DoclingProcessor()

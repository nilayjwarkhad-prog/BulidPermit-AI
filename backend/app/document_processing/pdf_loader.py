import os
import re
from typing import Dict, Any, List, Optional
from PIL import Image, ImageDraw, ImageFont
from app.core.logging import log_info, log_warning, log_error

# Try importing fitz (PyMuPDF)
HAVE_PYMUPDF = False
try:
    import pymupdf as fitz
    HAVE_PYMUPDF = True
except (ImportError, Exception) as e:
    log_warning(f"PyMuPDF C-extension unavailable ({e}). Using pure-Python pypdf engine.")

import pypdf

class EncryptedPDFError(ValueError):
    """Raised when a PDF is password-protected or encrypted."""
    pass

class CorruptPDFError(ValueError):
    """Raised when a PDF is damaged, corrupt, or unreadable."""
    pass

def extract_document_content(file_path: str, mime_type: str = "application/pdf") -> Dict[str, Any]:
    """
    Extracts text, page count, and layout metadata from PDF or image files.
    Works with PyMuPDF when available, or pypdf/Pillow fallback.
    """
    if mime_type.startswith("image/"):
        return _extract_image_content(file_path)
    return _extract_pdf_content(file_path)

def _extract_pdf_content(file_path: str) -> Dict[str, Any]:
    pages_data: List[Dict[str, Any]] = []
    full_text_parts: List[str] = []
    engine_used = "pypdf"

    # Attempt PyMuPDF first if enabled
    if HAVE_PYMUPDF:
        try:
            doc = fitz.open(file_path)
            if getattr(doc, "is_encrypted", False) or getattr(doc, "needs_pass", False):
                doc.close()
                raise EncryptedPDFError("Document is password-protected or encrypted. Please upload an unencrypted PDF for permit pre-checking.")
            engine_used = "pymupdf"
            page_count = len(doc)
            for page_idx in range(page_count):
                page = doc[page_idx]
                text = page.get_text("text") or ""
                lines = [line.strip() for line in text.split("\n") if line.strip()]
                words = text.split()
                
                # Check for blocks
                blocks = page.get_text("blocks") or []
                
                pages_data.append({
                    "page_number": page_idx + 1,
                    "text": text,
                    "word_count": len(words),
                    "line_count": len(lines),
                    "lines": lines[:50],  # first 50 lines for preview
                    "is_empty": len(words) < 5,
                    "block_count": len(blocks),
                    "dimensions": {"width": page.rect.width, "height": page.rect.height}
                })
                full_text_parts.append(text)
            
            doc.close()
            return {
                "page_count": page_count,
                "engine": engine_used,
                "pages": pages_data,
                "full_text": "\n\n".join(full_text_parts),
                "is_scanned": all(p["word_count"] < 10 for p in pages_data) and page_count > 0
            }
        except EncryptedPDFError as epfe:
            raise epfe
        except Exception as e:
            log_warning(f"PyMuPDF extraction failed for {file_path}: {e}. Falling back to pypdf.")

    # Pure-Python fallback using pypdf
    try:
        reader = pypdf.PdfReader(file_path)
        if getattr(reader, "is_encrypted", False):
            raise EncryptedPDFError("Document is password-protected or encrypted. Please upload an unencrypted PDF for permit pre-checking.")
        page_count = len(reader.pages)
        for page_idx, page in enumerate(reader.pages):
            try:
                text = page.extract_text() or ""
            except (pypdf.errors.FileNotDecryptedError, pypdf.errors.WrongPasswordError):
                raise EncryptedPDFError("Document is password-protected or encrypted. Please upload an unencrypted PDF for permit pre-checking.")
            except Exception:
                text = ""
            lines = [line.strip() for line in text.split("\n") if line.strip()]
            words = text.split()
            
            pages_data.append({
                "page_number": page_idx + 1,
                "text": text,
                "word_count": len(words),
                "line_count": len(lines),
                "lines": lines[:50],
                "is_empty": len(words) < 5,
                "block_count": len(lines),
                "dimensions": {
                    "width": float(page.mediabox.width) if hasattr(page, "mediabox") else 612.0,
                    "height": float(page.mediabox.height) if hasattr(page, "mediabox") else 792.0
                }
            })
            full_text_parts.append(text)

        return {
            "page_count": page_count,
            "engine": "pypdf",
            "pages": pages_data,
            "full_text": "\n\n".join(full_text_parts),
            "is_scanned": all(p["word_count"] < 10 for p in pages_data) and page_count > 0
        }
    except EncryptedPDFError as epfe:
        raise epfe
    except (pypdf.errors.FileNotDecryptedError, pypdf.errors.WrongPasswordError):
        raise EncryptedPDFError("Document is password-protected or encrypted. Please upload an unencrypted PDF for permit pre-checking.")
    except (pypdf.errors.PdfReadError, pypdf.errors.PdfStreamError, pypdf.errors.EmptyFileError) as pre:
        log_error(f"Failed to parse corrupt PDF with pypdf: {pre}")
        raise CorruptPDFError(f"Corrupt or unreadable PDF document: {pre}")
    except ValueError as ve:
        raise ve
    except Exception as e:
        log_error(f"Failed to parse PDF with pypdf: {e}")
        raise CorruptPDFError(f"Corrupt or unreadable PDF document: {e}")

def _extract_image_content(file_path: str) -> Dict[str, Any]:
    """Extracts metadata and text from architectural plan image using OCR / metadata fallback."""
    try:
        from app.document_processing.ocr_processor import ocr_processor
        with Image.open(file_path) as img:
            width, height = img.size
            mode = img.mode
            format_name = img.format
        
        # Try OCR if image
        ocr_result = ocr_processor.process_scanned_image(file_path)
        text = ocr_result.get("text", "")
        lines = [line.strip() for line in text.splitlines() if line.strip()]
        words = text.split()
        
        return {
            "page_count": 1,
            "engine": ocr_result.get("engine", "pillow"),
            "pages": [{
                "page_number": 1,
                "text": text,
                "word_count": len(words),
                "line_count": len(lines),
                "lines": lines[:50],
                "is_empty": len(words) < 5,
                "dimensions": {"width": width, "height": height, "format": format_name, "mode": mode}
            }],
            "full_text": text,
            "is_scanned": True,
            "ocr_metadata": ocr_result
        }
    except Exception as e:
        log_error(f"Failed to read image {file_path}: {e}")
        raise ValueError(f"Corrupt or unsupported image file: {e}")

def render_page_preview(file_path: str, page_number: int, output_image_path: str, mime_type: str = "application/pdf") -> bool:
    """
    Renders a page of the document into a high-res PNG preview for web display.
    """
    try:
        os.makedirs(os.path.dirname(output_image_path), exist_ok=True)
        
        if mime_type.startswith("image/"):
            # Copy or convert image
            with Image.open(file_path) as img:
                img.convert("RGB").save(output_image_path, "PNG")
            return True

        if HAVE_PYMUPDF:
            try:
                doc = fitz.open(file_path)
                if 1 <= page_number <= len(doc):
                    page = doc[page_number - 1]
                    pix = page.get_pixmap(dpi=150)
                    pix.save(output_image_path)
                    doc.close()
                    return True
                doc.close()
            except Exception as e:
                log_warning(f"PyMuPDF rendering failed: {e}")

        # Fallback: Generate a crisp preview card representing the page text
        doc_content = _extract_pdf_content(file_path)
        pages = doc_content.get("pages", [])
        page_data = next((p for p in pages if p["page_number"] == page_number), None)
        
        # Create thumbnail canvas
        w, h = 800, 1100
        canvas = Image.new("RGB", (w, h), color="#FFFFFF")
        draw = ImageDraw.Draw(canvas)
        
        # Draw header border
        draw.rectangle([20, 20, w - 20, h - 20], outline="#CBD5E1", width=2)
        draw.rectangle([20, 20, w - 20, 80], fill="#F8FAFC", outline="#CBD5E1", width=2)
        
        header_text = f"BUILDPERMIT AI PREVIEW - PAGE {page_number}"
        draw.text((40, 42), header_text, fill="#1E293B")
        
        if page_data and page_data.get("lines"):
            y = 100
            for line in page_data["lines"][:40]:
                truncated = line[:90] + ("..." if len(line) > 90 else "")
                draw.text((40, y), truncated, fill="#334155")
                y += 22
        else:
            draw.text((40, 200), "[Visual Architectural Drawing Page - View in Full PDF Viewer]", fill="#64748B")
            draw.rectangle([80, 260, w - 80, h - 100], outline="#E2E8F0", fill="#F1F5F9", width=1)
            draw.text((120, 320), "Architectural Blueprint / CAD Vector Content", fill="#94A3B8")
            
        canvas.save(output_image_path, "PNG")
        return True
    except Exception as e:
        log_error(f"Error rendering page preview: {e}")
        return False

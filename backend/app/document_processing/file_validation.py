import os
from typing import Tuple

ALLOWED_EXTENSIONS = {".pdf", ".png", ".jpg", ".jpeg"}
ALLOWED_MIME_TYPES = {
    "application/pdf",
    "image/png",
    "image/jpeg",
    "image/pjpeg"
}

# Magic signatures (first bytes)
MAGIC_SIGNATURES = {
    b"%PDF": "application/pdf",
    b"\x89PNG\r\n\x1a\n": "image/png",
    b"\xff\xd8\xff": "image/jpeg"
}

def validate_uploaded_file(file_bytes: bytes, filename: str, max_size_bytes: int = 50 * 1024 * 1024) -> Tuple[bool, str, str]:
    """
    Validates uploaded file against security checks:
    - Path traversal
    - File size limits
    - Allowed extension
    - File magic signature (magic bytes)
    Returns (is_valid, detected_mime, error_message)
    """
    if not filename or ".." in filename or "/" in filename or "\\" in filename:
        return False, "", "Invalid filename or potential path traversal attempt"

    if len(file_bytes) == 0:
        return False, "", "File is empty"

    if len(file_bytes) > max_size_bytes:
        return False, "", f"File exceeds maximum allowed size ({max_size_bytes // (1024 * 1024)} MB)"

    _, ext = os.path.splitext(filename.lower())
    if ext not in ALLOWED_EXTENSIONS:
        return False, "", f"Unsupported file extension '{ext}'. Allowed: {', '.join(ALLOWED_EXTENSIONS)}"

    # Check magic signature
    detected_mime = None
    if file_bytes.startswith(b"%PDF"):
        detected_mime = "application/pdf"
    elif file_bytes.startswith(b"\x89PNG\r\n\x1a\n"):
        detected_mime = "image/png"
    elif file_bytes.startswith(b"\xff\xd8\xff"):
        detected_mime = "image/jpeg"

    if not detected_mime:
        return False, "", "File content signature does not match valid PDF, PNG, or JPEG header"

    if detected_mime not in ALLOWED_MIME_TYPES:
        return False, "", f"Disallowed MIME type: {detected_mime}"

    return True, detected_mime, ""

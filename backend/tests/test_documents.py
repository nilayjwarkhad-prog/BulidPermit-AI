import io
from app.document_processing.file_validation import validate_uploaded_file

def test_file_validation_rejects_invalid_file_types():
    # Empty bytes
    valid, _, err = validate_uploaded_file(b"", "plan.pdf")
    assert not valid
    assert "empty" in err.lower()

    # Disallowed extension
    valid, _, err = validate_uploaded_file(b"content", "script.exe")
    assert not valid
    assert "unsupported" in err.lower()

    # Invalid header signature (claims to be PDF but is plain text)
    valid, _, err = validate_uploaded_file(b"This is just text", "fake.pdf")
    assert not valid
    assert "signature" in err.lower()

    # Path traversal attempt
    valid, _, err = validate_uploaded_file(b"%PDF-1.4", "../etc/passwd.pdf")
    assert not valid
    assert "traversal" in err.lower()

def test_file_validation_accepts_valid_pdf_signature():
    valid_pdf_bytes = b"%PDF-1.4\n1 0 obj\n<<>>\nendobj\ntrailer\n<<>>\n%%EOF"
    valid, mime, err = validate_uploaded_file(valid_pdf_bytes, "valid_plan.pdf")
    assert valid
    assert mime == "application/pdf"
    assert err == ""

def test_upload_encrypted_pdf_cleans_up_and_returns_400(client, auth_headers):
    # Create project first
    proj_res = client.post("/api/v1/projects", json={
        "name": "Encrypted Test Project",
        "address": "124 Elm St",
        "city": "Springfield",
        "state_region": "CA"
    }, headers=auth_headers)
    assert proj_res.status_code == 201
    project_id = proj_res.json()["id"]

    # Create encrypted synthetic PDF bytes
    import pypdf
    writer = pypdf.PdfWriter()
    writer.add_blank_page(width=100, height=100)
    writer.encrypt("topsecret123")
    buf = io.BytesIO()
    writer.write(buf)
    enc_bytes = buf.getvalue()

    res = client.post(
        f"/api/v1/projects/{project_id}/documents",
        files={"file": ("locked.pdf", enc_bytes, "application/pdf")},
        data={"category": "Permit Application"},
        headers=auth_headers
    )
    assert res.status_code == 400
    assert "password-protected or encrypted" in res.json()["detail"].lower()
    
    # Verify no documents were stored in DB
    list_res = client.get(f"/api/v1/projects/{project_id}/documents", headers=auth_headers)
    assert len(list_res.json()) == 0

def test_upload_corrupt_pdf_cleans_up_and_returns_400(client, auth_headers):
    # Create project first
    proj_res = client.post("/api/v1/projects", json={
        "name": "Corrupt Test Project",
        "address": "124 Elm St",
        "city": "Springfield",
        "state_region": "CA"
    }, headers=auth_headers)
    assert proj_res.status_code == 201
    project_id = proj_res.json()["id"]

    corrupt_bytes = b"%PDF-1.4\nBroken binary payload with missing xref and dictionary%%EOF"
    res = client.post(
        f"/api/v1/projects/{project_id}/documents",
        files={"file": ("corrupt.pdf", corrupt_bytes, "application/pdf")},
        data={"category": "Permit Application"},
        headers=auth_headers
    )
    assert res.status_code == 400
    detail = res.json()["detail"].lower()
    assert "corrupt or unreadable" in detail
    assert "password" not in detail
    assert "encrypted" not in detail

    # Verify no documents were stored in DB
    list_res = client.get(f"/api/v1/projects/{project_id}/documents", headers=auth_headers)
    assert len(list_res.json()) == 0

def _create_test_project_and_pdf(client, auth_headers):
    """Helper to create a test project and upload a valid PDF document."""
    from reportlab.pdfgen import canvas
    buf = io.BytesIO()
    c = canvas.Canvas(buf)
    c.drawString(72, 700, "Permit Submittal - Architectural Plans Sheet A-101")
    c.showPage()
    c.save()
    pdf_bytes = buf.getvalue()

    proj_res = client.post("/api/v1/projects", json={
        "name": "Auth Download Test Project",
        "address": "456 Test Way",
        "city": "Springfield",
        "state_region": "CA"
    }, headers=auth_headers)
    assert proj_res.status_code == 201
    project_id = proj_res.json()["id"]

    upload_res = client.post(
        f"/api/v1/projects/{project_id}/documents",
        files={"file": ("blueprint.pdf", pdf_bytes, "application/pdf")},
        data={"category": "Floor Plan"},
        headers=auth_headers
    )
    assert upload_res.status_code == 201
    doc_id = upload_res.json()["id"]

    return project_id, doc_id, pdf_bytes

def test_authenticated_download_document_bearer_header(client, auth_headers):
    """Authenticated user downloads their document using standard Bearer header."""
    project_id, doc_id, original_bytes = _create_test_project_and_pdf(client, auth_headers)

    res = client.get(f"/api/v1/documents/{doc_id}/download", headers=auth_headers)
    assert res.status_code == 200
    assert "application/pdf" in res.headers["content-type"]
    assert res.content == original_bytes
    assert "blueprint.pdf" in res.headers.get("content-disposition", "")

def test_authenticated_download_document_query_token(client, auth_headers):
    """Authenticated user downloads their document using query parameter token."""
    project_id, doc_id, original_bytes = _create_test_project_and_pdf(client, auth_headers)
    token = auth_headers["Authorization"].split()[1]

    # No Authorization header passed, only query param
    res = client.get(f"/api/v1/documents/{doc_id}/download?token={token}")
    assert res.status_code == 200
    assert "application/pdf" in res.headers["content-type"]
    assert res.content == original_bytes

def test_unauthenticated_download_document_fails_401(client, auth_headers):
    """Attempting download with no token or credentials returns 401 Unauthorized."""
    project_id, doc_id, _ = _create_test_project_and_pdf(client, auth_headers)

    res = client.get(f"/api/v1/documents/{doc_id}/download")
    assert res.status_code == 401
    assert res.json()["detail"] == "Authentication credentials were not provided"

def test_invalid_token_download_document_fails_401(client, auth_headers):
    """Attempting download with malformed/expired token returns 401 Unauthorized."""
    project_id, doc_id, _ = _create_test_project_and_pdf(client, auth_headers)

    res = client.get(f"/api/v1/documents/{doc_id}/download?token=invalid.jwt.token")
    assert res.status_code == 401
    assert "Invalid or expired" in res.json()["detail"]

def test_unauthorized_user_download_document_fails_403(client, auth_headers):
    """A different user (User B) cannot download User A's document (returns 403 Forbidden)."""
    project_id, doc_id, _ = _create_test_project_and_pdf(client, auth_headers)

    # Register User B
    res_b = client.post("/api/v1/auth/register", json={
        "email": "user_b@example.com",
        "password": "Password123!",
        "full_name": "User B",
        "role": "contractor"
    })
    assert res_b.status_code == 201
    token_b = res_b.json()["access_token"]
    headers_b = {"Authorization": f"Bearer {token_b}"}

    # User B attempts download with Bearer header
    forbidden_header_res = client.get(f"/api/v1/documents/{doc_id}/download", headers=headers_b)
    assert forbidden_header_res.status_code == 403
    assert forbidden_header_res.json()["detail"] == "Forbidden"

    # User B attempts download with query token
    forbidden_query_res = client.get(f"/api/v1/documents/{doc_id}/download?token={token_b}")
    assert forbidden_query_res.status_code == 403
    assert forbidden_query_res.json()["detail"] == "Forbidden"

def test_document_preview_authentication_and_authorization(client, auth_headers):
    """Document preview respects authentication, query tokens, and 403 forbidden checks."""
    project_id, doc_id, _ = _create_test_project_and_pdf(client, auth_headers)
    token = auth_headers["Authorization"].split()[1]

    # Unauthenticated preview fails with 401
    unauth_prev = client.get(f"/api/v1/documents/{doc_id}/preview/1")
    assert unauth_prev.status_code == 401
    assert unauth_prev.json()["detail"] == "Authentication credentials were not provided"

    # User B preview fails with 403
    res_b = client.post("/api/v1/auth/register", json={
        "email": "preview_user_b@example.com",
        "password": "Password123!",
        "full_name": "Preview User B",
        "role": "contractor"
    })
    token_b = res_b.json()["access_token"]
    forbidden_prev = client.get(f"/api/v1/documents/{doc_id}/preview/1?token={token_b}")
    assert forbidden_prev.status_code == 403

    # Authenticated user can request preview (either returns 200 image/png or 404 if preview render isn't generated)
    auth_prev = client.get(f"/api/v1/documents/{doc_id}/preview/1?token={token}")
    assert auth_prev.status_code in (200, 404)

def test_report_download_authentication_and_authorization(client, auth_headers):
    """Report PDF download respects Bearer auth, query token, 401 unauthenticated, and 403 unauthorized."""
    project_id, doc_id, _ = _create_test_project_and_pdf(client, auth_headers)
    token = auth_headers["Authorization"].split()[1]

    # Generate a report for this project
    rep_res = client.post(f"/api/v1/projects/{project_id}/reports", headers=auth_headers)
    assert rep_res.status_code == 201
    report_id = rep_res.json()["id"]

    # 1. Authenticated download with Bearer header -> 200
    res_hdr = client.get(f"/api/v1/reports/{report_id}/download", headers=auth_headers)
    assert res_hdr.status_code == 200
    assert "application/pdf" in res_hdr.headers["content-type"]
    assert len(res_hdr.content) > 0

    # 2. Authenticated download with query token -> 200
    res_qry = client.get(f"/api/v1/reports/{report_id}/download?token={token}")
    assert res_qry.status_code == 200
    assert "application/pdf" in res_qry.headers["content-type"]
    assert res_qry.content == res_hdr.content

    # 3. Unauthenticated download -> 401
    res_unauth = client.get(f"/api/v1/reports/{report_id}/download")
    assert res_unauth.status_code == 401

    # 4. Unauthorized User B -> 403
    res_b = client.post("/api/v1/auth/register", json={
        "email": "report_user_b@example.com",
        "password": "Password123!",
        "full_name": "Report User B",
        "role": "contractor"
    })
    token_b = res_b.json()["access_token"]
    res_b_hdr = client.get(f"/api/v1/reports/{report_id}/download", headers={"Authorization": f"Bearer {token_b}"})
    assert res_b_hdr.status_code == 403
    res_b_qry = client.get(f"/api/v1/reports/{report_id}/download?token={token_b}")
    assert res_b_qry.status_code == 403


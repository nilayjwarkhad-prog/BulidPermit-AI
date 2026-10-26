import pytest
from app.db.session import SessionLocal
from app.models.user import User
from app.models.project import Project
from app.models.analysis import AnalysisJob
from app.models.finding import Finding
from app.models.checklist import Checklist, ChecklistItem
from app.services.analysis_service import execute_project_analysis

@pytest.mark.asyncio
async def test_end_to_end_analysis_pipeline(client, auth_headers, db_session):
    # 1. Create a project
    create_res = client.post("/api/v1/projects", json={
        "name": "End-to-End Test Residence",
        "description": "Integration test project",
        "country": "United States",
        "state_region": "California",
        "city": "Springfield",
        "address": "124 Elm Street, Springfield, CA 90210",
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

    # 2. Seed sample documents (including the inconsistent one)
    seed_res = client.post(f"/api/v1/projects/{proj_id}/seed_sample_documents?include_inconsistency=true", headers=auth_headers)
    assert seed_res.status_code == 200
    docs = seed_res.json()
    assert len(docs) >= 3

    # 3. Trigger analysis
    db = db_session
    try:
        job = AnalysisJob(
            project_id=proj_id,
            status="pending",
            current_step="Starting",
            total_steps=9,
            progress_percentage=0.0
        )
        db.add(job)
        db.commit()
        db.refresh(job)

        # Run analysis pipeline
        await execute_project_analysis(job.id, db)

        # Verify job completed
        db.refresh(job)
        assert job.status == "completed"
        assert job.progress_percentage == 100.0

        # Verify findings generated
        findings = db.query(Finding).filter(Finding.project_id == proj_id).all()
        assert len(findings) > 0
        
        # Check that address mismatch was flagged
        has_addr_mismatch = any(f.rule_code == "CROSS-DOC-ADDR-MISMATCH" for f in findings)
        assert has_addr_mismatch, "Should flag the address mismatch between 124 Elm St and 142 Elm St"

        # Check that checklist was populated
        chk = db.query(Checklist).filter(Checklist.project_id == proj_id).first()
        assert chk is not None
        items = db.query(ChecklistItem).filter(ChecklistItem.checklist_id == chk.id).all()
        assert len(items) >= 5
    finally:
        pass

    # 4. Generate PDF Report via API
    rep_res = client.post(f"/api/v1/projects/{proj_id}/reports", headers=auth_headers)
    assert rep_res.status_code == 201
    rep_data = rep_res.json()
    assert rep_data["report_number"].startswith("BPAI-")

    # Download report
    dl_res = client.get(f"/api/v1/reports/{rep_data['id']}/download", headers=auth_headers)
    assert dl_res.status_code == 200
    assert dl_res.headers["content-type"] == "application/pdf"
    assert len(dl_res.content) > 1000

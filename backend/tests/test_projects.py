def test_project_crud_and_ownership(client, auth_headers):
    # Create project
    create_res = client.post("/api/v1/projects", json={
        "name": "Oak Street Master Suite Addition",
        "description": "450 sq ft master bedroom addition",
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
    proj_data = create_res.json()
    proj_id = proj_data["id"]
    assert proj_data["name"] == "Oak Street Master Suite Addition"
    assert proj_data["jurisdiction_supported"] == "supported"

    # List projects
    list_res = client.get("/api/v1/projects", headers=auth_headers)
    assert list_res.status_code == 200
    assert len(list_res.json()) >= 1

    # Get single project
    get_res = client.get(f"/api/v1/projects/{proj_id}", headers=auth_headers)
    assert get_res.status_code == 200

    # Unauthorized access by second user
    second_user_res = client.post("/api/v1/auth/register", json={
        "email": "intruder@example.com",
        "password": "Password123!"
    })
    second_token = second_user_res.json()["access_token"]
    forbidden_res = client.get(f"/api/v1/projects/{proj_id}", headers={"Authorization": f"Bearer {second_token}"})
    assert forbidden_res.status_code == 403

    # Delete project
    del_res = client.delete(f"/api/v1/projects/{proj_id}", headers=auth_headers)
    assert del_res.status_code == 204

def test_register_and_login(client):
    # Register
    reg_res = client.post("/api/v1/auth/register", json={
        "email": "architect@buildpermit.ai",
        "password": "SecurePassword123!",
        "full_name": "Jane Architect",
        "role": "architect"
    })
    assert reg_res.status_code == 201
    data = reg_res.json()
    assert "access_token" in data
    assert data["user"]["email"] == "architect@buildpermit.ai"

    # Duplicate registration
    dup_res = client.post("/api/v1/auth/register", json={
        "email": "architect@buildpermit.ai",
        "password": "SecurePassword123!"
    })
    assert dup_res.status_code == 400

    # Login
    login_res = client.post("/api/v1/auth/login", json={
        "email": "architect@buildpermit.ai",
        "password": "SecurePassword123!"
    })
    assert login_res.status_code == 200
    token = login_res.json()["access_token"]

    # Access /me
    me_res = client.get("/api/v1/auth/me", headers={"Authorization": f"Bearer {token}"})
    assert me_res.status_code == 200
    assert me_res.json()["full_name"] == "Jane Architect"

def test_login_invalid_password(client):
    res = client.post("/api/v1/auth/login", json={
        "email": "architect@buildpermit.ai",
        "password": "WrongPassword!"
    })
    assert res.status_code == 401

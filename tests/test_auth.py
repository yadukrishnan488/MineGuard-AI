from tests.conftest import auth_header


def test_login_success(client, seed_test_context):
    response = client.post(
        "/api/v1/auth/login",
        json={"email": "test_admin@mineguard.gov.in", "password": "Pass@123"},
    )
    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    assert "refresh_token" in data
    assert data["token_type"] == "bearer"
    assert data["user"]["email"] == "test_admin@mineguard.gov.in"
    assert data["user"]["role"] == "SYSTEM_ADMIN"


def test_login_invalid_password(client, seed_test_context):
    response = client.post(
        "/api/v1/auth/login",
        json={"email": "test_admin@mineguard.gov.in", "password": "WrongPassword"},
    )
    assert response.status_code == 401
    assert "Incorrect email or password" in response.json()["detail"]


def test_login_nonexistent_user(client, seed_test_context):
    response = client.post(
        "/api/v1/auth/login",
        json={"email": "nonexistent@mineguard.gov.in", "password": "Pass@123"},
    )
    assert response.status_code == 401


def test_auth_me(client, seed_test_context):
    worker = seed_test_context["worker_1"]
    headers = auth_header(worker)

    # Authorized request
    res = client.get("/api/v1/auth/me", headers=headers)
    assert res.status_code == 200
    assert res.json()["email"] == worker.email

    # Unauthorized request
    res_unauth = client.get("/api/v1/auth/me")
    assert res_unauth.status_code == 401


def test_refresh_token_rotation(client, seed_test_context):
    # First login to obtain refresh token
    login_res = client.post(
        "/api/v1/auth/login",
        json={"email": "test_worker1@mineguard.gov.in", "password": "Pass@123"},
    )
    assert login_res.status_code == 200
    refresh_tok = login_res.json()["refresh_token"]

    # Use refresh token to obtain new tokens
    refresh_res = client.post(
        "/api/v1/auth/refresh",
        json={"refresh_token": refresh_tok},
    )
    assert refresh_res.status_code == 200
    new_data = refresh_res.json()
    assert "access_token" in new_data
    assert "refresh_token" in new_data
    assert new_data["refresh_token"] != refresh_tok

    # Attempting to reuse the old refresh token should be rejected (revoked!)
    reuse_res = client.post(
        "/api/v1/auth/refresh",
        json={"refresh_token": refresh_tok},
    )
    assert reuse_res.status_code == 401
    assert "revoked" in reuse_res.json()["detail"].lower()


def test_user_registration(client, seed_test_context):
    org = seed_test_context["org"]
    new_user_payload = {
        "email": "new_mechanic@mineguard.gov.in",
        "password": "Password@123",
        "full_name": "Deepak Hansda",
        "role": "WORKER",
        "organization_id": org.id,
        "worker_profile": {
            "employee_id": "EMP-9901",
            "trade": "Excavator Operator",
            "blood_group": "O+",
        },
    }
    res = client.post("/api/v1/auth/register", json=new_user_payload)
    assert res.status_code == 201
    data = res.json()
    assert data["email"] == "new_mechanic@mineguard.gov.in"
    assert data["worker_profile"]["employee_id"] == "EMP-9901"

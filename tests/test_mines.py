from tests.conftest import auth_header


def test_list_and_get_mines(client, seed_test_context):
    mine_a = seed_test_context["mine_a"]
    res = client.get("/api/v1/mines")
    assert res.status_code == 200
    mines = res.json()
    assert len(mines) >= 2

    # Get single mine
    res_single = client.get(f"/api/v1/mines/{mine_a.id}")
    assert res_single.status_code == 200
    assert res_single.json()["name"] == mine_a.name


def test_mine_subsidence_endpoint(client, seed_test_context):
    mine_a = seed_test_context["mine_a"]
    admin = seed_test_context["admin"]
    res = client.get(f"/api/v1/mines/{mine_a.id}/subsidence", headers=auth_header(admin))
    assert res.status_code == 200
    data = res.json()
    assert data["mine_id"] == mine_a.id
    assert "subsidence_rate_mm_year" in data
    assert "hotspots" in data
    assert len(data["hotspots"]) >= 1


def test_mine_creation_rbac(client, seed_test_context):
    sub = seed_test_context["sub"]
    admin = seed_test_context["admin"]
    worker = seed_test_context["worker_1"]

    payload = {
        "subsidiary_id": sub.id,
        "name": "North Quarry Pit",
        "code": "TEST-NQP-09",
        "location_name": "Ranchi",
        "mine_type": "OPEN_CAST",
        "status": "ACTIVE",
    }

    # Worker role should be denied (403 Forbidden)
    res_worker = client.post("/api/v1/mines", json=payload, headers=auth_header(worker))
    assert res_worker.status_code == 403

    # System Admin should succeed (201 Created)
    res_admin = client.post("/api/v1/mines", json=payload, headers=auth_header(admin))
    assert res_admin.status_code == 201
    assert res_admin.json()["name"] == "North Quarry Pit"


def test_mine_access_isolation(client, seed_test_context):
    mine_b = seed_test_context["mine_b"]
    mgr_a = seed_test_context["mgr_a"]  # Assigned to Mine A

    # Manager of Mine A attempting to access subsidence of Mine B
    res = client.get(f"/api/v1/mines/{mine_b.id}/subsidence", headers=auth_header(mgr_a))
    assert res.status_code == 403
    assert "forbidden" in res.json()["detail"].lower()

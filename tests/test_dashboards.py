from tests.conftest import auth_header


def test_worker_dashboard(client, seed_test_context):
    worker = seed_test_context["worker_1"]
    res = client.get("/api/v1/dashboard/worker", headers=auth_header(worker))
    assert res.status_code == 200
    data = res.json()
    assert data["worker_id"] == worker.id
    assert "open_grievances_count" in data
    assert "active_mine_safety_alerts" in data


def test_mine_dashboard(client, seed_test_context):
    mgr_a = seed_test_context["mgr_a"]
    mine_a = seed_test_context["mine_a"]
    res = client.get(f"/api/v1/dashboard/mine?mine_id={mine_a.id}", headers=auth_header(mgr_a))
    assert res.status_code == 200
    data = res.json()
    assert data["mine_id"] == mine_a.id
    assert "current_risk_score" in data
    assert "current_risk_level" in data
    assert "compliance_score_pct" in data


def test_corporate_dashboard(client, seed_test_context):
    corp = seed_test_context["corp"]
    worker = seed_test_context["worker_1"]

    # Worker trying to access corporate dashboard -> 403 Forbidden
    unauth_res = client.get("/api/v1/dashboard/corporate", headers=auth_header(worker))
    assert unauth_res.status_code == 403

    # Corporate Admin -> 200 OK
    res = client.get("/api/v1/dashboard/corporate", headers=auth_header(corp))
    assert res.status_code == 200
    data = res.json()
    assert data["total_mines"] >= 2
    assert "average_compliance_pct" in data
    assert "recurring_violations_by_category" in data

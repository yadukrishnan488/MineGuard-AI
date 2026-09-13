from tests.conftest import auth_header


def test_grievance_submission_and_privacy_isolation(client, seed_test_context):
    worker_1 = seed_test_context["worker_1"]
    worker_2 = seed_test_context["worker_2"]
    mgr_a = seed_test_context["mgr_a"]
    mine_a = seed_test_context["mine_a"]

    # 1. Worker 1 submits a confidential grievance
    payload = {
        "mine_id": mine_a.id,
        "category": "WORKPLACE_SAFETY",
        "description": "Loose boulder above conveyor gallery #3 needs immediate scaling.",
        "priority": "HIGH",
        "is_confidential": True,
    }
    res = client.post("/api/v1/grievances", json=payload, headers=auth_header(worker_1))
    assert res.status_code == 201
    data = res.json()
    grv_id = data["id"]
    assert data["complaint_reference"].startswith("MG-GRV-")
    assert data["worker_id"] == worker_1.id

    # 2. Worker 1 can view their own complaint via /my
    my_res = client.get("/api/v1/grievances/my", headers=auth_header(worker_1))
    assert my_res.status_code == 200
    my_list = my_res.json()
    assert any(g["id"] == grv_id for g in my_list)

    # 3. Privacy Enforcement: Worker 2 tries to access Worker 1's grievance -> 403 Forbidden!
    unauth_res = client.get(f"/api/v1/grievances/{grv_id}", headers=auth_header(worker_2))
    assert unauth_res.status_code == 403
    assert "cannot view this grievance" in unauth_res.json()["detail"].lower()

    # 4. Mine Manager updates status
    status_payload = {
        "status": "RESOLVED",
        "assigned_officer_id": mgr_a.id,
        "resolution_notes": "Scaling team deployed and gallery cleared of loose boulders.",
    }
    mgr_res = client.patch(f"/api/v1/grievances/{grv_id}/status", json=status_payload, headers=auth_header(mgr_a))
    assert mgr_res.status_code == 200
    assert mgr_res.json()["status"] == "RESOLVED"
    assert mgr_res.json()["resolved_at"] is not None

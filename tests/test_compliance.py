from datetime import date, timedelta
from tests.conftest import auth_header


def test_compliance_lifecycle(client, seed_test_context):
    admin = seed_test_context["admin"]
    mgr_a = seed_test_context["mgr_a"]
    mine_a = seed_test_context["mine_a"]

    # 1. Create requirement
    req_payload = {
        "title": "Quarterly Water Discharge Testing",
        "category": "ENVIRONMENT",
        "description": "Biological oxygen demand and pH testing of mine sumps.",
        "statutory_act": "Water Act 1974, Section 25",
        "frequency": "QUARTERLY",
    }
    req_res = client.post("/api/v1/compliance/requirements", json=req_payload, headers=auth_header(admin))
    assert req_res.status_code == 201
    req_id = req_res.json()["id"]

    # 2. Link requirement to Mine A
    rec_payload = {
        "requirement_id": req_id,
        "mine_id": mine_a.id,
        "due_date": str(date.today() + timedelta(days=14)),
    }
    rec_res = client.post("/api/v1/compliance", json=rec_payload, headers=auth_header(mgr_a))
    assert rec_res.status_code == 201
    record_id = rec_res.json()["id"]
    assert rec_res.json()["status"] == "PENDING"

    # 3. Update record status to SUBMITTED
    patch_res = client.patch(
        f"/api/v1/compliance/{record_id}",
        json={"status": "SUBMITTED", "review_notes": "Water laboratory report attached."},
        headers=auth_header(mgr_a),
    )
    assert patch_res.status_code == 200
    assert patch_res.json()["status"] == "SUBMITTED"

    # 4. Summary calculation
    summary_res = client.get(f"/api/v1/compliance/summary/{mine_a.id}", headers=auth_header(mgr_a))
    assert summary_res.status_code == 200
    summary = summary_res.json()
    assert summary["mine_id"] == mine_a.id
    assert summary["total_requirements"] >= 1
    assert summary["submitted_count"] >= 1

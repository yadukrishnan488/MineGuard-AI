from datetime import date, timedelta
from tests.conftest import auth_header


def test_inspection_and_observation_workflow(client, seed_test_context):
    insp_a = seed_test_context["insp_a"]
    mine_a = seed_test_context["mine_a"]

    # 1. Create inspection
    insp_payload = {
        "mine_id": mine_a.id,
        "inspection_type": "VENTILATION_AUDIT",
        "latitude": 23.791,
        "longitude": 86.432,
        "summary": "Auxiliary fan velocity testing at Level 2.",
    }
    insp_res = client.post("/api/v1/inspections", json=insp_payload, headers=auth_header(insp_a))
    assert insp_res.status_code == 201
    insp_data = insp_res.json()
    insp_id = insp_data["id"]
    assert insp_data["status"] == "REPORTED"

    # 2. Add high-priority safety observation (triggers immediate alert)
    obs_payload = {
        "mine_id": mine_a.id,
        "title": "Methane Buildup Near Goaf Edge",
        "description": "CH4 level measured at 1.4%, exceeding statutory threshold of 0.8%.",
        "severity": "CRITICAL",
        "category": "GAS_VENTILATION",
        "latitude": 23.7915,
        "longitude": 86.4325,
    }
    obs_res = client.post("/api/v1/inspections/observations/direct", json=obs_payload, headers=auth_header(insp_a))
    assert obs_res.status_code == 201
    obs_id = obs_res.json()["id"]
    assert obs_res.json()["severity"] == "CRITICAL"

    # 3. Create corrective action
    ca_payload = {
        "safety_observation_id": obs_id,
        "inspection_id": insp_id,
        "mine_id": mine_a.id,
        "description": "Isolate power supply and deploy auxiliary booster fan immediately.",
        "due_date": str(date.today() + timedelta(days=1)),
    }
    ca_res = client.post("/api/v1/inspections/corrective-actions", json=ca_payload, headers=auth_header(insp_a))
    assert ca_res.status_code == 201
    ca_id = ca_res.json()["id"]

    # 4. Advance inspection workflow
    update_res = client.patch(
        f"/api/v1/inspections/{insp_id}",
        json={"status": "IN_PROGRESS", "summary": "Remediation team mobilized."},
        headers=auth_header(insp_a),
    )
    assert update_res.status_code == 200
    assert update_res.json()["status"] == "IN_PROGRESS"

    # 5. Resolve corrective action
    ca_update_res = client.patch(
        f"/api/v1/inspections/corrective-actions/{ca_id}",
        json={"status": "COMPLETED", "completion_notes": "CH4 levels restored to 0.2%."},
        headers=auth_header(insp_a),
    )
    assert ca_update_res.status_code == 200
    assert ca_update_res.json()["status"] == "COMPLETED"

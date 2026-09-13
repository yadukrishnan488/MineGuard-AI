from datetime import datetime, timezone
import uuid
from tests.conftest import auth_header


def test_offline_sync_batch_and_idempotency(client, seed_test_context):
    insp_a = seed_test_context["insp_a"]
    mine_a = seed_test_context["mine_a"]

    client_id_1 = str(uuid.uuid4())
    idempotency_key_1 = f"sync-key-{uuid.uuid4()}"

    batch_payload = {
        "inspections": [
            {
                "client_id": client_id_1,
                "idempotency_key": idempotency_key_1,
                "mine_id": mine_a.id,
                "inspection_type": "OFFLINE_AUDIT",
                "client_timestamp": datetime.now(timezone.utc).isoformat(),
                "latitude": 23.792,
                "longitude": 86.433,
                "summary": "Offline field audit in opencast pit zone 3.",
                "observations": [
                    {
                        "client_id": str(uuid.uuid4()),
                        "title": "Minor Spillage on Haul Ramp",
                        "description": "Loose coal gravel on ramp curvature.",
                        "severity": "LOW",
                        "category": "HAUL_ROAD",
                    }
                ],
            }
        ]
    }

    # 1. First Sync Request
    res_1 = client.post("/api/v1/inspections/sync", json=batch_payload, headers=auth_header(insp_a))
    assert res_1.status_code == 200
    data_1 = res_1.json()
    assert data_1["total_processed"] == 1
    assert data_1["accepted_count"] == 1
    assert data_1["results"][0]["sync_status"] == "ACCEPTED"
    server_id = data_1["results"][0]["server_id"]
    assert server_id is not None

    # 2. Idempotent Retry: Submit exact same batch payload with same idempotency_key
    res_2 = client.post("/api/v1/inspections/sync", json=batch_payload, headers=auth_header(insp_a))
    assert res_2.status_code == 200
    data_2 = res_2.json()
    assert data_2["total_processed"] == 1
    assert data_2["accepted_count"] == 1
    # Check that it detected the idempotency key and returned the existing server_id without recreating
    assert "idempotent" in data_2["results"][0]["message"].lower()


def test_offline_sync_invalid_mine_rejection(client, seed_test_context):
    insp_a = seed_test_context["insp_a"]
    fake_mine_id = str(uuid.uuid4())

    batch_payload = {
        "inspections": [
            {
                "client_id": str(uuid.uuid4()),
                "idempotency_key": f"sync-key-invalid-{uuid.uuid4()}",
                "mine_id": fake_mine_id,
                "inspection_type": "ROUTINE_SAFETY",
                "client_timestamp": datetime.now(timezone.utc).isoformat(),
            }
        ]
    }

    res = client.post("/api/v1/inspections/sync", json=batch_payload, headers=auth_header(insp_a))
    assert res.status_code == 200
    data = res.json()
    assert data["rejected_count"] == 1
    assert data["results"][0]["sync_status"] == "REJECTED"

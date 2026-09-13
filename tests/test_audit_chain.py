from tests.conftest import auth_header
from app.models.audit import AuditLog
from app.services.audit_service import AuditService


def test_audit_hash_chain_and_tamper_detection(client, db, seed_test_context):
    admin = seed_test_context["admin"]
    headers = auth_header(admin)

    # 1. Create a few explicit audit entries
    entry1 = AuditService.create_audit_entry(
        db, action="CONFIG_CHANGE", entity_type="SYSTEM", entity_id="cfg_1", actor_id=admin.id, change_metadata={"setting": "auto_alert", "val": True}
    )
    entry2 = AuditService.create_audit_entry(
        db, action="ACCESS_POLICY_UPDATE", entity_type="ROLE", entity_id="role_1", actor_id=admin.id, change_metadata={"scope": "mine_level"}
    )

    # 2. Verify hash linking
    assert entry2.prev_hash == entry1.current_hash

    # 3. Call verify endpoint: Should report 100% verified
    verify_res = client.get("/api/v1/audit/verify", headers=headers)
    assert verify_res.status_code == 200
    assert verify_res.json()["verified"] is True
    assert verify_res.json()["chain_valid"] is True
    assert len(verify_res.json()["tampered_records"]) == 0

    # 4. Tamper Simulation: Directly modify change_metadata of entry1 behind the back of the app
    entry1.change_metadata = '{"setting": "FORGED_UNAUTHORIZED_DATA"}'
    db.commit()

    # 5. Call verify endpoint: Tampering MUST be detected!
    tamper_check_res = client.get("/api/v1/audit/verify", headers=headers)
    assert tamper_check_res.status_code == 200
    tamper_data = tamper_check_res.json()
    assert tamper_data["verified"] is False
    assert len(tamper_data["tampered_records"]) >= 1
    assert "tampering detected" in tamper_data["verification_message"].lower()

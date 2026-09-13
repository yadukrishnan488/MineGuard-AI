import json
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional
from sqlalchemy.orm import Session
from app.core.security import compute_audit_hash
from app.models.audit import AuditLog

GENESIS_HASH = "0" * 64


class AuditService:
    @staticmethod
    def create_audit_entry(
        db: Session,
        action: str,
        entity_type: str,
        entity_id: str,
        actor_id: Optional[str] = None,
        change_metadata: Optional[Dict[str, Any]] = None,
    ) -> AuditLog:
        """
        Append a new tamper-evident audit record to the cryptographic hash chain.
        """
        # Fetch the most recent audit record to obtain prev_hash
        latest_entry = db.query(AuditLog).order_by(AuditLog.timestamp.desc()).first()
        prev_hash = latest_entry.current_hash if latest_entry else GENESIS_HASH

        now_utc = datetime.now(timezone.utc)
        now_iso = now_utc.isoformat()

        # Compute SHA-256 hash binding previous hash and record payload
        current_hash = compute_audit_hash(
            prev_hash=prev_hash,
            actor_id=actor_id,
            action=action,
            entity_type=entity_type,
            entity_id=str(entity_id),
            timestamp_iso=now_iso,
            metadata=change_metadata,
        )

        audit_log = AuditLog(
            actor_id=actor_id,
            action=action,
            entity_type=entity_type,
            entity_id=str(entity_id),
            timestamp=now_utc,
            change_metadata=json.dumps(change_metadata, default=str) if change_metadata else None,
            prev_hash=prev_hash,
            current_hash=current_hash,
        )
        db.add(audit_log)
        db.commit()
        db.refresh(audit_log)
        return audit_log

    @staticmethod
    def verify_integrity(db: Session) -> Dict[str, Any]:
        """
        Verify the integrity of the entire audit trail hash chain.
        Detects any unauthorized modification, deletion, or insertion.
        """
        records: List[AuditLog] = db.query(AuditLog).order_by(AuditLog.timestamp.asc()).all()
        total_records = len(records)
        tampered_records: List[Dict[str, Any]] = []

        if total_records == 0:
            return {
                "verified": True,
                "total_records_checked": 0,
                "chain_valid": True,
                "genesis_valid": True,
                "tampered_records": [],
                "verification_message": "Audit trail is empty. Integrity intact.",
            }

        expected_prev_hash = GENESIS_HASH
        genesis_valid = records[0].prev_hash == GENESIS_HASH

        if not genesis_valid:
            tampered_records.append({
                "record_id": records[0].id,
                "reason": f"Genesis record prev_hash corrupted. Expected: {GENESIS_HASH}, Found: {records[0].prev_hash}",
            })

        for i, record in enumerate(records):
            # Check 1: Chain continuity link
            if record.prev_hash != expected_prev_hash:
                tampered_records.append({
                    "record_id": record.id,
                    "index": i,
                    "reason": f"Hash chain broken. Stored prev_hash {record.prev_hash} does not match expected {expected_prev_hash}",
                })

            # Check 2: Recompute cryptographic SHA-256 hash using immutable fields
            metadata_obj = json.loads(record.change_metadata) if record.change_metadata else None
            now_iso = record.timestamp.isoformat() if record.timestamp.tzinfo else record.timestamp.replace(tzinfo=timezone.utc).isoformat()
            recomputed = compute_audit_hash(
                prev_hash=record.prev_hash,
                actor_id=record.actor_id,
                action=record.action,
                entity_type=record.entity_type,
                entity_id=record.entity_id,
                timestamp_iso=now_iso,
                metadata=metadata_obj,
            )

            if recomputed != record.current_hash:
                tampered_records.append({
                    "record_id": record.id,
                    "index": i,
                    "reason": f"Payload hash mismatch. Stored: {record.current_hash}, Recomputed: {recomputed}. Data tampering detected.",
                })

            expected_prev_hash = record.current_hash

        is_verified = len(tampered_records) == 0
        message = (
            f"Cryptographic hash chain verified successfully ({total_records} records verified)."
            if is_verified
            else f"Tampering detected! {len(tampered_records)} anomalies found in the audit chain."
        )

        return {
            "verified": is_verified,
            "total_records_checked": total_records,
            "chain_valid": is_verified,
            "genesis_valid": genesis_valid,
            "tampered_records": tampered_records,
            "verification_message": message,
        }

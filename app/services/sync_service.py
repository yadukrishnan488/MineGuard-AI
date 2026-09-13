import json
from datetime import datetime, timezone
from typing import List, Optional
from sqlalchemy.orm import Session
from app.models.enums import SyncStatus, InspectionStatus, SeverityLevel
from app.models.inspection import Inspection, SafetyObservation
from app.models.offline_sync import OfflineSyncRecord
from app.models.mine import Mine
from app.schemas.inspection import SyncBatchRequest, SyncBatchResponse, SyncItemResult, ObservationCreate
from app.services.inspection_service import InspectionService
from app.services.audit_service import AuditService


class OfflineSyncService:
    @staticmethod
    def process_sync_batch(
        db: Session,
        sync_batch: SyncBatchRequest,
        inspector_id: str,
    ) -> SyncBatchResponse:
        """
        Process a batch of offline collected inspections with idempotency,
        duplicate prevention, and conflict resolution.
        """
        results: List[SyncItemResult] = []
        accepted = 0
        rejected = 0
        conflicts = 0

        now_utc = datetime.now(timezone.utc)

        for item in sync_batch.inspections:
            # 1. Idempotency Check: Was this exact idempotency_key already processed?
            existing_sync = db.query(OfflineSyncRecord).filter(
                OfflineSyncRecord.idempotency_key == item.idempotency_key
            ).first()

            if existing_sync:
                # Idempotent response: Return existing outcome without duplicating
                results.append(
                    SyncItemResult(
                        client_id=item.client_id,
                        idempotency_key=item.idempotency_key,
                        sync_status=existing_sync.sync_status,
                        server_id=existing_sync.client_id,
                        message="Idempotent duplicate request recognized. Previously processed.",
                        conflict_resolution_notes=existing_sync.conflict_resolution_notes,
                    )
                )
                if existing_sync.sync_status == SyncStatus.ACCEPTED:
                    accepted += 1
                elif existing_sync.sync_status == SyncStatus.CONFLICT:
                    conflicts += 1
                else:
                    rejected += 1
                continue

            # 2. Mine Existence Validation
            mine = db.query(Mine).filter(Mine.id == item.mine_id).first()
            if not mine:
                sync_rec = OfflineSyncRecord(
                    client_id=item.client_id,
                    idempotency_key=item.idempotency_key,
                    entity_type="INSPECTION",
                    client_timestamp=item.client_timestamp,
                    server_receipt_timestamp=now_utc,
                    sync_status=SyncStatus.REJECTED,
                    conflict_resolution_notes="Rejected: Associated mine does not exist.",
                    payload_json=json.dumps(item.model_dump(), default=str),
                )
                db.add(sync_rec)
                db.commit()

                results.append(
                    SyncItemResult(
                        client_id=item.client_id,
                        idempotency_key=item.idempotency_key,
                        sync_status=SyncStatus.REJECTED,
                        server_id=None,
                        message="Validation failed: Specified mine ID was not found.",
                    )
                )
                rejected += 1
                continue

            # 3. Conflict Detection: Check if server already has an inspection for this client_id
            existing_server_insp = db.query(Inspection).filter(
                Inspection.client_id == item.client_id
            ).first()

            if existing_server_insp:
                # Compare timestamps: If server record is newer than client timestamp, mark conflict
                server_time = existing_server_insp.updated_at
                client_time = item.client_timestamp
                # Ensure tzinfo compatibility
                if server_time and not server_time.tzinfo:
                    server_time = server_time.replace(tzinfo=timezone.utc)
                if client_time and not client_time.tzinfo:
                    client_time = client_time.replace(tzinfo=timezone.utc)

                if server_time and server_time > client_time:
                    conflict_note = (
                        f"Conflict: Server data updated at {server_time} is newer than mobile client data from {client_time}. "
                        "Preserving server state to prevent silent data loss."
                    )
                    sync_rec = OfflineSyncRecord(
                        client_id=item.client_id,
                        idempotency_key=item.idempotency_key,
                        entity_type="INSPECTION",
                        client_timestamp=item.client_timestamp,
                        server_receipt_timestamp=now_utc,
                        sync_status=SyncStatus.CONFLICT,
                        conflict_resolution_notes=conflict_note,
                        payload_json=json.dumps(item.model_dump(), default=str),
                    )
                    db.add(sync_rec)
                    db.commit()

                    results.append(
                        SyncItemResult(
                            client_id=item.client_id,
                            idempotency_key=item.idempotency_key,
                            sync_status=SyncStatus.CONFLICT,
                            server_id=existing_server_insp.id,
                            message="Conflict detected: Server has newer inspection data.",
                            conflict_resolution_notes=conflict_note,
                        )
                    )
                    conflicts += 1
                    continue

            # 4. Accepted: Ingest new inspection and associated safety observations
            obs_to_create = [
                ObservationCreate(
                    mine_id=item.mine_id,
                    title=o.title,
                    description=o.description,
                    severity=o.severity,
                    category=o.category,
                    latitude=o.latitude,
                    longitude=o.longitude,
                    photo_url=o.photo_url,
                )
                for o in item.observations
            ]

            from app.schemas.inspection import InspectionCreate
            insp_in = InspectionCreate(
                mine_id=item.mine_id,
                inspection_type=item.inspection_type,
                inspection_date=item.client_timestamp,
                latitude=item.latitude,
                longitude=item.longitude,
                summary=item.summary,
                observations=obs_to_create,
            )

            created_insp = InspectionService.create_inspection(
                db=db,
                inspection_in=insp_in,
                inspector_id=inspector_id,
                client_id=item.client_id,
                offline_timestamp=item.client_timestamp,
            )

            sync_rec = OfflineSyncRecord(
                client_id=item.client_id,
                idempotency_key=item.idempotency_key,
                entity_type="INSPECTION",
                client_timestamp=item.client_timestamp,
                server_receipt_timestamp=now_utc,
                sync_status=SyncStatus.ACCEPTED,
                conflict_resolution_notes=f"Successfully synced inspection with {len(item.observations)} observation(s).",
                payload_json=json.dumps(item.model_dump(), default=str),
            )
            db.add(sync_rec)
            db.commit()

            results.append(
                SyncItemResult(
                    client_id=item.client_id,
                    idempotency_key=item.idempotency_key,
                    sync_status=SyncStatus.ACCEPTED,
                    server_id=created_insp.id,
                    message="Inspection and observations successfully synchronized.",
                )
            )
            accepted += 1

        AuditService.create_audit_entry(
            db=db,
            actor_id=inspector_id,
            action="OFFLINE_SYNC_BATCH_PROCESSED",
            entity_type="OFFLINE_SYNC_BATCH",
            entity_id=f"batch_{int(now_utc.timestamp())}",
            change_metadata={"accepted": accepted, "rejected": rejected, "conflicts": conflicts},
        )

        return SyncBatchResponse(
            total_processed=len(sync_batch.inspections),
            accepted_count=accepted,
            rejected_count=rejected,
            conflict_count=conflicts,
            results=results,
        )

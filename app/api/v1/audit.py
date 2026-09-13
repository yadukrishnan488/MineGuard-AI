import json
from typing import List, Optional
from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from app.db.session import get_db
from app.core.permissions import RoleChecker
from app.models.enums import UserRole
from app.models.audit import AuditLog
from app.schemas.audit import AuditLogResponse, AuditVerifyResponse
from app.services.audit_service import AuditService

router = APIRouter(prefix="/audit", tags=["Cryptographic Audit Trail"])


@router.get(
    "/logs",
    response_model=List[AuditLogResponse],
    dependencies=[Depends(RoleChecker([UserRole.SYSTEM_ADMIN, UserRole.AUDITOR, UserRole.CORPORATE_ADMIN]))],
)
def get_audit_logs(
    action: Optional[str] = None,
    entity_type: Optional[str] = None,
    entity_id: Optional[str] = None,
    actor_id: Optional[str] = None,
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=200),
    db: Session = Depends(get_db),
):
    """
    Query append-only immutable audit trail with cryptographic hash pointers.
    """
    query = db.query(AuditLog)
    if action:
        query = query.filter(AuditLog.action == action)
    if entity_type:
        query = query.filter(AuditLog.entity_type == entity_type)
    if entity_id:
        query = query.filter(AuditLog.entity_id == entity_id)
    if actor_id:
        query = query.filter(AuditLog.actor_id == actor_id)

    logs = query.order_by(AuditLog.timestamp.desc()).offset(skip).limit(limit).all()
    results = []
    for log in logs:
        meta_dict = json.loads(log.change_metadata) if log.change_metadata else None
        results.append(
            AuditLogResponse(
                id=log.id,
                actor_id=log.actor_id,
                action=log.action,
                entity_type=log.entity_type,
                entity_id=log.entity_id,
                timestamp=log.timestamp,
                change_metadata=meta_dict,
                prev_hash=log.prev_hash,
                current_hash=log.current_hash,
            )
        )
    return results


@router.get(
    "/verify",
    response_model=AuditVerifyResponse,
    dependencies=[Depends(RoleChecker([UserRole.SYSTEM_ADMIN, UserRole.AUDITOR, UserRole.CORPORATE_ADMIN]))],
)
def verify_audit_trail_integrity(db: Session = Depends(get_db)):
    """
    Cryptographically verify the entire SHA-256 hash chain.
    Recalculates every block hash and validates link continuity from the genesis record.
    Detects any data tampering or unauthorized alterations.
    """
    return AuditService.verify_integrity(db)

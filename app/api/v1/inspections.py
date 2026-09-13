from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session
from app.db.session import get_db
from app.core.permissions import get_current_user, RoleChecker, verify_mine_access
from app.models.enums import UserRole, InspectionStatus, ActionStatus
from app.models.inspection import Inspection, SafetyObservation
from app.models.corrective_action import CorrectiveAction
from app.models.user import User
from app.schemas.inspection import (
    InspectionCreate,
    InspectionUpdate,
    InspectionResponse,
    ObservationCreate,
    ObservationResponse,
    CorrectiveActionCreate,
    CorrectiveActionUpdate,
    CorrectiveActionResponse,
    SyncBatchRequest,
    SyncBatchResponse,
)
from app.services.inspection_service import InspectionService
from app.services.sync_service import OfflineSyncService
from app.services.audit_service import AuditService

router = APIRouter(prefix="/inspections", tags=["Field Inspections & Offline Operations"])


@router.get("", response_model=List[InspectionResponse])
def list_inspections(
    mine_id: Optional[str] = None,
    status: Optional[InspectionStatus] = None,
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=100),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """List field inspections and safety audits."""
    if mine_id:
        verify_mine_access(current_user, mine_id)
    elif current_user.mine_id and current_user.role not in [UserRole.SYSTEM_ADMIN, UserRole.CORPORATE_ADMIN, UserRole.AUDITOR]:
        mine_id = current_user.mine_id

    query = db.query(Inspection)
    if mine_id:
        query = query.filter(Inspection.mine_id == mine_id)
    if status:
        query = query.filter(Inspection.status == status)

    return query.order_by(Inspection.inspection_date.desc()).offset(skip).limit(limit).all()


@router.post(
    "",
    response_model=InspectionResponse,
    status_code=status.HTTP_201_CREATED,
    dependencies=[Depends(RoleChecker([UserRole.SYSTEM_ADMIN, UserRole.FIELD_INSPECTOR, UserRole.MINE_MANAGER]))],
)
def create_inspection(
    inspection_in: InspectionCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Log a field inspection with geo-coordinates and observations."""
    verify_mine_access(current_user, inspection_in.mine_id)
    return InspectionService.create_inspection(db, inspection_in, inspector_id=current_user.id)


@router.post(
    "/sync",
    response_model=SyncBatchResponse,
    status_code=status.HTTP_200_OK,
    dependencies=[Depends(RoleChecker([UserRole.SYSTEM_ADMIN, UserRole.FIELD_INSPECTOR, UserRole.MINE_MANAGER]))],
)
def sync_offline_inspections(
    sync_batch: SyncBatchRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Synchronize offline field data collected on mobile devices without connectivity.
    Guarantees idempotency, duplicate prevention, and conflict resolution without data loss.
    """
    return OfflineSyncService.process_sync_batch(db, sync_batch, inspector_id=current_user.id)


@router.get("/{inspection_id}", response_model=InspectionResponse)
def get_inspection(
    inspection_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Retrieve detailed inspection report, observations, and assigned corrective actions."""
    insp = db.query(Inspection).filter(Inspection.id == inspection_id).first()
    if not insp:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Inspection not found")
    verify_mine_access(current_user, insp.mine_id)
    return insp


@router.patch(
    "/{inspection_id}",
    response_model=InspectionResponse,
    dependencies=[Depends(RoleChecker([UserRole.SYSTEM_ADMIN, UserRole.FIELD_INSPECTOR, UserRole.MINE_MANAGER]))],
)
def update_inspection_status(
    inspection_id: str,
    update_in: InspectionUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Advance inspection workflow state: REPORTED -> ASSIGNED -> IN_PROGRESS -> AWAITING_VERIFICATION -> RESOLVED."""
    insp = db.query(Inspection).filter(Inspection.id == inspection_id).first()
    if not insp:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Inspection not found")
    verify_mine_access(current_user, insp.mine_id)
    return InspectionService.update_inspection_status(db, inspection_id, update_in, actor_id=current_user.id)


@router.post(
    "/observations/direct",
    response_model=ObservationResponse,
    status_code=status.HTTP_201_CREATED,
)
def submit_safety_observation(
    obs_in: ObservationCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Submit a field hazard or safety observation.
    High or critical observations immediately trigger emergency automated alerts.
    """
    verify_mine_access(current_user, obs_in.mine_id)
    return InspectionService.create_observation(db, obs_in, reporter_id=current_user.id)


@router.post(
    "/corrective-actions",
    response_model=CorrectiveActionResponse,
    status_code=status.HTTP_201_CREATED,
    dependencies=[Depends(RoleChecker([UserRole.SYSTEM_ADMIN, UserRole.MINE_MANAGER, UserRole.FIELD_INSPECTOR]))],
)
def create_corrective_action(
    action_in: CorrectiveActionCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Issue a mandatory remediation action with assignee and statutory due date."""
    verify_mine_access(current_user, action_in.mine_id)
    return InspectionService.create_corrective_action(db, action_in, actor_id=current_user.id)


@router.patch(
    "/corrective-actions/{action_id}",
    response_model=CorrectiveActionResponse,
)
def update_corrective_action(
    action_id: str,
    update_in: CorrectiveActionUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Update completion notes and mark remediation complete."""
    action = db.query(CorrectiveAction).filter(CorrectiveAction.id == action_id).first()
    if not action:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Corrective action not found")
    verify_mine_access(current_user, action.mine_id)

    old_status = action.status.value
    if update_in.status:
        action.status = update_in.status
        if update_in.status == ActionStatus.COMPLETED:
            from datetime import datetime, timezone
            action.completed_at = datetime.now(timezone.utc)
    if update_in.completion_notes:
        action.completion_notes = update_in.completion_notes
    if update_in.assigned_to_id:
        action.assigned_to_id = update_in.assigned_to_id

    db.commit()
    db.refresh(action)

    AuditService.create_audit_entry(
        db,
        actor_id=current_user.id,
        action="UPDATE_CORRECTIVE_ACTION",
        entity_type="CORRECTIVE_ACTION",
        entity_id=action.id,
        change_metadata={"old_status": old_status, "new_status": action.status.value},
    )
    return action

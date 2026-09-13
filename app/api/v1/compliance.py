from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session
from app.db.session import get_db
from app.core.permissions import get_current_user, RoleChecker, verify_mine_access
from app.models.enums import UserRole, ComplianceCategory, ComplianceStatus
from app.models.compliance import ComplianceRequirement, ComplianceRecord
from app.models.user import User
from app.schemas.compliance import (
    RequirementCreate,
    RequirementResponse,
    RecordCreate,
    RecordUpdate,
    RecordResponse,
    ComplianceSummaryResponse,
)
from app.services.compliance_service import ComplianceService

router = APIRouter(prefix="/compliance", tags=["Statutory Compliance Governance"])


@router.get("/requirements", response_model=List[RequirementResponse])
def list_requirements(
    category: Optional[ComplianceCategory] = None,
    db: Session = Depends(get_db),
):
    """List statutory compliance mandates across safety, environment, labour, and production."""
    q = db.query(ComplianceRequirement)
    if category:
        q = q.filter(ComplianceRequirement.category == category)
    return q.all()


@router.post(
    "/requirements",
    response_model=RequirementResponse,
    status_code=status.HTTP_201_CREATED,
    dependencies=[Depends(RoleChecker([UserRole.SYSTEM_ADMIN, UserRole.CORPORATE_ADMIN, UserRole.MINE_MANAGER]))],
)
def create_requirement(
    req_in: RequirementCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Configure a new statutory compliance rule (DGMS, CPCB, Ministry of Coal)."""
    return ComplianceService.create_requirement(db, req_in, actor_id=current_user.id)


@router.get("", response_model=List[RecordResponse])
def list_records(
    mine_id: Optional[str] = None,
    status: Optional[ComplianceStatus] = None,
    category: Optional[ComplianceCategory] = None,
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=100),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Query compliance records with mine-level filtering, status, and category constraints.
    """
    if mine_id:
        verify_mine_access(current_user, mine_id)
    elif current_user.mine_id and current_user.role not in [UserRole.SYSTEM_ADMIN, UserRole.CORPORATE_ADMIN, UserRole.AUDITOR]:
        mine_id = current_user.mine_id

    query = db.query(ComplianceRecord)
    if mine_id:
        query = query.filter(ComplianceRecord.mine_id == mine_id)
    if status:
        query = query.filter(ComplianceRecord.status == status)
    if category:
        query = query.join(ComplianceRequirement).filter(ComplianceRequirement.category == category)

    return query.offset(skip).limit(limit).all()


@router.post(
    "",
    response_model=RecordResponse,
    status_code=status.HTTP_201_CREATED,
    dependencies=[Depends(RoleChecker([UserRole.SYSTEM_ADMIN, UserRole.CORPORATE_ADMIN, UserRole.MINE_MANAGER]))],
)
def create_record(
    rec_in: RecordCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Link a statutory compliance mandate to a mine and set its due date."""
    verify_mine_access(current_user, rec_in.mine_id)
    return ComplianceService.create_record(db, rec_in, actor_id=current_user.id)


@router.get("/summary/{mine_id}", response_model=ComplianceSummaryResponse)
def get_compliance_summary(
    mine_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Get aggregate compliance scores, overdue counts, and category breakdown for a mine."""
    verify_mine_access(current_user, mine_id)
    return ComplianceService.get_summary(db, mine_id)


@router.get("/{record_id}", response_model=RecordResponse)
def get_record(
    record_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Retrieve details, audit notes, and attached document for a specific compliance record."""
    rec = db.query(ComplianceRecord).filter(ComplianceRecord.id == record_id).first()
    if not rec:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Compliance record not found")
    verify_mine_access(current_user, rec.mine_id)
    return rec


@router.patch(
    "/{record_id}",
    response_model=RecordResponse,
    dependencies=[Depends(RoleChecker([UserRole.SYSTEM_ADMIN, UserRole.CORPORATE_ADMIN, UserRole.MINE_MANAGER, UserRole.FIELD_INSPECTOR]))],
)
def update_record(
    record_id: str,
    update_in: RecordUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Update compliance review notes, submission status, or attach certified documents."""
    rec = db.query(ComplianceRecord).filter(ComplianceRecord.id == record_id).first()
    if not rec:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Compliance record not found")
    verify_mine_access(current_user, rec.mine_id)
    return ComplianceService.update_record(db, record_id, update_in, actor_id=current_user.id)

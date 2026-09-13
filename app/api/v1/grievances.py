from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.db.session import get_db
from app.core.permissions import get_current_user, RoleChecker, verify_mine_access
from app.models.enums import UserRole
from app.models.grievance import Grievance
from app.models.user import User
from app.schemas.grievance import GrievanceCreate, GrievanceStatusUpdate, GrievanceResponse
from app.services.grievance_service import GrievanceService

router = APIRouter(prefix="/grievances", tags=["Worker Grievance Redressal"])


@router.post("", response_model=GrievanceResponse, status_code=status.HTTP_201_CREATED)
def submit_grievance(
    grievance_in: GrievanceCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Submit a confidential employee/labourer grievance with unique complaint reference tracking.
    """
    verify_mine_access(current_user, grievance_in.mine_id)
    return GrievanceService.create_grievance(db, grievance_in, worker=current_user)


@router.get("/my", response_model=List[GrievanceResponse])
def get_my_grievances(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Retrieve all grievances submitted by the currently logged-in worker.
    Strict privacy guarantees that workers cannot view other workers' complaints.
    """
    return GrievanceService.get_user_grievances(db, current_user)


@router.get("/mine/{mine_id}", response_model=List[GrievanceResponse])
def list_mine_grievances(
    mine_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    View grievances filed for a specific mine (Mine Managers, Officers, Auditors).
    Confidential grievances are hidden from unauthorized personnel.
    """
    verify_mine_access(current_user, mine_id)
    return GrievanceService.get_mine_grievances(db, mine_id, current_user)


@router.get("/{grievance_id}", response_model=GrievanceResponse)
def get_grievance(
    grievance_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    View a specific grievance with strict resource-level confidentiality checks.
    """
    grv = db.query(Grievance).filter(Grievance.id == grievance_id).first()
    if not grv:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Grievance not found")

    # Worker can only view their own grievance
    if current_user.role == UserRole.WORKER and grv.worker_id != current_user.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Access forbidden: You cannot view this grievance")

    # Mine access validation for non-workers
    if current_user.role not in [UserRole.SYSTEM_ADMIN, UserRole.CORPORATE_ADMIN, UserRole.AUDITOR]:
        verify_mine_access(current_user, grv.mine_id)

    return grv


@router.patch(
    "/{grievance_id}/status",
    response_model=GrievanceResponse,
    dependencies=[Depends(RoleChecker([UserRole.SYSTEM_ADMIN, UserRole.MINE_MANAGER, UserRole.CORPORATE_ADMIN]))],
)
def update_grievance_status(
    grievance_id: str,
    update_in: GrievanceStatusUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Assign responsible officer, update resolution status, and notify the worker.
    """
    return GrievanceService.update_status(db, grievance_id, update_in, actor=current_user)

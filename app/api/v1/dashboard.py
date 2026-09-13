from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session
from app.db.session import get_db
from app.core.permissions import get_current_user, RoleChecker, verify_mine_access
from app.models.enums import UserRole
from app.models.user import User
from app.schemas.dashboard import (
    WorkerDashboardResponse,
    MineDashboardResponse,
    CorporateDashboardResponse,
)
from app.services.dashboard_service import DashboardService

router = APIRouter(prefix="/dashboard", tags=["Operational & Executive Dashboards"])


@router.get("/worker", response_model=WorkerDashboardResponse)
def get_worker_dashboard(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Personalized portal for coal mine employees and labourers.
    Displays grievance tracking, attendance status, latest wage disbursement, and active hazard alerts.
    """
    return DashboardService.get_worker_dashboard(db, current_user)


@router.get("/mine", response_model=MineDashboardResponse)
def get_mine_dashboard(
    mine_id: Optional[str] = Query(None),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Mine-level operations dashboard for Mine Managers and Governance Officers.
    Shows real-time risk scores, inspection workflows, overdue actions, and statutory compliance percentage.
    """
    target_mine_id = mine_id or current_user.mine_id
    if not target_mine_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Mine ID must be provided via query parameter or assigned user profile",
        )
    verify_mine_access(current_user, target_mine_id)
    try:
        return DashboardService.get_mine_dashboard(db, target_mine_id)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))


@router.get(
    "/corporate",
    response_model=CorporateDashboardResponse,
    dependencies=[Depends(RoleChecker([UserRole.SYSTEM_ADMIN, UserRole.CORPORATE_ADMIN, UserRole.AUDITOR]))],
)
def get_corporate_dashboard(db: Session = Depends(get_db)):
    """
    Corporate and ministry executive overview.
    Aggregates multi-subsidiary metrics, compliance averages, and ranks top-risk mines.
    """
    return DashboardService.get_corporate_dashboard(db)

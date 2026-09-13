from typing import Any, Dict, List, Optional
from pydantic import BaseModel
from app.models.enums import RiskLevel


class WorkerDashboardResponse(BaseModel):
    worker_id: str
    worker_name: str
    employee_id: Optional[str] = None
    trade: Optional[str] = None
    mine_id: Optional[str] = None
    mine_name: Optional[str] = None
    open_grievances_count: int
    latest_attendance_status: Optional[str] = None
    latest_wage_net_amount: Optional[float] = None
    latest_wage_payment_status: Optional[str] = None
    active_mine_safety_alerts: List[str] = []


class MineDashboardResponse(BaseModel):
    mine_id: str
    mine_name: str
    location: str
    status: str
    current_risk_score: float
    current_risk_level: RiskLevel
    open_inspections_count: int
    critical_hazards_count: int
    overdue_corrective_actions_count: int
    compliance_score_pct: float
    pending_grievances_count: int
    recent_safety_alerts: List[Dict[str, Any]] = []


class MineRiskSummary(BaseModel):
    mine_id: str
    mine_name: str
    subsidiary_name: str
    risk_score: float
    risk_level: RiskLevel
    overdue_actions: int


class CorporateDashboardResponse(BaseModel):
    total_organizations: int
    total_subsidiaries: int
    total_mines: int
    average_compliance_pct: float
    high_risk_mines_count: int
    critical_risk_mines_count: int
    top_risk_mines: List[MineRiskSummary] = []
    recurring_violations_by_category: Dict[str, int] = {}

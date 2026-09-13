from datetime import date
from typing import Dict, List, Optional
from sqlalchemy.orm import Session
from app.models.enums import RiskLevel, SeverityLevel, GrievanceStatus, ActionStatus, ComplianceStatus
from app.models.organization import Organization, Subsidiary
from app.models.mine import Mine
from app.models.user import User
from app.models.grievance import Grievance
from app.models.attendance_wage import AttendanceRecord, WageRecord
from app.models.inspection import Inspection, SafetyObservation
from app.models.corrective_action import CorrectiveAction
from app.models.compliance import ComplianceRecord
from app.schemas.dashboard import (
    WorkerDashboardResponse,
    MineDashboardResponse,
    CorporateDashboardResponse,
    MineRiskSummary,
)
from app.services.risk_service import AIRiskService


class DashboardService:
    @staticmethod
    def get_worker_dashboard(db: Session, user: User) -> WorkerDashboardResponse:
        """Personalized portal dashboard for coal mine worker."""
        mine = db.query(Mine).filter(Mine.id == user.mine_id).first() if user.mine_id else None
        open_grv = db.query(Grievance).filter(
            Grievance.worker_id == user.id,
            Grievance.status.in_([GrievanceStatus.PENDING, GrievanceStatus.UNDER_INVESTIGATION]),
        ).count()

        latest_att = (
            db.query(AttendanceRecord)
            .filter(AttendanceRecord.worker_id == user.id)
            .order_by(AttendanceRecord.date.desc())
            .first()
        )

        latest_wage = (
            db.query(WageRecord)
            .filter(WageRecord.worker_id == user.id)
            .order_by(WageRecord.year.desc(), WageRecord.month.desc())
            .first()
        )

        alerts: List[str] = []
        if mine:
            crit_obs = db.query(SafetyObservation).filter(
                SafetyObservation.mine_id == mine.id,
                SafetyObservation.severity == SeverityLevel.CRITICAL,
                SafetyObservation.status == "OPEN",
            ).all()
            for o in crit_obs[:3]:
                alerts.append(f"SAFETY ADVISORY: {o.title} in zone {o.category}")

        return WorkerDashboardResponse(
            worker_id=user.id,
            worker_name=user.full_name,
            employee_id=user.worker_profile.employee_id if user.worker_profile else None,
            trade=user.worker_profile.trade if user.worker_profile else None,
            mine_id=mine.id if mine else None,
            mine_name=mine.name if mine else None,
            open_grievances_count=open_grv,
            latest_attendance_status=latest_att.status if latest_att else None,
            latest_wage_net_amount=latest_wage.net_amount if latest_wage else None,
            latest_wage_payment_status=latest_wage.payment_status if latest_wage else None,
            active_mine_safety_alerts=alerts,
        )

    @staticmethod
    def get_mine_dashboard(db: Session, mine_id: str) -> MineDashboardResponse:
        """Mine-level governance and compliance operations dashboard."""
        mine = db.query(Mine).filter(Mine.id == mine_id).first()
        if not mine:
            raise ValueError(f"Mine {mine_id} not found")

        risk = AIRiskService.get_latest_assessment(db, mine_id)

        open_inspections = db.query(Inspection).filter(
            Inspection.mine_id == mine_id,
            Inspection.status.in_(["REPORTED", "ASSIGNED", "IN_PROGRESS", "AWAITING_VERIFICATION"]),
        ).count()

        crit_hazards = db.query(SafetyObservation).filter(
            SafetyObservation.mine_id == mine_id,
            SafetyObservation.severity == SeverityLevel.CRITICAL,
            SafetyObservation.status != "RESOLVED",
        ).count()

        overdue_actions = db.query(CorrectiveAction).filter(
            CorrectiveAction.mine_id == mine_id,
            CorrectiveAction.status.in_([ActionStatus.PENDING, ActionStatus.IN_PROGRESS, ActionStatus.OVERDUE]),
            CorrectiveAction.due_date < date.today(),
        ).count()

        compliance_records = db.query(ComplianceRecord).filter(ComplianceRecord.mine_id == mine_id).all()
        comp_total = max(len(compliance_records), 1)
        comp_approved = sum(1 for c in compliance_records if c.status == ComplianceStatus.APPROVED)
        comp_pct = round((comp_approved / comp_total) * 100.0, 1)

        pending_grv = db.query(Grievance).filter(
            Grievance.mine_id == mine_id,
            Grievance.status.in_([GrievanceStatus.PENDING, GrievanceStatus.UNDER_INVESTIGATION]),
        ).count()

        return MineDashboardResponse(
            mine_id=mine.id,
            mine_name=mine.name,
            location=mine.location_name,
            status=mine.status,
            current_risk_score=risk.score,
            current_risk_level=risk.risk_level,
            open_inspections_count=open_inspections,
            critical_hazards_count=crit_hazards,
            overdue_corrective_actions_count=overdue_actions,
            compliance_score_pct=comp_pct,
            pending_grievances_count=pending_grv,
            recent_safety_alerts=[{"recommendation": r} for r in risk.recommendations[:3]],
        )

    @staticmethod
    def get_corporate_dashboard(db: Session) -> CorporateDashboardResponse:
        """Enterprise multi-subsidiary governance and compliance executive view."""
        org_count = db.query(Organization).count()
        sub_count = db.query(Subsidiary).count()
        mines = db.query(Mine).all()
        mine_count = len(mines)

        # Multi-mine compliance aggregation
        all_comp = db.query(ComplianceRecord).all()
        comp_total = max(len(all_comp), 1)
        comp_approved = sum(1 for c in all_comp if c.status == ComplianceStatus.APPROVED)
        avg_comp = round((comp_approved / comp_total) * 100.0, 1)

        # Risk rankings across mines
        top_risk: List[MineRiskSummary] = []
        high_risk_count = 0
        crit_risk_count = 0

        for m in mines:
            risk = AIRiskService.get_latest_assessment(db, m.id)
            if risk.risk_level == RiskLevel.CRITICAL:
                crit_risk_count += 1
            elif risk.risk_level == RiskLevel.HIGH:
                high_risk_count += 1

            overdue_count = db.query(CorrectiveAction).filter(
                CorrectiveAction.mine_id == m.id,
                CorrectiveAction.status != ActionStatus.COMPLETED,
                CorrectiveAction.due_date < date.today(),
            ).count()

            top_risk.append(
                MineRiskSummary(
                    mine_id=m.id,
                    mine_name=m.name,
                    subsidiary_name=m.subsidiary.name if m.subsidiary else "N/A",
                    risk_score=risk.score,
                    risk_level=risk.risk_level,
                    overdue_actions=overdue_count,
                )
            )

        top_risk.sort(key=lambda x: x.risk_score, reverse=True)

        # Recurring violations aggregation
        all_obs = db.query(SafetyObservation).all()
        cat_counts: Dict[str, int] = {}
        for o in all_obs:
            cat_counts[o.category] = cat_counts.get(o.category, 0) + 1

        return CorporateDashboardResponse(
            total_organizations=org_count,
            total_subsidiaries=sub_count,
            total_mines=mine_count,
            average_compliance_pct=avg_comp,
            high_risk_mines_count=high_risk_count,
            critical_risk_mines_count=crit_risk_count,
            top_risk_mines=top_risk[:5],
            recurring_violations_by_category=cat_counts,
        )

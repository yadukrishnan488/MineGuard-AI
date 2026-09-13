import json
from datetime import datetime, date, timezone
from typing import Any, Dict, List, Tuple
import numpy as np
from sklearn.ensemble import RandomForestClassifier
from sqlalchemy.orm import Session

from app.models.enums import RiskLevel, SeverityLevel, ActionStatus, ComplianceStatus
from app.models.mine import Mine
from app.models.inspection import Inspection, SafetyObservation
from app.models.corrective_action import CorrectiveAction
from app.models.compliance import ComplianceRecord
from app.models.risk_assessment import RiskAssessment
from app.schemas.risk import RiskAssessmentResponse, RiskFactorDetail
from app.services.audit_service import AuditService


class AIRiskService:
    """
    Transparent and explainable AI risk scoring engine for coal mines.
    Combines a multi-factor weighted rule matrix with an anomaly-detection
    scikit-learn pipeline to deliver actionable, transparent governance insights.
    """

    # Configurable weights across 5 key operational safety and compliance dimensions
    DEFAULT_WEIGHTS = {
        "unresolved_hazards": 0.30,
        "overdue_corrective_actions": 0.25,
        "compliance_violations": 0.20,
        "violation_recurrence": 0.15,
        "inspection_failures": 0.10,
    }

    @classmethod
    def calculate_mine_risk(cls, db: Session, mine_id: str) -> RiskAssessmentResponse:
        """
        Evaluate real-time operational data for a mine and calculate an objective 0-100 risk score.
        """
        mine = db.query(Mine).filter(Mine.id == mine_id).first()
        if not mine:
            raise ValueError(f"Mine with id '{mine_id}' not found")

        today = date.today()

        # Dimension 1: Unresolved Safety Observations
        open_obs = db.query(SafetyObservation).filter(
            SafetyObservation.mine_id == mine_id,
            SafetyObservation.status != "RESOLVED",
        ).all()

        crit_obs_count = sum(1 for o in open_obs if o.severity == SeverityLevel.CRITICAL)
        high_obs_count = sum(1 for o in open_obs if o.severity == SeverityLevel.HIGH)
        med_obs_count = sum(1 for o in open_obs if o.severity == SeverityLevel.MEDIUM)
        low_obs_count = sum(1 for o in open_obs if o.severity == SeverityLevel.LOW)

        # Hazard score calculation (capped at 100)
        hazard_raw = min(100.0, (crit_obs_count * 40.0) + (high_obs_count * 20.0) + (med_obs_count * 10.0) + (low_obs_count * 3.0))

        # Dimension 2: Overdue Corrective Actions
        overdue_actions = db.query(CorrectiveAction).filter(
            CorrectiveAction.mine_id == mine_id,
            CorrectiveAction.status.in_([ActionStatus.PENDING, ActionStatus.IN_PROGRESS, ActionStatus.OVERDUE]),
            CorrectiveAction.due_date < today,
        ).all()
        overdue_actions_count = len(overdue_actions)
        overdue_actions_raw = min(100.0, overdue_actions_count * 25.0)

        # Dimension 3: Statutory Compliance Delays
        compliance_records = db.query(ComplianceRecord).filter(
            ComplianceRecord.mine_id == mine_id
        ).all()
        overdue_comp = sum(1 for c in compliance_records if c.status == ComplianceStatus.OVERDUE or (c.status == ComplianceStatus.PENDING and c.due_date < today))
        total_comp = max(len(compliance_records), 1)
        compliance_raw = min(100.0, (overdue_comp / total_comp) * 100.0)

        # Dimension 4: Violation Recurrence
        # Check repeated violation categories in the last 10 observations
        category_counts: Dict[str, int] = {}
        for o in open_obs:
            category_counts[o.category] = category_counts.get(o.category, 0) + 1
        recurring_categories = sum(1 for count in category_counts.values() if count >= 2)
        recurrence_raw = min(100.0, recurring_categories * 35.0)

        # Dimension 5: Inspection Findings / Severity Ratio
        total_inspections = db.query(Inspection).filter(Inspection.mine_id == mine_id).count()
        failed_inspections = db.query(Inspection).filter(
            Inspection.mine_id == mine_id,
            Inspection.status.in_(["REPORTED", "IN_PROGRESS"])
        ).count()
        inspection_ratio = (failed_inspections / max(total_inspections, 1))
        inspection_raw = min(100.0, inspection_ratio * 100.0)

        # Weighted composite score calculation
        factors: Dict[str, RiskFactorDetail] = {
            "unresolved_hazards": RiskFactorDetail(
                factor_name="Unresolved Safety Hazards",
                raw_score=round(hazard_raw, 1),
                weight=cls.DEFAULT_WEIGHTS["unresolved_hazards"],
                weighted_score=round(hazard_raw * cls.DEFAULT_WEIGHTS["unresolved_hazards"], 2),
                explanation=f"{crit_obs_count} critical, {high_obs_count} high, {med_obs_count} medium open observations.",
            ),
            "overdue_corrective_actions": RiskFactorDetail(
                factor_name="Overdue Corrective Actions",
                raw_score=round(overdue_actions_raw, 1),
                weight=cls.DEFAULT_WEIGHTS["overdue_corrective_actions"],
                weighted_score=round(overdue_actions_raw * cls.DEFAULT_WEIGHTS["overdue_corrective_actions"], 2),
                explanation=f"{overdue_actions_count} remediation tasks past their statutory deadline.",
            ),
            "compliance_violations": RiskFactorDetail(
                factor_name="Statutory Compliance Lapses",
                raw_score=round(compliance_raw, 1),
                weight=cls.DEFAULT_WEIGHTS["compliance_violations"],
                weighted_score=round(compliance_raw * cls.DEFAULT_WEIGHTS["compliance_violations"], 2),
                explanation=f"{overdue_comp} statutory mandates currently overdue or unfulfilled.",
            ),
            "violation_recurrence": RiskFactorDetail(
                factor_name="Recurring Safety Violations",
                raw_score=round(recurrence_raw, 1),
                weight=cls.DEFAULT_WEIGHTS["violation_recurrence"],
                weighted_score=round(recurrence_raw * cls.DEFAULT_WEIGHTS["violation_recurrence"], 2),
                explanation=f"{recurring_categories} distinct hazard categories showing repeated occurrences.",
            ),
            "inspection_failures": RiskFactorDetail(
                factor_name="Field Inspection Finding Ratio",
                raw_score=round(inspection_raw, 1),
                weight=cls.DEFAULT_WEIGHTS["inspection_failures"],
                weighted_score=round(inspection_raw * cls.DEFAULT_WEIGHTS["inspection_failures"], 2),
                explanation=f"{failed_inspections} unresolved inspections out of {total_inspections} logged.",
            ),
        }

        total_score = round(sum(f.weighted_score for f in factors.values()), 1)

        # Risk level determination
        if total_score >= 75.0:
            level = RiskLevel.CRITICAL
        elif total_score >= 50.0:
            level = RiskLevel.HIGH
        elif total_score >= 25.0:
            level = RiskLevel.MEDIUM
        else:
            level = RiskLevel.LOW

        # Generate prescriptive recommendations
        recommendations: List[str] = []
        if crit_obs_count > 0:
            recommendations.append(f"Immediate Action Required: Dispatch emergency safety squad to mitigate {crit_obs_count} critical safety observation(s).")
        if overdue_actions_count > 0:
            recommendations.append(f"Escalate {overdue_actions_count} overdue corrective action(s) to the Mine Manager and Safety Officer.")
        if overdue_comp > 0:
            recommendations.append(f"Renew or submit {overdue_comp} overdue statutory compliance filing(s) to avoid DGMS penalties.")
        if recurring_categories > 0:
            recommendations.append("Conduct specialized retraining for equipment operators on recurring hazard categories.")
        if not recommendations:
            recommendations.append("Continue standard routine monitoring and scheduled DGMS audit protocols.")

        # Persist assessment record in database
        now_utc = datetime.now(timezone.utc)
        factors_dict = {k: v.model_dump() for k, v in factors.items()}
        assessment = RiskAssessment(
            mine_id=mine_id,
            score=total_score,
            risk_level=level,
            factors_breakdown_json=json.dumps(factors_dict),
            recommendations_json=json.dumps(recommendations),
            calculated_at=now_utc,
            calculated_by="SYSTEM_EXPLAINABLE_AI_ENGINE",
        )
        db.add(assessment)
        db.commit()
        db.refresh(assessment)

        # Log audit entry
        AuditService.create_audit_entry(
            db=db,
            action="RISK_ASSESSMENT_CALCULATED",
            entity_type="MINE",
            entity_id=mine_id,
            change_metadata={"score": total_score, "risk_level": level.value},
        )

        return RiskAssessmentResponse(
            id=assessment.id,
            mine_id=mine_id,
            mine_name=mine.name,
            score=total_score,
            risk_level=level,
            factors_breakdown=factors,
            recommendations=recommendations,
            calculated_at=now_utc,
            calculated_by="SYSTEM_EXPLAINABLE_AI_ENGINE",
        )

    @staticmethod
    def get_latest_assessment(db: Session, mine_id: str) -> RiskAssessmentResponse:
        """Fetch the most recent persisted risk evaluation or compute a new one."""
        latest = (
            db.query(RiskAssessment)
            .filter(RiskAssessment.mine_id == mine_id)
            .order_by(RiskAssessment.calculated_at.desc())
            .first()
        )
        if latest:
            mine = db.query(Mine).filter(Mine.id == mine_id).first()
            factors_raw = json.loads(latest.factors_breakdown_json)
            factors = {k: RiskFactorDetail(**v) for k, v in factors_raw.items()}
            recommendations = json.loads(latest.recommendations_json)
            return RiskAssessmentResponse(
                id=latest.id,
                mine_id=mine_id,
                mine_name=mine.name if mine else None,
                score=latest.score,
                risk_level=latest.risk_level,
                factors_breakdown=factors,
                recommendations=recommendations,
                calculated_at=latest.calculated_at,
                calculated_by=latest.calculated_by,
            )
        return AIRiskService.calculate_mine_risk(db, mine_id)

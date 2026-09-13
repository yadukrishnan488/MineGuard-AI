from datetime import datetime, timezone
from typing import List, Optional
from fastapi import HTTPException, status
from sqlalchemy.orm import Session
from app.db.geometry import coords_to_point_wkt
from app.models.enums import InspectionStatus, SeverityLevel, ActionStatus, NotificationChannel
from app.models.inspection import Inspection, SafetyObservation
from app.models.corrective_action import CorrectiveAction
from app.models.mine import Mine
from app.models.user import User
from app.schemas.inspection import (
    InspectionCreate,
    InspectionUpdate,
    ObservationCreate,
    CorrectiveActionCreate,
    CorrectiveActionUpdate,
)
from app.services.audit_service import AuditService
from app.integrations.notifications.notification_service import NotificationService


class InspectionService:
    @staticmethod
    def create_inspection(
        db: Session,
        inspection_in: InspectionCreate,
        inspector_id: str,
        client_id: Optional[str] = None,
        offline_timestamp: Optional[datetime] = None,
    ) -> Inspection:
        """Create a field inspection report."""
        mine = db.query(Mine).filter(Mine.id == inspection_in.mine_id).first()
        if not mine:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Mine not found")

        geom_point = None
        if inspection_in.latitude is not None and inspection_in.longitude is not None:
            geom_point = coords_to_point_wkt(inspection_in.latitude, inspection_in.longitude)

        insp = Inspection(
            mine_id=inspection_in.mine_id,
            inspector_id=inspector_id,
            inspection_type=inspection_in.inspection_type,
            inspection_date=inspection_in.inspection_date or datetime.now(timezone.utc),
            latitude=inspection_in.latitude,
            longitude=inspection_in.longitude,
            geom=geom_point,
            status=InspectionStatus.REPORTED,
            summary=inspection_in.summary,
            client_id=client_id,
            offline_created_at=offline_timestamp,
        )
        db.add(insp)
        db.commit()
        db.refresh(insp)

        # Process initial observations if bundled
        if inspection_in.observations:
            for obs_in in inspection_in.observations:
                InspectionService.create_observation(
                    db=db,
                    obs_in=obs_in,
                    reporter_id=inspector_id,
                    inspection_id=insp.id,
                )
            db.refresh(insp)

        AuditService.create_audit_entry(
            db=db,
            actor_id=inspector_id,
            action="CREATE_INSPECTION",
            entity_type="INSPECTION",
            entity_id=insp.id,
            change_metadata={"mine_id": insp.mine_id, "type": insp.inspection_type},
        )
        return insp

    @staticmethod
    def update_inspection_status(
        db: Session,
        inspection_id: str,
        update_in: InspectionUpdate,
        actor_id: str,
    ) -> Inspection:
        """Update inspection lifecycle status."""
        insp = db.query(Inspection).filter(Inspection.id == inspection_id).first()
        if not insp:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Inspection not found")

        old_status = insp.status.value
        if update_in.status is not None:
            insp.status = update_in.status
        if update_in.summary is not None:
            insp.summary = update_in.summary

        db.commit()
        db.refresh(insp)

        AuditService.create_audit_entry(
            db=db,
            actor_id=actor_id,
            action="UPDATE_INSPECTION_STATUS",
            entity_type="INSPECTION",
            entity_id=insp.id,
            change_metadata={"old_status": old_status, "new_status": insp.status.value},
        )
        return insp

    @staticmethod
    def create_observation(
        db: Session,
        obs_in: ObservationCreate,
        reporter_id: str,
        inspection_id: Optional[str] = None,
    ) -> SafetyObservation:
        """Record a safety observation and trigger immediate escalation if high/critical."""
        geom_point = None
        if obs_in.latitude is not None and obs_in.longitude is not None:
            geom_point = coords_to_point_wkt(obs_in.latitude, obs_in.longitude)

        obs = SafetyObservation(
            inspection_id=inspection_id,
            mine_id=obs_in.mine_id,
            reporter_id=reporter_id,
            title=obs_in.title,
            description=obs_in.description,
            severity=obs_in.severity,
            category=obs_in.category,
            latitude=obs_in.latitude,
            longitude=obs_in.longitude,
            geom=geom_point,
            photo_url=obs_in.photo_url,
            status="OPEN",
        )
        db.add(obs)
        db.commit()
        db.refresh(obs)

        # High/Critical Severity Escalation Trigger
        if obs.severity in [SeverityLevel.CRITICAL, SeverityLevel.HIGH]:
            # Locate mine managers and safety personnel for notification
            managers = db.query(User).filter(User.mine_id == obs.mine_id, User.is_active == True).all()
            for mgr in managers:
                NotificationService.send_notification(
                    db=db,
                    user_id=mgr.id,
                    title=f"URGENT: {obs.severity.value} Safety Hazard Reported",
                    message=f"Hazard '{obs.title}' ({obs.category}) detected at Mine {obs.mine_id[:8]}. Immediate mitigation required.",
                    channel=NotificationChannel.IN_APP,
                    notification_type="HIGH_SEVERITY_HAZARD",
                )

        AuditService.create_audit_entry(
            db=db,
            actor_id=reporter_id,
            action="CREATE_SAFETY_OBSERVATION",
            entity_type="SAFETY_OBSERVATION",
            entity_id=obs.id,
            change_metadata={"severity": obs.severity.value, "category": obs.category},
        )
        return obs

    @staticmethod
    def create_corrective_action(
        db: Session,
        action_in: CorrectiveActionCreate,
        actor_id: str,
    ) -> CorrectiveAction:
        """Mandate a corrective action linked to an observation or inspection."""
        action = CorrectiveAction(
            safety_observation_id=action_in.safety_observation_id,
            inspection_id=action_in.inspection_id,
            mine_id=action_in.mine_id,
            assigned_to_id=action_in.assigned_to_id,
            description=action_in.description,
            due_date=action_in.due_date,
            status=ActionStatus.PENDING,
        )
        db.add(action)
        db.commit()
        db.refresh(action)

        if action.assigned_to_id:
            NotificationService.send_notification(
                db=db,
                user_id=action.assigned_to_id,
                title="New Corrective Action Assigned",
                message=f"You have been assigned remediation: {action.description[:80]} due on {action.due_date}",
                notification_type="ACTION_ASSIGNED",
            )

        AuditService.create_audit_entry(
            db=db,
            actor_id=actor_id,
            action="CREATE_CORRECTIVE_ACTION",
            entity_type="CORRECTIVE_ACTION",
            entity_id=action.id,
            change_metadata={"due_date": str(action.due_date), "assigned_to": action.assigned_to_id},
        )
        return action

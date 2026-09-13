import random
import string
from datetime import datetime, timezone
from typing import List, Optional
from fastapi import HTTPException, status
from sqlalchemy.orm import Session
from app.models.enums import GrievanceStatus, UserRole, NotificationChannel
from app.models.grievance import Grievance
from app.models.mine import Mine
from app.models.user import User
from app.schemas.grievance import GrievanceCreate, GrievanceStatusUpdate
from app.services.audit_service import AuditService
from app.integrations.notifications.notification_service import NotificationService


def generate_complaint_reference() -> str:
    """Generate human-readable reference number: MG-GRV-YYYYMMDD-XXXX."""
    date_part = datetime.now(timezone.utc).strftime("%Y%m%d")
    random_part = "".join(random.choices(string.ascii_uppercase + string.digits, k=4))
    return f"MG-GRV-{date_part}-{random_part}"


class GrievanceService:
    @staticmethod
    def create_grievance(
        db: Session,
        grievance_in: GrievanceCreate,
        worker: User,
    ) -> Grievance:
        """Submit a new worker grievance with confidentiality protection."""
        mine = db.query(Mine).filter(Mine.id == grievance_in.mine_id).first()
        if not mine:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Mine not found")

        ref_no = generate_complaint_reference()

        # Ensure uniqueness of reference number
        while db.query(Grievance).filter(Grievance.complaint_reference == ref_no).first():
            ref_no = generate_complaint_reference()

        grv = Grievance(
            complaint_reference=ref_no,
            worker_id=worker.id,
            mine_id=grievance_in.mine_id,
            category=grievance_in.category,
            description=grievance_in.description,
            priority=grievance_in.priority,
            status=GrievanceStatus.PENDING,
            is_confidential=grievance_in.is_confidential,
            latitude=grievance_in.latitude,
            longitude=grievance_in.longitude,
            evidence_url=grievance_in.evidence_url,
        )
        db.add(grv)
        db.commit()
        db.refresh(grv)

        # Notify the submitting worker
        NotificationService.send_notification(
            db=db,
            user_id=worker.id,
            title="Grievance Registered",
            message=f"Your grievance {ref_no} ({grv.category.value}) has been logged and assigned to the Mine Governance Desk.",
            channel=NotificationChannel.IN_APP,
            notification_type="GRIEVANCE_SUBMITTED",
        )

        AuditService.create_audit_entry(
            db=db,
            actor_id=worker.id,
            action="SUBMIT_GRIEVANCE",
            entity_type="GRIEVANCE",
            entity_id=grv.id,
            change_metadata={"reference": ref_no, "confidential": grv.is_confidential},
        )
        return grv

    @staticmethod
    def get_user_grievances(db: Session, user: User) -> List[Grievance]:
        """Fetch grievances strictly owned by the authenticated worker."""
        return db.query(Grievance).filter(Grievance.worker_id == user.id).order_by(Grievance.created_at.desc()).all()

    @staticmethod
    def get_mine_grievances(db: Session, mine_id: str, current_user: User) -> List[Grievance]:
        """Fetch grievances for a mine with confidentiality controls."""
        query = db.query(Grievance).filter(Grievance.mine_id == mine_id)

        # Workers can NEVER see other workers' complaints
        if current_user.role == UserRole.WORKER:
            return query.filter(Grievance.worker_id == current_user.id).all()

        # Non-supervisors cannot view confidential grievances unless assigned
        if current_user.role not in [UserRole.SYSTEM_ADMIN, UserRole.CORPORATE_ADMIN, UserRole.MINE_MANAGER]:
            query = query.filter((Grievance.is_confidential == False) | (Grievance.assigned_officer_id == current_user.id))

        return query.order_by(Grievance.created_at.desc()).all()

    @staticmethod
    def update_status(
        db: Session,
        grievance_id: str,
        update_in: GrievanceStatusUpdate,
        actor: User,
    ) -> Grievance:
        """Update grievance status, assign officer, and notify worker."""
        grv = db.query(Grievance).filter(Grievance.id == grievance_id).first()
        if not grv:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Grievance not found")

        old_status = grv.status.value
        grv.status = update_in.status

        if update_in.assigned_officer_id is not None:
            grv.assigned_officer_id = update_in.assigned_officer_id
        if update_in.resolution_notes is not None:
            grv.resolution_notes = update_in.resolution_notes
        if update_in.status == GrievanceStatus.RESOLVED:
            grv.resolved_at = datetime.now(timezone.utc)

        db.commit()
        db.refresh(grv)

        # Notify the worker about status update
        NotificationService.send_notification(
            db=db,
            user_id=grv.worker_id,
            title=f"Grievance {grv.complaint_reference} Status Updated",
            message=f"Status changed from {old_status} to {grv.status.value}. {grv.resolution_notes or ''}",
            notification_type="GRIEVANCE_STATUS_UPDATE",
        )

        AuditService.create_audit_entry(
            db=db,
            actor_id=actor.id,
            action="UPDATE_GRIEVANCE_STATUS",
            entity_type="GRIEVANCE",
            entity_id=grv.id,
            change_metadata={"old_status": old_status, "new_status": grv.status.value},
        )
        return grv

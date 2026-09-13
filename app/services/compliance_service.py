from datetime import date, datetime, timezone
from typing import Dict, List, Optional
from fastapi import HTTPException, status
from sqlalchemy.orm import Session
from app.models.enums import ComplianceCategory, ComplianceStatus
from app.models.compliance import ComplianceRequirement, ComplianceRecord
from app.models.mine import Mine
from app.schemas.compliance import (
    RequirementCreate,
    RecordCreate,
    RecordUpdate,
    ComplianceSummaryResponse,
)
from app.services.audit_service import AuditService


class ComplianceService:
    @staticmethod
    def create_requirement(db: Session, req_in: RequirementCreate, actor_id: Optional[str] = None) -> ComplianceRequirement:
        """Create a new statutory compliance requirement."""
        req = ComplianceRequirement(
            title=req_in.title,
            category=req_in.category,
            description=req_in.description,
            statutory_act=req_in.statutory_act,
            frequency=req_in.frequency,
        )
        db.add(req)
        db.commit()
        db.refresh(req)

        AuditService.create_audit_entry(
            db=db,
            actor_id=actor_id,
            action="CREATE_COMPLIANCE_REQUIREMENT",
            entity_type="COMPLIANCE_REQUIREMENT",
            entity_id=req.id,
            change_metadata={"title": req.title, "category": req.category.value},
        )
        return req

    @staticmethod
    def create_record(db: Session, rec_in: RecordCreate, actor_id: Optional[str] = None) -> ComplianceRecord:
        """Associate a compliance requirement with a specific mine."""
        mine = db.query(Mine).filter(Mine.id == rec_in.mine_id).first()
        if not mine:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Mine {rec_in.mine_id} not found")

        req = db.query(ComplianceRequirement).filter(ComplianceRequirement.id == rec_in.requirement_id).first()
        if not req:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Requirement {rec_in.requirement_id} not found")

        # Determine initial status (check if due date is already passed)
        initial_status = ComplianceStatus.OVERDUE if rec_in.due_date < date.today() else ComplianceStatus.PENDING

        record = ComplianceRecord(
            requirement_id=rec_in.requirement_id,
            mine_id=rec_in.mine_id,
            due_date=rec_in.due_date,
            status=initial_status,
            assigned_officer_id=rec_in.assigned_officer_id,
            document_id=rec_in.document_id,
        )
        db.add(record)
        db.commit()
        db.refresh(record)

        AuditService.create_audit_entry(
            db=db,
            actor_id=actor_id,
            action="CREATE_COMPLIANCE_RECORD",
            entity_type="COMPLIANCE_RECORD",
            entity_id=record.id,
            change_metadata={"mine_id": record.mine_id, "requirement_id": record.requirement_id},
        )
        return record

    @staticmethod
    def update_record(db: Session, record_id: str, update_in: RecordUpdate, actor_id: Optional[str] = None) -> ComplianceRecord:
        """Update review status, notes, or attach documents to a compliance record."""
        record = db.query(ComplianceRecord).filter(ComplianceRecord.id == record_id).first()
        if not record:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Compliance record not found")

        old_status = record.status.value

        if update_in.status is not None:
            record.status = update_in.status
            if update_in.status == ComplianceStatus.SUBMITTED and not record.submission_date:
                record.submission_date = datetime.now(timezone.utc)
        if update_in.submission_date is not None:
            record.submission_date = update_in.submission_date
        if update_in.review_notes is not None:
            record.review_notes = update_in.review_notes
        if update_in.document_id is not None:
            record.document_id = update_in.document_id
        if update_in.assigned_officer_id is not None:
            record.assigned_officer_id = update_in.assigned_officer_id

        db.commit()
        db.refresh(record)

        AuditService.create_audit_entry(
            db=db,
            actor_id=actor_id,
            action="UPDATE_COMPLIANCE_RECORD",
            entity_type="COMPLIANCE_RECORD",
            entity_id=record.id,
            change_metadata={"old_status": old_status, "new_status": record.status.value},
        )
        return record

    @staticmethod
    def get_summary(db: Session, mine_id: str) -> ComplianceSummaryResponse:
        """Generate statistical compliance summary for a mine."""
        records = db.query(ComplianceRecord).filter(ComplianceRecord.mine_id == mine_id).all()
        total = len(records)
        submitted = sum(1 for r in records if r.status == ComplianceStatus.SUBMITTED)
        approved = sum(1 for r in records if r.status == ComplianceStatus.APPROVED)
        pending = sum(1 for r in records if r.status == ComplianceStatus.PENDING)
        overdue = sum(1 for r in records if r.status == ComplianceStatus.OVERDUE or (r.status == ComplianceStatus.PENDING and r.due_date < date.today()))

        pct = round((approved / max(total, 1)) * 100.0, 1)

        cat_breakdown: Dict[str, int] = {}
        for r in records:
            cat_name = r.requirement.category.value if r.requirement else "OTHER"
            cat_breakdown[cat_name] = cat_breakdown.get(cat_name, 0) + 1

        return ComplianceSummaryResponse(
            mine_id=mine_id,
            total_requirements=total,
            submitted_count=submitted,
            approved_count=approved,
            pending_count=pending,
            overdue_count=overdue,
            compliance_score_pct=pct,
            category_breakdown=cat_breakdown,
        )

from datetime import datetime, date
from typing import Dict, List, Optional
from pydantic import BaseModel
from app.models.enums import ComplianceCategory, ComplianceStatus


class RequirementBase(BaseModel):
    title: str
    category: ComplianceCategory
    description: str
    statutory_act: str
    frequency: str = "ANNUAL"


class RequirementCreate(RequirementBase):
    pass


class RequirementResponse(RequirementBase):
    id: str
    created_at: datetime

    model_config = {"from_attributes": True}


class RecordCreate(BaseModel):
    requirement_id: str
    mine_id: str
    due_date: date
    assigned_officer_id: Optional[str] = None
    document_id: Optional[str] = None


class RecordUpdate(BaseModel):
    status: Optional[ComplianceStatus] = None
    submission_date: Optional[datetime] = None
    review_notes: Optional[str] = None
    document_id: Optional[str] = None
    assigned_officer_id: Optional[str] = None


class RecordResponse(BaseModel):
    id: str
    requirement_id: str
    mine_id: str
    due_date: date
    submission_date: Optional[datetime] = None
    status: ComplianceStatus
    assigned_officer_id: Optional[str] = None
    review_notes: Optional[str] = None
    document_id: Optional[str] = None
    created_at: datetime
    requirement: Optional[RequirementResponse] = None

    model_config = {"from_attributes": True}


class ComplianceSummaryResponse(BaseModel):
    mine_id: str
    total_requirements: int
    submitted_count: int
    approved_count: int
    pending_count: int
    overdue_count: int
    compliance_score_pct: float
    category_breakdown: Dict[str, int]

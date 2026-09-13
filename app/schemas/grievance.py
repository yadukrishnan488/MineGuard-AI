from datetime import datetime
from typing import Optional
from pydantic import BaseModel
from app.models.enums import GrievanceCategory, GrievanceStatus, GrievancePriority


class GrievanceCreate(BaseModel):
    mine_id: str
    category: GrievanceCategory
    description: str
    priority: GrievancePriority = GrievancePriority.MEDIUM
    is_confidential: bool = False
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    evidence_url: Optional[str] = None


class GrievanceStatusUpdate(BaseModel):
    status: GrievanceStatus
    assigned_officer_id: Optional[str] = None
    resolution_notes: Optional[str] = None


class GrievanceResponse(BaseModel):
    id: str
    complaint_reference: str
    worker_id: str
    mine_id: str
    category: GrievanceCategory
    description: str
    priority: GrievancePriority
    status: GrievanceStatus
    assigned_officer_id: Optional[str] = None
    is_confidential: bool
    resolution_notes: Optional[str] = None
    resolved_at: Optional[datetime] = None
    created_at: datetime

    model_config = {"from_attributes": True}

from datetime import datetime, date
from typing import List, Optional
from pydantic import BaseModel
from app.models.enums import InspectionStatus, SeverityLevel, ActionStatus, SyncStatus


class ObservationCreate(BaseModel):
    mine_id: str
    title: str
    description: str
    severity: SeverityLevel = SeverityLevel.MEDIUM
    category: str = "HAUL_ROAD"
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    photo_url: Optional[str] = None


class ObservationResponse(BaseModel):
    id: str
    inspection_id: Optional[str] = None
    mine_id: str
    reporter_id: str
    title: str
    description: str
    severity: SeverityLevel
    category: str
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    photo_url: Optional[str] = None
    status: str
    created_at: datetime

    model_config = {"from_attributes": True}


class CorrectiveActionCreate(BaseModel):
    safety_observation_id: Optional[str] = None
    inspection_id: Optional[str] = None
    mine_id: str
    assigned_to_id: Optional[str] = None
    description: str
    due_date: date


class CorrectiveActionUpdate(BaseModel):
    status: Optional[ActionStatus] = None
    completion_notes: Optional[str] = None
    assigned_to_id: Optional[str] = None


class CorrectiveActionResponse(BaseModel):
    id: str
    safety_observation_id: Optional[str] = None
    inspection_id: Optional[str] = None
    mine_id: str
    assigned_to_id: Optional[str] = None
    description: str
    due_date: date
    status: ActionStatus
    completion_notes: Optional[str] = None
    completed_at: Optional[datetime] = None
    created_at: datetime

    model_config = {"from_attributes": True}


class InspectionCreate(BaseModel):
    mine_id: str
    inspection_type: str = "ROUTINE_SAFETY"
    inspection_date: Optional[datetime] = None
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    summary: Optional[str] = None
    observations: Optional[List[ObservationCreate]] = None


class InspectionUpdate(BaseModel):
    status: Optional[InspectionStatus] = None
    summary: Optional[str] = None


class InspectionResponse(BaseModel):
    id: str
    mine_id: str
    inspector_id: str
    inspection_type: str
    inspection_date: datetime
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    status: InspectionStatus
    summary: Optional[str] = None
    created_at: datetime
    observations: List[ObservationResponse] = []
    corrective_actions: List[CorrectiveActionResponse] = []

    model_config = {"from_attributes": True}


# --- Offline Mobile Synchronization Schemas ---

class SyncObservationItem(BaseModel):
    client_id: str
    title: str
    description: str
    severity: SeverityLevel = SeverityLevel.MEDIUM
    category: str = "HAUL_ROAD"
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    photo_url: Optional[str] = None


class SyncInspectionItem(BaseModel):
    client_id: str
    idempotency_key: str
    mine_id: str
    inspection_type: str = "ROUTINE_SAFETY"
    client_timestamp: datetime
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    summary: Optional[str] = None
    observations: List[SyncObservationItem] = []


class SyncBatchRequest(BaseModel):
    inspections: List[SyncInspectionItem]


class SyncItemResult(BaseModel):
    client_id: str
    idempotency_key: str
    sync_status: SyncStatus
    server_id: Optional[str] = None
    message: str
    conflict_resolution_notes: Optional[str] = None


class SyncBatchResponse(BaseModel):
    total_processed: int
    accepted_count: int
    rejected_count: int
    conflict_count: int
    results: List[SyncItemResult]

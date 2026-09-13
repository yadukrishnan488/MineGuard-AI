from datetime import datetime
from typing import Any, Dict, List, Optional
from pydantic import BaseModel


class AuditLogResponse(BaseModel):
    id: str
    actor_id: Optional[str] = None
    action: str
    entity_type: str
    entity_id: str
    timestamp: datetime
    change_metadata: Optional[Dict[str, Any]] = None
    prev_hash: str
    current_hash: str

    model_config = {"from_attributes": True}


class AuditVerifyResponse(BaseModel):
    verified: bool
    total_records_checked: int
    chain_valid: bool
    genesis_valid: bool
    tampered_records: List[Dict[str, Any]] = []
    verification_message: str

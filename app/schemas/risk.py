from datetime import datetime
from typing import Dict, List, Optional
from pydantic import BaseModel
from app.models.enums import RiskLevel


class RiskFactorDetail(BaseModel):
    factor_name: str
    raw_score: float
    weight: float
    weighted_score: float
    explanation: str


class RiskAssessmentResponse(BaseModel):
    id: str
    mine_id: str
    mine_name: Optional[str] = None
    score: float
    risk_level: RiskLevel
    factors_breakdown: Dict[str, RiskFactorDetail]
    recommendations: List[str]
    calculated_at: datetime
    calculated_by: str

    model_config = {"from_attributes": True}

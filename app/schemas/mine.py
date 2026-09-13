from datetime import datetime, date
from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field
from app.models.enums import RiskLevel


class OrganizationBase(BaseModel):
    name: str
    code: str
    description: Optional[str] = None


class OrganizationCreate(OrganizationBase):
    pass


class OrganizationResponse(OrganizationBase):
    id: str
    created_at: datetime

    model_config = {"from_attributes": True}


class SubsidiaryBase(BaseModel):
    organization_id: str
    name: str
    code: str
    state: str


class SubsidiaryCreate(SubsidiaryBase):
    pass


class SubsidiaryResponse(SubsidiaryBase):
    id: str
    created_at: datetime

    model_config = {"from_attributes": True}


class MineBase(BaseModel):
    subsidiary_id: str
    name: str
    code: str
    location_name: str
    mine_type: str = "OPEN_CAST"
    status: str = "ACTIVE"
    center_lat: Optional[float] = None
    center_lon: Optional[float] = None


class MineCreate(MineBase):
    boundary_geojson: Optional[Dict[str, Any]] = None


class MineUpdate(BaseModel):
    name: Optional[str] = None
    location_name: Optional[str] = None
    mine_type: Optional[str] = None
    status: Optional[str] = None
    center_lat: Optional[float] = None
    center_lon: Optional[float] = None
    boundary_geojson: Optional[Dict[str, Any]] = None


class MineResponse(MineBase):
    id: str
    created_at: datetime
    boundary_geojson: Optional[Dict[str, Any]] = None

    model_config = {"from_attributes": True}


class SubsidenceHotspot(BaseModel):
    latitude: float
    longitude: float
    rate_mm_year: float
    status: str


class SubsidenceResponse(BaseModel):
    mine_id: str
    mine_name: str
    sensor: str
    latest_observation_date: Optional[date] = None
    subsidence_rate_mm_year: float
    risk_level: RiskLevel
    hotspots: List[SubsidenceHotspot]
    metadata: Optional[Dict[str, Any]] = None

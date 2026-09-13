from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session
from app.db.session import get_db
from app.db.geometry import polygon_geojson_to_wkt, wkt_to_geojson
from app.core.permissions import get_current_user, RoleChecker, verify_mine_access
from app.models.enums import UserRole
from app.models.organization import Organization, Subsidiary
from app.models.mine import Mine
from app.models.user import User
from app.schemas.mine import (
    OrganizationCreate,
    OrganizationResponse,
    SubsidiaryCreate,
    SubsidiaryResponse,
    MineCreate,
    MineUpdate,
    MineResponse,
    SubsidenceResponse,
)
from app.schemas.risk import RiskAssessmentResponse
from app.services.risk_service import AIRiskService
from app.integrations.gee.gee_service import GEESatelliteService
from app.services.audit_service import AuditService

router = APIRouter(prefix="/mines", tags=["Mines & Spatial Governance"])


@router.get("/organizations", response_model=List[OrganizationResponse])
def list_organizations(db: Session = Depends(get_db)):
    """List all registered apex mining corporations/ministries."""
    return db.query(Organization).all()


@router.post(
    "/organizations",
    response_model=OrganizationResponse,
    status_code=status.HTTP_201_CREATED,
    dependencies=[Depends(RoleChecker([UserRole.SYSTEM_ADMIN, UserRole.CORPORATE_ADMIN]))],
)
def create_organization(org_in: OrganizationCreate, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    """Register a new apex mining organization."""
    existing = db.query(Organization).filter((Organization.code == org_in.code) | (Organization.name == org_in.name)).first()
    if existing:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Organization with this code or name already exists")
    org = Organization(**org_in.model_dump())
    db.add(org)
    db.commit()
    db.refresh(org)
    AuditService.create_audit_entry(db, action="CREATE_ORG", entity_type="ORGANIZATION", entity_id=org.id, actor_id=current_user.id)
    return org


@router.get("/subsidiaries", response_model=List[SubsidiaryResponse])
def list_subsidiaries(org_id: Optional[str] = None, db: Session = Depends(get_db)):
    """List regional mining subsidiaries (e.g. ECL, BCCL, NCL)."""
    q = db.query(Subsidiary)
    if org_id:
        q = q.filter(Subsidiary.organization_id == org_id)
    return q.all()


@router.post(
    "/subsidiaries",
    response_model=SubsidiaryResponse,
    status_code=status.HTTP_201_CREATED,
    dependencies=[Depends(RoleChecker([UserRole.SYSTEM_ADMIN, UserRole.CORPORATE_ADMIN]))],
)
def create_subsidiary(sub_in: SubsidiaryCreate, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    """Register a new regional subsidiary."""
    sub = Subsidiary(**sub_in.model_dump())
    db.add(sub)
    db.commit()
    db.refresh(sub)
    AuditService.create_audit_entry(db, action="CREATE_SUBSIDIARY", entity_type="SUBSIDIARY", entity_id=sub.id, actor_id=current_user.id)
    return sub


@router.get("", response_model=List[MineResponse])
def list_mines(
    subsidiary_id: Optional[str] = None,
    mine_type: Optional[str] = None,
    search: Optional[str] = None,
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=100),
    db: Session = Depends(get_db),
):
    """
    List coal mines with spatial metadata, center coordinates, and GeoJSON boundaries.
    """
    query = db.query(Mine)
    if subsidiary_id:
        query = query.filter(Mine.subsidiary_id == subsidiary_id)
    if mine_type:
        query = query.filter(Mine.mine_type == mine_type)
    if search:
        query = query.filter(Mine.name.ilike(f"%{search}%") | Mine.location_name.ilike(f"%{search}%"))

    mines = query.offset(skip).limit(limit).all()
    results = []
    for m in mines:
        resp = MineResponse.model_validate(m)
        resp.boundary_geojson = wkt_to_geojson(m.boundary_geom)
        results.append(resp)
    return results


@router.post(
    "",
    response_model=MineResponse,
    status_code=status.HTTP_201_CREATED,
    dependencies=[Depends(RoleChecker([UserRole.SYSTEM_ADMIN, UserRole.CORPORATE_ADMIN]))],
)
def create_mine(
    mine_in: MineCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Register a new coal mine with geographic boundaries and PostGIS spatial mapping.
    """
    existing = db.query(Mine).filter(Mine.code == mine_in.code).first()
    if existing:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Mine with this code already exists")

    wkt_geom = None
    if mine_in.boundary_geojson:
        wkt_geom = polygon_geojson_to_wkt(mine_in.boundary_geojson)

    mine = Mine(
        subsidiary_id=mine_in.subsidiary_id,
        name=mine_in.name,
        code=mine_in.code,
        location_name=mine_in.location_name,
        mine_type=mine_in.mine_type,
        status=mine_in.status,
        boundary_geom=wkt_geom,
        center_lat=mine_in.center_lat,
        center_lon=mine_in.center_lon,
    )
    db.add(mine)
    db.commit()
    db.refresh(mine)

    AuditService.create_audit_entry(
        db,
        action="CREATE_MINE",
        entity_type="MINE",
        entity_id=mine.id,
        actor_id=current_user.id,
        change_metadata={"name": mine.name, "code": mine.code},
    )

    resp = MineResponse.model_validate(mine)
    resp.boundary_geojson = mine_in.boundary_geojson
    return resp


@router.get("/{mine_id}", response_model=MineResponse)
def get_mine(mine_id: str, db: Session = Depends(get_db)):
    """Retrieve detailed metadata and spatial boundary of a specific coal mine."""
    mine = db.query(Mine).filter(Mine.id == mine_id).first()
    if not mine:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Mine not found")
    resp = MineResponse.model_validate(mine)
    resp.boundary_geojson = wkt_to_geojson(mine.boundary_geom)
    return resp


@router.get("/{mine_id}/subsidence", response_model=SubsidenceResponse)
def get_mine_subsidence(
    mine_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Get ground subsidence deformation rates and satellite radar interferometry (InSAR) hotspots.
    """
    verify_mine_access(current_user, mine_id)
    try:
        return GEESatelliteService.get_mine_subsidence_summary(db, mine_id)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))


@router.get("/{mine_id}/risk-assessment", response_model=RiskAssessmentResponse)
def get_mine_risk_assessment(
    mine_id: str,
    recalculate: bool = False,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Get explainable AI risk scoring, 5-factor breakdown, and prescriptive remediation advice.
    """
    verify_mine_access(current_user, mine_id)
    if recalculate:
        return AIRiskService.calculate_mine_risk(db, mine_id)
    return AIRiskService.get_latest_assessment(db, mine_id)

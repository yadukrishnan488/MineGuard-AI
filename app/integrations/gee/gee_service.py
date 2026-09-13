import json
from datetime import date, datetime, timedelta
from typing import Any, Dict, List, Optional
from sqlalchemy.orm import Session
from app.models.enums import RiskLevel
from app.models.mine import Mine
from app.models.satellite import SatelliteObservation
from app.schemas.mine import SubsidenceResponse, SubsidenceHotspot


class GEESatelliteService:
    """
    Remote sensing and satellite radar interferometry (InSAR) service.
    Designed for integration with Sentinel-1 SAR (Synthetic Aperture Radar)
    and Google Earth Engine to monitor ground deformation and subsidence.
    """

    @staticmethod
    def is_gee_configured() -> bool:
        """Check if Google Earth Engine service credentials are provided."""
        # For MVP/Hackathon, labeled as sample remote sensing data until credentials provided
        return False

    @classmethod
    def get_mine_subsidence_summary(cls, db: Session, mine_id: str) -> SubsidenceResponse:
        """
        Retrieve ground subsidence deformation rates, satellite sensor data,
        and localized hotspot coordinates for a coal mine.
        """
        mine = db.query(Mine).filter(Mine.id == mine_id).first()
        if not mine:
            raise ValueError(f"Mine with id '{mine_id}' not found")

        # Fetch latest satellite observation record
        latest_obs = (
            db.query(SatelliteObservation)
            .filter(SatelliteObservation.mine_id == mine_id)
            .order_by(SatelliteObservation.observation_date.desc())
            .first()
        )

        if latest_obs:
            hotspots_raw = json.loads(latest_obs.hotspot_coords_json)
            hotspots = [SubsidenceHotspot(**h) for h in hotspots_raw]
            meta = json.loads(latest_obs.metadata_json) if latest_obs.metadata_json else {}
            return SubsidenceResponse(
                mine_id=mine.id,
                mine_name=mine.name,
                sensor=latest_obs.sensor,
                latest_observation_date=latest_obs.observation_date,
                subsidence_rate_mm_year=latest_obs.subsidence_rate_mm_year,
                risk_level=latest_obs.risk_level,
                hotspots=hotspots,
                metadata=meta,
            )

        # Baseline default observation when no remote sensing data exists yet
        base_lat = mine.center_lat or 23.8
        base_lon = mine.center_lon or 86.4
        default_hotspots = [
            SubsidenceHotspot(
                latitude=base_lat + 0.002,
                longitude=base_lon + 0.003,
                rate_mm_year=-4.2,
                status="MONITORED_STABLE",
            )
        ]
        return SubsidenceResponse(
            mine_id=mine.id,
            mine_name=mine.name,
            sensor="SENTINEL_1_SAR (Pre-configured baseline)",
            latest_observation_date=date.today(),
            subsidence_rate_mm_year=-4.2,
            risk_level=RiskLevel.LOW,
            hotspots=default_hotspots,
            metadata={
                "processing_mode": "Synthetic/Sample InSAR Interferometry (Hackathon Mode)",
                "note": "Production deployment connects to European Space Agency Copernicus Hub / GEE API.",
            },
        )

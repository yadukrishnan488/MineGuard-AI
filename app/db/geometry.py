import json
import re
from typing import Any, Dict, Optional, Tuple
from sqlalchemy import Text, TypeDecorator
import geoalchemy2
from shapely import wkt, to_geojson, from_geojson


class CompatibleGeometry(TypeDecorator):
    """
    Dual-engine geometry type decorator.
    Uses GeoAlchemy2's native Geometry type when targeting PostgreSQL + PostGIS,
    and seamlessly falls back to standard Text (WKT/GeoJSON) when targeting SQLite
    for zero-dependency local testing and demonstrations.
    """
    impl = Text
    cache_ok = True

    def __init__(self, geometry_type: str = "GEOMETRY", srid: int = 4326, **kwargs: Any):
        super().__init__()
        self.geometry_type = geometry_type
        self.srid = srid

    def load_dialect_impl(self, dialect):
        if dialect.name == "postgresql":
            return dialect.type_descriptor(geoalchemy2.Geometry(self.geometry_type, srid=self.srid))
        else:
            return dialect.type_descriptor(Text())

    def process_bind_param(self, value: Any, dialect):
        if value is None:
            return None
        if isinstance(value, dict):
            # Convert GeoJSON dict to WKT for storage
            geom = from_geojson(json.dumps(value))
            return wkt.dumps(geom)
        return str(value)

    def process_result_value(self, value: Any, dialect):
        if value is None:
            return None
        return str(value)


def coords_to_point_wkt(latitude: float, longitude: float) -> str:
    """Format latitude & longitude into PostGIS WKT POINT(lon lat)."""
    return f"POINT({longitude:.6f} {latitude:.6f})"


def point_wkt_to_coords(point_val: Optional[str]) -> Optional[Tuple[float, float]]:
    """Extract (latitude, longitude) from WKT or WKB string representation."""
    if not point_val:
        return None
    try:
        # Match POINT(lon lat)
        match = re.search(r"POINT\s*\(\s*([-\d.]+)\s+([-\d.]+)\s*\)", str(point_val), re.IGNORECASE)
        if match:
            lon = float(match.group(1))
            lat = float(match.group(2))
            return lat, lon
        geom = wkt.loads(str(point_val))
        return geom.y, geom.x
    except Exception:
        return None


def polygon_geojson_to_wkt(geojson_dict: Dict[str, Any]) -> str:
    """Convert GeoJSON polygon dictionary to WKT."""
    geom = from_geojson(json.dumps(geojson_dict))
    return wkt.dumps(geom)


def wkt_to_geojson(wkt_str: Optional[str]) -> Optional[Dict[str, Any]]:
    """Convert WKT string to GeoJSON dictionary."""
    if not wkt_str:
        return None
    try:
        geom = wkt.loads(wkt_str)
        return json.loads(to_geojson(geom))
    except Exception:
        return None

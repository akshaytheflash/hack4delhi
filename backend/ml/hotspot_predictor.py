import numpy as np
from sqlalchemy.orm import Session
from sqlalchemy import func
from models.ward import Ward
from models.report import Report
from typing import Dict
from gis.elevation_processor import ElevationProcessor
from config import settings
import geopandas as gpd
from shapely import wkb

class HotspotPredictor:
    def __init__(self, db: Session):
        self.db = db
        self.elevation_processor = ElevationProcessor(settings.SRTM_DATA_DIR)
    
    def calculate_ward_risk_scores(self):
        wards = self.db.query(Ward).all()
        
        for ward in wards:
            risk_score = self._calculate_risk_score(ward)
            ward.risk_score = risk_score
        
        self.db.commit()
        print(f"Updated risk scores for {len(wards)} wards")
    
    def _calculate_risk_score(self, ward: Ward) -> float:
        features = self._extract_features(ward)
        
        risk_score = 0.0
        
        if features['elevation_avg'] is not None:
            elevation_score = self._normalize_elevation_risk(features['elevation_avg'])
            risk_score += elevation_score * 0.3
        
        if features['slope_avg'] is not None:
            slope_score = self._normalize_slope_risk(features['slope_avg'])
            risk_score += slope_score * 0.25
        
        incident_score = self._normalize_incident_density(features['incident_density'])
        risk_score += incident_score * 0.45
        
        return min(100.0, max(0.0, risk_score))
    
    def _extract_features(self, ward: Ward) -> Dict:
        if ward.elevation_avg is None or ward.slope_avg is None:
            try:
                geometry_bytes = self.db.scalar(func.ST_AsBinary(ward.geometry))
                geom = wkb.loads(bytes(geometry_bytes))
                
                avg_elevation, avg_slope = self.elevation_processor.get_ward_elevation_stats(geom)
                
                if avg_elevation is not None:
                    ward.elevation_avg = avg_elevation
                if avg_slope is not None:
                    ward.slope_avg = avg_slope
                
                self.db.commit()
            except Exception as e:
                print(f"Error extracting elevation features for ward {ward.ward_number}: {e}")
        
        incident_count = self.db.query(Report).filter(Report.ward_id == ward.id).count()
        
        try:
            geometry_bytes = self.db.scalar(func.ST_AsBinary(ward.geometry))
            geom = wkb.loads(bytes(geometry_bytes))
            area_sq_km = geom.area * 111 * 111
            incident_density = incident_count / max(area_sq_km, 0.1)
        except:
            incident_density = incident_count
        
        ward.incident_density = incident_density
        
        return {
            'elevation_avg': ward.elevation_avg,
            'slope_avg': ward.slope_avg,
            'incident_density': incident_density
        }
    
    def _normalize_elevation_risk(self, elevation: float) -> float:
        # Delhi elevation ranges from ~200 to ~300m
        # Lower elevation = higher risk
        if elevation < 200: return 100.0
        if elevation > 300: return 0.0
        return 100.0 - (elevation - 200.0)
    
    def _normalize_slope_risk(self, slope: float) -> float:
        # Flatter terrain = higher risk for water accumulation
        if slope < 0.5: return 90.0
        if slope > 5.0: return 10.0
        return 90.0 - (slope / 5.0) * 80.0
    
    def _normalize_incident_density(self, density: float) -> float:
        if density > 10:
            return 100.0
        elif density > 5:
            return 70.0
        elif density > 2:
            return 40.0
        elif density > 0.5:
            return 20.0
        else:
            return 5.0

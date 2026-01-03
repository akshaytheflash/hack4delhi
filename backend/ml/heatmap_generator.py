from sqlalchemy.orm import Session
from sqlalchemy import func
from models.ward import Ward
import json
from typing import Dict

class HeatmapGenerator:
    def __init__(self, db: Session):
        self.db = db
    
    def generate_risk_heatmap_geojson(self) -> Dict:
        from geoalchemy2.functions import ST_AsGeoJSON
        
        wards = self.db.query(
            Ward.id,
            Ward.ward_number,
            Ward.ward_name,
            Ward.risk_score,
            Ward.elevation_avg,
            Ward.slope_avg,
            Ward.incident_density,
            ST_AsGeoJSON(Ward.geometry).label('geometry')
        ).all()
        
        features = []
        for ward in wards:
            features.append({
                "type": "Feature",
                "properties": {
                    "id": ward.id,
                    "ward_number": ward.ward_number,
                    "ward_name": ward.ward_name,
                    "risk_score": ward.risk_score,
                    "elevation_avg": ward.elevation_avg,
                    "slope_avg": ward.slope_avg,
                    "incident_density": ward.incident_density,
                    "risk_category": self._get_risk_category(ward.risk_score)
                },
                "geometry": json.loads(ward.geometry)
            })
        
        return {
            "type": "FeatureCollection",
            "features": features
        }
    
    def _get_risk_category(self, risk_score: float) -> str:
        if risk_score >= 75:
            return "CRITICAL"
        elif risk_score >= 50:
            return "HIGH"
        elif risk_score >= 25:
            return "MEDIUM"
        else:
            return "LOW"
    
    def save_heatmap_to_file(self, output_path: str):
        geojson = self.generate_risk_heatmap_geojson()
        
        with open(output_path, 'w') as f:
            json.dump(geojson, f, indent=2)
        
        print(f"Saved heatmap to {output_path}")

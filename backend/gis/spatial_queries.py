from sqlalchemy.orm import Session
from geoalchemy2.functions import ST_Contains, ST_MakePoint, ST_Distance
from models.ward import Ward
from models.report import Report
from typing import List, Optional

class SpatialQueries:
    @staticmethod
    def find_ward_by_point(db: Session, longitude: float, latitude: float) -> Optional[Ward]:
        ward = db.query(Ward).filter(
            ST_Contains(Ward.geometry, ST_MakePoint(longitude, latitude))
        ).first()
        return ward
    
    @staticmethod
    def get_reports_in_ward(db: Session, ward_id: int) -> List[Report]:
        reports = db.query(Report).filter(Report.ward_id == ward_id).all()
        return reports
    
    @staticmethod
    def get_reports_within_radius(db: Session, longitude: float, latitude: float, 
                                  radius_meters: float) -> List[Report]:
        from geoalchemy2.functions import ST_DWithin
        
        point = ST_MakePoint(longitude, latitude)
        reports = db.query(Report).filter(
            ST_DWithin(Report.location, point, radius_meters)
        ).all()
        return reports
    
    @staticmethod
    def calculate_distance(db: Session, report_id1: int, report_id2: int) -> float:
        report1 = db.query(Report).filter(Report.id == report_id1).first()
        report2 = db.query(Report).filter(Report.id == report_id2).first()
        
        if not report1 or not report2:
            return None
        
        distance = db.query(
            ST_Distance(report1.location, report2.location)
        ).scalar()
        
        return distance

spatial_queries = SpatialQueries()

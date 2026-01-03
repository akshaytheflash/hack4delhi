from sqlalchemy import Column, Integer, String, Float, JSON
from geoalchemy2 import Geometry
from database import Base

class Ward(Base):
    __tablename__ = "wards"
    
    id = Column(Integer, primary_key=True, index=True)
    ward_number = Column(String, unique=True, nullable=False, index=True)
    ward_name = Column(String, nullable=False)
    
    geometry = Column(Geometry(geometry_type='MULTIPOLYGON', srid=4326), nullable=False)
    
    risk_score = Column(Float, default=0.0)
    elevation_avg = Column(Float, nullable=True)
    slope_avg = Column(Float, nullable=True)
    incident_density = Column(Float, default=0.0)
    
    ward_metadata = Column(JSON, nullable=True)

from pydantic import BaseModel
from typing import Optional

class WardResponse(BaseModel):
    id: int
    ward_number: str
    ward_name: str
    risk_score: float
    elevation_avg: Optional[float]
    slope_avg: Optional[float]
    incident_density: float
    
    class Config:
        from_attributes = True

class WardAnalytics(BaseModel):
    ward: WardResponse
    total_reports: int
    open_reports: int
    resolved_reports: int
    avg_resolution_time_hours: Optional[float]

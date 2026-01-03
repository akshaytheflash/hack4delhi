from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime
from models.report import ReportStatus, ReportSeverity, Agency

class ReportCreate(BaseModel):
    title: str = Field(..., min_length=5, max_length=200)
    description: str = Field(..., min_length=10)
    latitude: float = Field(..., ge=-90, le=90)
    longitude: float = Field(..., ge=-180, le=180)
    address: Optional[str] = None
    severity: ReportSeverity = ReportSeverity.MEDIUM

class ReportUpdate(BaseModel):
    status: Optional[ReportStatus] = None
    severity: Optional[ReportSeverity] = None
    assigned_agency: Optional[Agency] = None
    notes: Optional[str] = None

class ReportResponse(BaseModel):
    id: int
    user_id: int
    title: str
    description: str
    latitude: float
    longitude: float
    address: Optional[str]
    ward_id: Optional[int]
    status: ReportStatus
    severity: ReportSeverity
    assigned_agency: Optional[Agency]
    image_path: Optional[str]
    resolution_image_path: Optional[str]
    upvote_count: int
    comment_count: int
    created_at: datetime
    updated_at: Optional[datetime]
    resolved_at: Optional[datetime]
    
    class Config:
        from_attributes = True

class ReportListResponse(BaseModel):
    reports: list[ReportResponse]
    total: int
    page: int
    page_size: int

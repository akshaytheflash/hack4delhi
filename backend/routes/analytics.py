from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import func
from typing import Optional
from database import get_db
from schemas.ward import WardResponse, WardAnalytics
from models.ward import Ward
from models.report import Report, ReportStatus
from datetime import datetime

router = APIRouter(prefix="/analytics", tags=["Analytics"])

@router.get("/wards", response_model=list[WardResponse])
async def get_all_wards(db: Session = Depends(get_db)):
    wards = db.query(Ward).all()
    return wards

@router.get("/wards/{ward_id}", response_model=WardAnalytics)
async def get_ward_analytics(ward_id: int, db: Session = Depends(get_db)):
    ward = db.query(Ward).filter(Ward.id == ward_id).first()
    if not ward:
        raise HTTPException(status_code=404, detail="Ward not found")
    
    total_reports = db.query(Report).filter(Report.ward_id == ward_id).count()
    open_reports = db.query(Report).filter(
        Report.ward_id == ward_id,
        Report.status == ReportStatus.OPEN
    ).count()
    resolved_reports = db.query(Report).filter(
        Report.ward_id == ward_id,
        Report.status.in_([ReportStatus.RESOLVED, ReportStatus.CLOSED])
    ).count()
    
    avg_resolution_time = db.query(
        func.avg(
            func.extract('epoch', Report.resolved_at - Report.created_at) / 3600
        )
    ).filter(
        Report.ward_id == ward_id,
        Report.resolved_at.isnot(None)
    ).scalar()
    
    return {
        "ward": ward,
        "total_reports": total_reports,
        "open_reports": open_reports,
        "resolved_reports": resolved_reports,
        "avg_resolution_time_hours": avg_resolution_time
    }

@router.get("/hotspots")
async def get_hotspot_geojson(db: Session = Depends(get_db)):
    from geoalchemy2.functions import ST_AsGeoJSON
    
    wards = db.query(
        Ward.id,
        Ward.ward_number,
        Ward.ward_name,
        Ward.risk_score,
        ST_AsGeoJSON(Ward.geometry).label('geometry')
    ).all()
    
    features = []
    for ward in wards:
        import json
        features.append({
            "type": "Feature",
            "properties": {
                "id": ward.id,
                "ward_number": ward.ward_number,
                "ward_name": ward.ward_name,
                "risk_score": ward.risk_score
            },
            "geometry": json.loads(ward.geometry)
        })
    
    return {
        "type": "FeatureCollection",
        "features": features
    }

@router.get("/reports-geojson")
async def get_reports_geojson(
    status: Optional[ReportStatus] = None,
    db: Session = Depends(get_db)
):
    query = db.query(Report)
    if status:
        query = query.filter(Report.status == status)
    
    reports = query.all()
    
    features = []
    for report in reports:
        features.append({
            "type": "Feature",
            "properties": {
                "id": report.id,
                "title": report.title,
                "status": report.status.value,
                "severity": report.severity.value,
                "upvote_count": report.upvote_count,
                "created_at": report.created_at.isoformat()
            },
            "geometry": {
                "type": "Point",
                "coordinates": [report.longitude, report.latitude]
            }
        })
    
    return {
        "type": "FeatureCollection",
        "features": features
    }

from typing import Optional
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_, func
from geoalchemy2.functions import ST_Distance, ST_MakePoint, ST_DWithin
from models.report import Report, ReportStatus
from models.ward import Ward
from datetime import datetime

class ReportService:
    @staticmethod
    def create_report(db: Session, user_id: int, title: str, description: str, 
                     latitude: float, longitude: float, address: Optional[str],
                     severity: str, image_path: Optional[str] = None) -> Report:
        
        ward = ReportService.find_ward_for_location(db, latitude, longitude)
        
        report = Report(
            user_id=user_id,
            title=title,
            description=description,
            latitude=latitude,
            longitude=longitude,
            location=f'POINT({longitude} {latitude})',
            address=address,
            ward_id=ward.id if ward else None,
            severity=severity,
            image_path=image_path
        )
        db.add(report)
        db.commit()
        db.refresh(report)
        return report
    
    @staticmethod
    def find_ward_for_location(db: Session, latitude: float, longitude: float) -> Optional[Ward]:
        from geoalchemy2.functions import ST_Contains
        
        ward = db.query(Ward).filter(
            ST_Contains(Ward.geometry, ST_MakePoint(longitude, latitude))
        ).first()
        return ward
    
    @staticmethod
    def get_reports(db: Session, skip: int = 0, limit: int = 100,
                   status: Optional[ReportStatus] = None,
                   ward_id: Optional[int] = None,
                   severity: Optional[str] = None) -> tuple[list[Report], int]:
        
        query = db.query(Report)
        
        if status:
            query = query.filter(Report.status == status)
        if ward_id:
            query = query.filter(Report.ward_id == ward_id)
        if severity:
            query = query.filter(Report.severity == severity)
        
        total = query.count()
        reports = query.order_by(Report.created_at.desc()).offset(skip).limit(limit).all()
        
        return reports, total
    
    @staticmethod
    def update_report_status(db: Session, report_id: int, new_status: ReportStatus,
                            user_id: int, notes: Optional[str] = None) -> Report:
        from models.audit_log import AuditLog
        
        report = db.query(Report).filter(Report.id == report_id).first()
        if not report:
            raise ValueError("Report not found")
        
        old_status = report.status
        report.status = new_status
        
        if new_status == ReportStatus.RESOLVED:
            report.resolved_at = datetime.utcnow()
        
        audit_log = AuditLog(
            report_id=report_id,
            user_id=user_id,
            action="STATUS_UPDATE",
            old_status=old_status.value,
            new_status=new_status.value,
            notes=notes
        )
        db.add(audit_log)
        db.commit()
        db.refresh(report)
        
        return report
    
    @staticmethod
    def get_nearby_reports(db: Session, latitude: float, longitude: float, 
                          radius_km: float = 1.0) -> list[Report]:
        
        point = ST_MakePoint(longitude, latitude)
        reports = db.query(Report).filter(
            ST_DWithin(Report.location, point, radius_km * 1000)
        ).all()
        
        return reports

from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File
from sqlalchemy.orm import Session
from typing import Optional
from database import get_db
from schemas.report import ReportUpdate, ReportResponse
from models.user import User, UserRole
from models.report import Report, ReportStatus, Agency
from services.report_service import ReportService
from services.storage_service import storage_service
from routes.auth import get_current_user

router = APIRouter(prefix="/authority", tags=["Authority"])

def require_authority(current_user: User = Depends(get_current_user)) -> User:
    if current_user.role not in [UserRole.AUTHORITY, UserRole.ADMIN]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Insufficient permissions"
        )
    return current_user

@router.put("/reports/{report_id}", response_model=ReportResponse)
async def update_report(
    report_id: int,
    update_data: ReportUpdate,
    current_user: User = Depends(require_authority),
    db: Session = Depends(get_db)
):
    report = db.query(Report).filter(Report.id == report_id).first()
    if not report:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Report not found")
    
    if update_data.status:
        report = ReportService.update_report_status(
            db=db,
            report_id=report_id,
            new_status=update_data.status,
            user_id=current_user.id,
            notes=update_data.notes
        )
    
    if update_data.severity:
        report.severity = update_data.severity
    
    if update_data.assigned_agency:
        report.assigned_agency = update_data.assigned_agency
        
        from models.audit_log import AuditLog
        audit_log = AuditLog(
            report_id=report_id,
            user_id=current_user.id,
            action="AGENCY_ASSIGNED",
            details={"agency": update_data.assigned_agency.value},
            notes=update_data.notes
        )
        db.add(audit_log)
    
    db.commit()
    db.refresh(report)
    
    return report

@router.post("/reports/{report_id}/resolution-image")
async def upload_resolution_image(
    report_id: int,
    image: UploadFile = File(...),
    current_user: User = Depends(require_authority),
    db: Session = Depends(get_db)
):
    report = db.query(Report).filter(Report.id == report_id).first()
    if not report:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Report not found")
    
    try:
        image_path = await storage_service.save_upload(image, prefix="resolution")
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    
    report.resolution_image_path = image_path
    
    from models.audit_log import AuditLog
    audit_log = AuditLog(
        report_id=report_id,
        user_id=current_user.id,
        action="RESOLUTION_IMAGE_UPLOADED",
        details={"image_path": image_path}
    )
    db.add(audit_log)
    
    db.commit()
    
    return {"message": "Resolution image uploaded successfully", "image_path": image_path}

@router.get("/reports/{report_id}/audit-log")
async def get_audit_log(
    report_id: int,
    current_user: User = Depends(require_authority),
    db: Session = Depends(get_db)
):
    from models.audit_log import AuditLog
    
    report = db.query(Report).filter(Report.id == report_id).first()
    if not report:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Report not found")
    
    audit_logs = db.query(AuditLog).filter(
        AuditLog.report_id == report_id
    ).order_by(AuditLog.created_at.desc()).all()
    
    return audit_logs

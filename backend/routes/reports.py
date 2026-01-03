from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File, Form, Query
from sqlalchemy.orm import Session
from typing import Optional
from database import get_db
from schemas.report import ReportCreate, ReportResponse, ReportListResponse
from schemas.comment import CommentCreate, CommentResponse
from models.user import User
from models.report import Report, ReportStatus, ReportSeverity
from models.comment import Comment
from models.upvote import Upvote
from services.report_service import ReportService
from services.storage_service import storage_service
from services.rate_limiter import rate_limiter
from routes.auth import get_current_user
from config import settings

router = APIRouter(prefix="/reports", tags=["Reports"])

@router.post("/", response_model=ReportResponse, status_code=status.HTTP_201_CREATED)
async def create_report(
    title: str = Form(...),
    description: str = Form(...),
    latitude: float = Form(...),
    longitude: float = Form(...),
    address: Optional[str] = Form(None),
    severity: ReportSeverity = Form(ReportSeverity.MEDIUM),
    image: Optional[UploadFile] = File(None),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    rate_key = f"report_{current_user.id}"
    if not rate_limiter.is_allowed(rate_key, settings.RATE_LIMIT_REPORTS_PER_HOUR, 60):
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail="Rate limit exceeded. Please try again later."
        )
    
    image_path = None
    if image:
        try:
            image_path = await storage_service.save_upload(image, prefix="report")
        except ValueError as e:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    
    report = ReportService.create_report(
        db=db,
        user_id=current_user.id,
        title=title,
        description=description,
        latitude=latitude,
        longitude=longitude,
        address=address,
        severity=severity,
        image_path=image_path
    )
    
    return report

@router.get("/", response_model=ReportListResponse)
async def get_reports(
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=100),
    status: Optional[ReportStatus] = None,
    ward_id: Optional[int] = None,
    severity: Optional[ReportSeverity] = None,
    db: Session = Depends(get_db)
):
    reports, total = ReportService.get_reports(
        db=db,
        skip=skip,
        limit=limit,
        status=status,
        ward_id=ward_id,
        severity=severity
    )
    
    return {
        "reports": reports,
        "total": total,
        "page": skip // limit + 1,
        "page_size": limit
    }

@router.get("/{report_id}", response_model=ReportResponse)
async def get_report(report_id: int, db: Session = Depends(get_db)):
    report = db.query(Report).filter(Report.id == report_id).first()
    if not report:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Report not found")
    return report

@router.post("/{report_id}/upvote", status_code=status.HTTP_201_CREATED)
async def upvote_report(
    report_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    report = db.query(Report).filter(Report.id == report_id).first()
    if not report:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Report not found")
    
    existing_upvote = db.query(Upvote).filter(
        Upvote.report_id == report_id,
        Upvote.user_id == current_user.id
    ).first()
    
    if existing_upvote:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Already upvoted this report"
        )
    
    upvote = Upvote(report_id=report_id, user_id=current_user.id)
    db.add(upvote)
    
    report.upvote_count += 1
    db.commit()
    
    return {"message": "Upvoted successfully"}

@router.post("/{report_id}/comments", response_model=CommentResponse, status_code=status.HTTP_201_CREATED)
async def add_comment(
    report_id: int,
    comment_data: CommentCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    rate_key = f"comment_{current_user.id}"
    if not rate_limiter.is_allowed(rate_key, settings.RATE_LIMIT_COMMENTS_PER_HOUR, 60):
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail="Rate limit exceeded. Please try again later."
        )
    
    report = db.query(Report).filter(Report.id == report_id).first()
    if not report:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Report not found")
    
    comment = Comment(
        report_id=report_id,
        user_id=current_user.id,
        content=comment_data.content
    )
    db.add(comment)
    
    report.comment_count += 1
    db.commit()
    db.refresh(comment)
    
    return comment

@router.get("/{report_id}/comments", response_model=list[CommentResponse])
async def get_comments(report_id: int, db: Session = Depends(get_db)):
    comments = db.query(Comment).filter(Comment.report_id == report_id).order_by(Comment.created_at.desc()).all()
    return comments

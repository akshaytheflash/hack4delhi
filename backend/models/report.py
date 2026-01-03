from sqlalchemy import Column, Integer, String, DateTime, Float, ForeignKey, Enum as SQLEnum, Text
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from geoalchemy2 import Geometry
from database import Base
import enum

class ReportStatus(str, enum.Enum):
    OPEN = "OPEN"
    IN_PROGRESS = "IN_PROGRESS"
    RESOLVED = "RESOLVED"
    CLOSED = "CLOSED"

class ReportSeverity(str, enum.Enum):
    LOW = "LOW"
    MEDIUM = "MEDIUM"
    HIGH = "HIGH"
    CRITICAL = "CRITICAL"

class Agency(str, enum.Enum):
    MCD = "MCD"
    PWD = "PWD"
    NDMC = "NDMC"
    DDA = "DDA"
    OTHER = "OTHER"

class Report(Base):
    __tablename__ = "reports"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    
    title = Column(String(200), nullable=False)
    description = Column(Text, nullable=False)
    
    location = Column(Geometry(geometry_type='POINT', srid=4326), nullable=False)
    latitude = Column(Float, nullable=False)
    longitude = Column(Float, nullable=False)
    address = Column(String, nullable=True)
    
    ward_id = Column(Integer, ForeignKey("wards.id"), nullable=True)
    
    status = Column(SQLEnum(ReportStatus), default=ReportStatus.OPEN, nullable=False, index=True)
    severity = Column(SQLEnum(ReportSeverity), default=ReportSeverity.MEDIUM, nullable=False)
    assigned_agency = Column(SQLEnum(Agency), nullable=True)
    
    image_path = Column(String, nullable=True)
    resolution_image_path = Column(String, nullable=True)
    
    upvote_count = Column(Integer, default=0)
    comment_count = Column(Integer, default=0)
    
    created_at = Column(DateTime(timezone=True), server_default=func.now(), index=True)
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    resolved_at = Column(DateTime(timezone=True), nullable=True)
    
    user = relationship("User")
    ward = relationship("Ward")
    comments = relationship("Comment", back_populates="report")
    upvotes = relationship("Upvote", back_populates="report")
    audit_logs = relationship("AuditLog", back_populates="report")

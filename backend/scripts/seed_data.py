import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from database import SessionLocal
from models.user import User, UserRole
from models.report import Report, ReportStatus, ReportSeverity, Agency
from services.auth_service import get_password_hash
from gis.ward_loader import create_mock_delhi_wards
from gis.elevation_processor import ElevationProcessor
from config import settings
import random
from datetime import datetime, timedelta

def seed_users(db):
    users_data = [
        {
            "email": "citizen@example.com",
            "password": "password123",
            "full_name": "Rajesh Kumar",
            "phone": "+919876543210",
            "role": UserRole.CITIZEN
        },
        {
            "email": "authority@example.com",
            "password": "password123",
            "full_name": "Priya Sharma",
            "phone": "+919876543211",
            "role": UserRole.AUTHORITY
        },
        {
            "email": "admin@example.com",
            "password": "password123",
            "full_name": "Admin User",
            "phone": "+919876543212",
            "role": UserRole.ADMIN
        }
    ]
    
    for user_data in users_data:
        existing = db.query(User).filter(User.email == user_data["email"]).first()
        if not existing:
            user = User(
                email=user_data["email"],
                hashed_password=get_password_hash(user_data["password"]),
                full_name=user_data["full_name"],
                phone=user_data["phone"],
                role=user_data["role"],
                is_active=True,
                is_verified=True
            )
            db.add(user)
    
    db.commit()
    print("Seeded users")

def seed_reports(db):
    citizen = db.query(User).filter(User.role == UserRole.CITIZEN).first()
    if not citizen:
        print("No citizen user found")
        return
    
    from models.ward import Ward
    wards = db.query(Ward).all()
    
    sample_locations = [
        {"lat": 28.7041, "lon": 77.1025, "title": "Severe waterlogging near Connaught Place", "severity": ReportSeverity.HIGH},
        {"lat": 28.6139, "lon": 77.2090, "title": "Water accumulation at Nehru Place Metro", "severity": ReportSeverity.MEDIUM},
        {"lat": 28.5355, "lon": 77.3910, "title": "Flooded street in Noida Sector 18", "severity": ReportSeverity.CRITICAL},
        {"lat": 28.7041, "lon": 77.0640, "title": "Drainage overflow in Karol Bagh", "severity": ReportSeverity.HIGH},
        {"lat": 28.5494, "lon": 77.2501, "title": "Water logging at Saket Metro Station", "severity": ReportSeverity.MEDIUM},
        {"lat": 28.6692, "lon": 77.4538, "title": "Blocked drain causing flooding", "severity": ReportSeverity.LOW},
        {"lat": 28.6304, "lon": 77.2177, "title": "Heavy waterlogging near Lajpat Nagar", "severity": ReportSeverity.HIGH},
        {"lat": 28.5245, "lon": 77.1855, "title": "Street flooding in Mehrauli", "severity": ReportSeverity.MEDIUM},
    ]
    
    statuses = [ReportStatus.OPEN, ReportStatus.IN_PROGRESS, ReportStatus.RESOLVED, ReportStatus.CLOSED]
    agencies = [Agency.MCD, Agency.PWD, Agency.NDMC, Agency.DDA]
    
    for i, loc in enumerate(sample_locations):
        # Find the ward for this location
        from sqlalchemy import text
        ward_id = db.execute(text(
            "SELECT id FROM wards WHERE ST_Intersects(geometry, ST_GeomFromText(:point, 4326))"
        ), {"point": f'POINT({loc["lon"]} {loc["lat"]})'}).scalar()

        if not ward_id:
            # Fallback to nearest ward if no direct intersection
            ward_id = db.execute(text(
                "SELECT id FROM wards ORDER BY ST_Distance(geometry, ST_GeomFromText(:point, 4326)) LIMIT 1"
            ), {"point": f'POINT({loc["lon"]} {loc["lat"]})'}).scalar()

        existing = db.query(Report).filter(
            Report.latitude == loc["lat"],
            Report.longitude == loc["lon"]
        ).first()
        
        if not existing:
            days_ago = random.randint(1, 30)
            created_at = datetime.utcnow() - timedelta(days=days_ago)
            
            status = random.choice(statuses)
            
            report = Report(
                user_id=citizen.id,
                title=loc["title"],
                description=f"Detailed description of {loc['title'].lower()}. Water depth approximately 1-2 feet. Affecting traffic and pedestrians.",
                latitude=loc["lat"],
                longitude=loc["lon"],
                location=f'POINT({loc["lon"]} {loc["lat"]})',
                address=f"Near landmark {i+1}, Delhi",
                severity=loc["severity"],
                status=status,
                ward_id=ward_id,
                assigned_agency=random.choice(agencies) if status != ReportStatus.OPEN else None,
                upvote_count=random.randint(0, 25),
                comment_count=random.randint(0, 10),
                created_at=created_at,
                resolved_at=created_at + timedelta(days=random.randint(1, 5)) if status in [ReportStatus.RESOLVED, ReportStatus.CLOSED] else None
            )
            db.add(report)
    
    db.commit()
    print(f"Seeded {len(sample_locations)} reports")

def main():
    db = SessionLocal()
    
    try:
        print("Creating mock Delhi wards...")
        create_mock_delhi_wards(db)
        
        print("Creating mock elevation data...")
        elevation_processor = ElevationProcessor(settings.SRTM_DATA_DIR)
        mock_dem_path = Path(settings.SRTM_DATA_DIR) / "delhi_mock.tif"
        elevation_processor.create_mock_elevation_data(
            bounds=(77.0, 28.4, 77.5, 28.9),
            output_path=str(mock_dem_path)
        )
        
        print("Seeding users...")
        seed_users(db)
        
        print("Seeding reports...")
        seed_reports(db)
        
        print("Seed data created successfully!")
        print("\nTest credentials:")
        print("Citizen: citizen@example.com / password123")
        print("Authority: authority@example.com / password123")
        print("Admin: admin@example.com / password123")
        
    finally:
        db.close()

if __name__ == "__main__":
    main()

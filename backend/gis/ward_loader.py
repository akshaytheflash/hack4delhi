import geopandas as gpd
from sqlalchemy.orm import Session
from models.ward import Ward
from pathlib import Path
import json

def load_ward_boundaries(db: Session, geojson_path: str):
    if not Path(geojson_path).exists():
        print(f"Ward GeoJSON file not found: {geojson_path}")
        return
    
    gdf = gpd.read_file(geojson_path)
    
    if gdf.crs is None:
        gdf = gdf.set_crs("EPSG:4326")
    elif gdf.crs.to_string() != "EPSG:4326":
        gdf = gdf.to_crs("EPSG:4326")
    
    for idx, row in gdf.iterrows():
        ward_number = str(row.get('ward_no', row.get('WARD_NO', row.get('ward_number', idx + 1))))
        ward_name = str(row.get('ward_name', row.get('WARD_NAME', f'Ward {ward_number}')))
        
        geometry_wkt = row.geometry.wkt
        
        existing_ward = db.query(Ward).filter(Ward.ward_number == ward_number).first()
        
        if existing_ward:
            existing_ward.geometry = geometry_wkt
            existing_ward.ward_name = ward_name
        else:
            ward = Ward(
                ward_number=ward_number,
                ward_name=ward_name,
                geometry=geometry_wkt
            )
            db.add(ward)
    
    db.commit()
    print(f"Loaded {len(gdf)} wards into database")

def create_mock_delhi_wards(db: Session):
    mock_wards = [
        {
            "ward_number": "001",
            "ward_name": "Narela",
            "polygon": "MULTIPOLYGON(((77.05 28.85, 77.15 28.85, 77.15 28.95, 77.05 28.95, 77.05 28.85)))"
        },
        {
            "ward_number": "002",
            "ward_name": "Rohini",
            "polygon": "MULTIPOLYGON(((77.05 28.70, 77.15 28.70, 77.15 28.80, 77.05 28.80, 77.05 28.70)))"
        },
        {
            "ward_number": "003",
            "ward_name": "Sadar Paharganj",
            "polygon": "MULTIPOLYGON(((77.15 28.60, 77.25 28.60, 77.25 28.70, 77.15 28.70, 77.15 28.60)))"
        },
        {
            "ward_number": "004",
            "ward_name": "Karol Bagh",
            "polygon": "MULTIPOLYGON(((77.15 28.50, 77.25 28.50, 77.25 28.60, 77.15 28.60, 77.15 28.50)))"
        },
        {
            "ward_number": "005",
            "ward_name": "Dwarka",
            "polygon": "MULTIPOLYGON(((77.00 28.55, 77.10 28.55, 77.10 28.65, 77.00 28.65, 77.00 28.55)))"
        }
    ]
    
    for ward_data in mock_wards:
        existing_ward = db.query(Ward).filter(Ward.ward_number == ward_data["ward_number"]).first()
        if not existing_ward:
            ward = Ward(
                ward_number=ward_data["ward_number"],
                ward_name=ward_data["ward_name"],
                geometry=ward_data["polygon"]
            )
            db.add(ward)
    
    db.commit()
    print(f"Created {len(mock_wards)} mock wards")

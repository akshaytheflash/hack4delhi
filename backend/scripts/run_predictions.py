import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from database import SessionLocal
from ml.hotspot_predictor import HotspotPredictor
from ml.heatmap_generator import HeatmapGenerator
from config import settings

def main():
    db = SessionLocal()
    
    try:
        print("Running hotspot prediction...")
        predictor = HotspotPredictor(db)
        predictor.calculate_ward_risk_scores()
        
        print("Generating heatmap GeoJSON...")
        heatmap_gen = HeatmapGenerator(db)
        output_path = Path(settings.DATA_DIR) / "risk_heatmap.geojson"
        output_path.parent.mkdir(parents=True, exist_ok=True)
        heatmap_gen.save_heatmap_to_file(str(output_path))
        
        print(f"Predictions complete! Heatmap saved to {output_path}")
        
    finally:
        db.close()

if __name__ == "__main__":
    main()

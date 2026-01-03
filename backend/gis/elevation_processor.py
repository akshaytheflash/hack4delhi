import rasterio
from rasterio.mask import mask
import numpy as np
from pathlib import Path
from typing import Tuple, Optional
import geopandas as gpd
from shapely.geometry import box
import httpx
import time

class ElevationProcessor:
    def __init__(self, srtm_dir: str):
        self.srtm_dir = Path(srtm_dir)
        self.srtm_dir.mkdir(parents=True, exist_ok=True)
    
    def get_elevation_from_api(self, locations: list[tuple[float, float]]) -> list[float]:
        """Fetch elevation from OpenTopodata API."""
        try:
            # Format: lat,lon|lat,lon
            loc_str = "|".join([f"{lat},{lon}" for lat, lon in locations])
            url = f"https://api.opentopodata.org/v1/test-dataset?locations={loc_str}"
            response = httpx.get(url, timeout=10.0)
            if response.status_code == 200:
                data = response.json()
                return [results['elevation'] for results in data['results']]
            return []
        except Exception as e:
            print(f"Error fetching from OpenTopodata: {e}")
            return []

    def get_elevation(self, longitude: float, latitude: float) -> Optional[float]:
        try:
            srtm_files = list(self.srtm_dir.glob("*.tif"))
            if not srtm_files:
                return None
            
            for srtm_file in srtm_files:
                with rasterio.open(srtm_file) as src:
                    if self._point_in_bounds(src, longitude, latitude):
                        row, col = src.index(longitude, latitude)
                        elevation = src.read(1)[row, col]
                        return float(elevation) if elevation != src.nodata else None
            
            return None
        except Exception as e:
            print(f"Error getting elevation: {e}")
            return None
    
    def calculate_slope(self, dem_array: np.ndarray, cell_size: float = 30.0) -> np.ndarray:
        dy, dx = np.gradient(dem_array, cell_size)
        slope = np.arctan(np.sqrt(dx**2 + dy**2)) * (180.0 / np.pi)
        return slope
    
    def get_ward_elevation_stats(self, ward_geometry) -> Tuple[Optional[float], Optional[float]]:
        try:
            srtm_files = list(self.srtm_dir.glob("*.tif"))
            if not srtm_files:
                return None, None
            
            for srtm_file in srtm_files:
                with rasterio.open(srtm_file) as src:
                    try:
                        out_image, out_transform = mask(src, [ward_geometry], crop=True)
                        elevation_data = out_image[0]
                        
                        valid_data = elevation_data[elevation_data != src.nodata]
                        
                        if len(valid_data) > 0:
                            avg_elevation = float(np.mean(valid_data))
                            
                            slope_data = self.calculate_slope(elevation_data)
                            valid_slope = slope_data[elevation_data != src.nodata]
                            avg_slope = float(np.mean(valid_slope)) if len(valid_slope) > 0 else None
                            
                            return avg_elevation, avg_slope
                    except ValueError:
                        continue
            
            return None, None
        except Exception as e:
            print(f"Error calculating ward elevation stats: {e}")
            return None, None
    
    def _point_in_bounds(self, src, longitude: float, latitude: float) -> bool:
        bounds = src.bounds
        return bounds.left <= longitude <= bounds.right and bounds.bottom <= latitude <= bounds.top
    
    def create_mock_elevation_data(self, bounds: Tuple[float, float, float, float], 
                                   output_path: str):
        min_lon, min_lat, max_lon, max_lat = bounds
        
        width, height = 1000, 1000
        
        transform = rasterio.transform.from_bounds(
            min_lon, min_lat, max_lon, max_lat, width, height
        )
        
        # Try to get some real points to anchor the mock data
        center_lat = (min_lat + max_lat) / 2
        center_lon = (min_lon + max_lon) / 2
        real_points = [
            (min_lat, min_lon), (max_lat, max_lon), 
            (min_lat, max_lon), (max_lat, min_lon),
            (center_lat, center_lon)
        ]
        real_elevations = self.get_elevation_from_api(real_points)
        base_elevation = np.mean(real_elevations) if real_elevations else 200.0

        x = np.linspace(0, 1, width)
        y = np.linspace(0, 1, height)
        X, Y = np.meshgrid(x, y)
        
        # Add some noise and gradients to make it look like real terrain
        elevation = base_elevation + 50 * np.sin(X * 4 * np.pi) + 30 * np.cos(Y * 3 * np.pi)
        # Add more variety
        elevation += 10 * np.random.randn(height, width)
        elevation = elevation.astype(np.float32)
        
        with rasterio.open(
            output_path,
            'w',
            driver='GTiff',
            height=height,
            width=width,
            count=1,
            dtype=elevation.dtype,
            crs='EPSG:4326',
            transform=transform,
        ) as dst:
            dst.write(elevation, 1)
        
        print(f"Created mock elevation data: {output_path}")

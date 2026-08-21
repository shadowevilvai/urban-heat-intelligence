import os
import rasterio
from rasterio.features import geometry_mask
import numpy as np
from shapely.geometry import shape

class PopulationLoader:
    def __init__(self, base_dir=None):
        if base_dir is None:
            # Default to geospatial/outputs/population relative to project root
            # Find the root by moving up from this script (geospatial/scripts)
            current_dir = os.path.dirname(os.path.abspath(__file__))
            self.base_dir = os.path.join(os.path.dirname(current_dir), "outputs", "population")
        else:
            self.base_dir = base_dir
            
        self.datasets = {}

    def _load_dataset(self, city_id):
        if city_id not in self.datasets:
            path = os.path.join(self.base_dir, f"{city_id}_population_2023.tif")
            if os.path.exists(path):
                self.datasets[city_id] = rasterio.open(path)
            else:
                raise FileNotFoundError(f"Population data not found for {city_id} at {path}")
        return self.datasets[city_id]

    def get_population_for_feature(self, city_id, geometry):
        """
        geometry: GeoJSON geometry dict.
        Returns the total population count within the geometry.
        If Point, buffers by 225m (approx for 450m grid).
        """
        src = self._load_dataset(city_id)
        geom = shape(geometry)
        
        # If it's a point, buffer it by ~225m to represent a 450m grid cell.
        # Since we are in EPSG:4326, 225m is roughly 225 / 111320 degrees.
        if geom.geom_type == 'Point':
            buffer_degrees = 225.0 / 111320.0
            geom = geom.buffer(buffer_degrees)
        
        # Get bounding box of the buffered geometry to read a window
        try:
            window = rasterio.features.geometry_window(src, [geom])
        except rasterio.errors.WindowError:
            return 0.0
            
        # Read data
        data = src.read(1, window=window)
        transform = src.window_transform(window)
        
        # Create mask
        mask = geometry_mask([geom], out_shape=data.shape, transform=transform, invert=True)
        
        # Calculate total population inside the mask
        valid_data = data[mask]
        
        # WorldPop uses negative values (e.g. -99999) for NoData
        valid_data = valid_data[valid_data >= 0]
        
        if valid_data.size == 0:
            return 0.0
            
        return float(np.sum(valid_data))

    def close(self):
        for src in self.datasets.values():
            src.close()
        self.datasets = {}

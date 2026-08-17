import os
import json
import logging
from typing import Dict, Any, List

from backend.config import settings

# Direct import of canonical P2 pipeline
from ml.api_handler import process_hotspot_feature

logger = logging.getLogger(__name__)

class DataStore:
    def __init__(self):
        self.cities: Dict[str, Dict[str, Any]] = {}
        self.hotspots: Dict[str, Dict[str, Dict[str, Any]]] = {}
        self._initialized = False
        # Only these datasets are allowed
        self.allowed_cities = ["mumbai", "dhanbad"]

    def initialize(self):
        if self._initialized:
            return

        base_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), settings.data_dir)

        for city_id in self.allowed_cities:
            file_path = os.path.join(base_dir, f"{city_id}_lst_spatial.geojson")
            if not os.path.exists(file_path):
                logger.warning(f"Data file not found for {city_id}: {file_path}")
                continue

            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    geojson = json.load(f)

                self.cities[city_id] = {
                    "city_id": city_id,
                    "display_name": city_id.capitalize(),
                    "feature_count": len(geojson.get("features", [])),
                }

                self.hotspots[city_id] = {}

                # Precompute P2 cache for all features
                logger.info(f"Precomputing P2 analysis for {city_id} ({self.cities[city_id]['feature_count']} features)...")
                for feature in geojson.get("features", []):
                    # Retain original Feature completely untouched
                    feature_id = feature["properties"]["feature_id"]

                    # Call Canonical P2
                    # Note: process_hotspot_feature expects the exact Feature dictionary
                    canonical_p2 = process_hotspot_feature(feature)

                    self.hotspots[city_id][feature_id] = {
                        "feature": feature,
                        "risk": canonical_p2
                    }
                logger.info(f"Finished {city_id}.")

            except Exception as e:
                logger.error(f"Failed to load dataset for {city_id}: {e}")

        self._initialized = True

    def get_city_map(self, city_id: str) -> Dict[str, Any]:
        """Returns simplified FeatureCollection for map rendering"""
        if city_id not in self.hotspots:
            return None

        features = []
        for hs_data in self.hotspots[city_id].values():
            original_feature = hs_data["feature"]
            p2_risk = hs_data["risk"]["p2_analysis"]

            properties = {
                "feature_id": original_feature["properties"]["feature_id"],
                "lst_c": original_feature["properties"]["lst_c"],
                "risk_category": p2_risk["risk_category"],
                "hotspot_context": p2_risk["hotspot_context"]
            }

            # Explicitly propagate the canonical hotspot_id from the backend evaluation
            hotspot_id = hs_data["risk"].get("hotspot_id")
            if hotspot_id is not None:
                properties["hotspot_id"] = hotspot_id
            features.append({
                "type": "Feature",
                "geometry": original_feature["geometry"],
                "properties": properties
            })

        return {
            "type": "FeatureCollection",
            "features": features
        }

    def get_hotspot_detail(self, city_id: str, feature_id: str) -> Dict[str, Any]:
        if city_id not in self.hotspots:
            return None
        return self.hotspots[city_id].get(feature_id)

data_store = DataStore()

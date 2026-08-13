"""
Interactive LST heat-layer generation for the Urban Heat Intelligence project.

This module:
1. Builds the validated LST composite.
2. Creates a visual heat representation.
3. Generates Earth Engine map tiles.
4. Returns metadata for frontend integration.

IMPORTANT:
The output represents Land Surface Temperature (LST),
not near-surface air temperature or human heat-health risk.
"""

import ee

from geospatial.src.earth_engine import initialize_earth_engine
from geospatial.src.lst_processor import get_lst_composite


PROJECT_ID = "cosmic-ascent-294213"


# Visualization palette.
# This is ONLY a visual representation of LST.
LST_PALETTE = [
    "313695",
    "4575B4",
    "74ADD1",
    "ABD9E9",
    "FFFFBF",
    "FEE090",
    "F46D43",
    "D73027",
    "A50026",
]


def create_heat_layer(city_key):
    """
    Create an Earth Engine tile layer for the city's LST composite.

    Returns:
        dict containing tile URL, statistics metadata and limitations.
    """

    initialize_earth_engine(PROJECT_ID)

    composite, scene_count = get_lst_composite(city_key)

    # Fixed visualization range for consistent comparison
    # between Mumbai and Dhanbad.
    vis_params = {
        "min": 25,
        "max": 55,
        "palette": LST_PALETTE,
        "opacity": 0.70,
    }

    map_id = composite.getMapId(vis_params)

    tile_url = map_id["tile_fetcher"].url_format

    return {
        "area_id": city_key,
        "data_type": "land_surface_temperature",
        "source": "Landsat 8/9 Collection 2 Level 2",
        "period": {
            "start": "2023-03-01",
            "end": "2023-05-31",
        },
        "unit": "celsius",
        "resolution_m": 30,
        "scene_count": scene_count,
        "tile_url": tile_url,
        "visualization": {
            "min_c": 25,
            "max_c": 55,
            "opacity": 0.70,
            "palette": LST_PALETTE,
        },
        "limitations": [
            "Represents Land Surface Temperature (LST), not near-surface air temperature.",
            "LST does not directly represent human thermal comfort or heat-health risk.",
            "Cloud, shadow and invalid pixels are masked.",
            "Visualization colors represent temperature ranges and are not additional measurements."
        ],
    }


if __name__ == "__main__":
    result = create_heat_layer("mumbai")

    print("\nHeat layer generated successfully.")
    print(f"Area: {result['area_id']}")
    print(f"Scenes: {result['scene_count']}")
    print(f"Tile URL:\n{result['tile_url']}")
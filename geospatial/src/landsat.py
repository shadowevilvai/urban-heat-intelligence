"""
Landsat data access and filtering utilities.

Retrieves Landsat 8 and Landsat 9 Collection 2 Level-2
imagery for the configured study areas.
"""

import sys
from pathlib import Path

import ee

PROJECT_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(PROJECT_ROOT))

from geospatial.Config.study_areas import (
    STUDY_AREAS,
    DEFAULT_DATE_RANGE,
)
from geospatial.src.earth_engine import initialize_earth_engine


LANDSAT_COLLECTIONS = {
    "landsat8": "LANDSAT/LC08/C02/T1_L2",
    "landsat9": "LANDSAT/LC09/C02/T1_L2",
}


def get_aoi(city_key):
    """Return the configured bounding-box geometry for a study area."""

    if city_key not in STUDY_AREAS:
        raise ValueError(
            f"Unknown study area '{city_key}'. "
            f"Available areas: {list(STUDY_AREAS)}"
        )

    bbox = STUDY_AREAS[city_key]["bbox"]
    return ee.Geometry.Rectangle(bbox)


def get_landsat_collection(
    city_key,
    satellite="landsat8",
    start_date=None,
    end_date=None,
):
    """Retrieve Landsat Collection 2 Level-2 imagery."""

    if satellite not in LANDSAT_COLLECTIONS:
        raise ValueError(
            f"Unknown satellite '{satellite}'. "
            f"Available options: {list(LANDSAT_COLLECTIONS)}"
        )

    start_date = start_date or DEFAULT_DATE_RANGE["start"]
    end_date = end_date or DEFAULT_DATE_RANGE["end"]

    aoi = get_aoi(city_key)

    collection = (
        ee.ImageCollection(LANDSAT_COLLECTIONS[satellite])
        .filterBounds(aoi)
        .filterDate(start_date, end_date)
    )

    return collection


def get_scene_count(
    city_key,
    satellite="landsat8",
    start_date=None,
    end_date=None,
):
    """Return the number of matching scenes."""

    collection = get_landsat_collection(
        city_key,
        satellite,
        start_date,
        end_date,
    )

    return collection.size().getInfo()


if __name__ == "__main__":
    initialize_earth_engine()

    for city in STUDY_AREAS:
        print(f"\n{STUDY_AREAS[city]['city']}")

        for satellite in LANDSAT_COLLECTIONS:
            count = get_scene_count(city, satellite)
            print(f"  {satellite}: {count} scenes")
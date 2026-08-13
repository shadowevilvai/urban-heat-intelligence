import sys
from pathlib import Path

# Allow imports from the project root.
PROJECT_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(PROJECT_ROOT))

from geospatial.Config.study_areas import STUDY_AREAS, DEFAULT_DATE_RANGE


def main():
    print("Study areas loaded successfully.")
    print()

    for key, area in STUDY_AREAS.items():
        print(f"{key}:")
        print(f"  City: {area['city']}")
        print(f"  State: {area['state']}")
        print(f"  BBox: {area['bbox']}")
        print()

    print("Date range:")
    print(f"  Start: {DEFAULT_DATE_RANGE['start']}")
    print(f"  End:   {DEFAULT_DATE_RANGE['end']}")


if __name__ == "__main__":
    main()
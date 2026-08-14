"""
Study area configuration for the Urban Heat Intelligence project.

The bounding boxes are currently used for development and validation.
They can be replaced with official municipal boundaries later.
"""

STUDY_AREAS = {
    "mumbai": {
        "city": "Mumbai",
        "state": "Maharashtra",
        "bbox": [72.80, 18.95, 72.95, 19.20],
    },
    "dhanbad": {
        "city": "Dhanbad",
        "state": "Jharkhand",
        "bbox": [86.30, 23.70, 86.55, 23.90],
    },
}

DEFAULT_DATE_RANGE = {
    "start": "2023-03-01",
    "end": "2023-05-31",
}
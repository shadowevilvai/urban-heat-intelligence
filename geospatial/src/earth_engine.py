"""
Reusable Google Earth Engine initialization.

Authentication is handled outside the repository.
The Cloud Project ID is supplied through the EE_PROJECT
environment variable.
"""

import os
import ee


DEFAULT_PROJECT = "cosmic-ascent-294213"


def initialize_earth_engine():
    """
    Initialize Google Earth Engine using the configured Cloud Project.
    """
    project = os.getenv("EE_PROJECT", DEFAULT_PROJECT)

    try:
        ee.Initialize(project=project)
    except Exception as exc:
        raise RuntimeError(
            f"Failed to initialize Google Earth Engine with project '{project}'. "
            "Make sure Earth Engine authentication is complete."
        ) from exc

    return project


if __name__ == "__main__":
    project = initialize_earth_engine()
    print("Earth Engine initialized successfully.")
    print(f"Project: {project}")
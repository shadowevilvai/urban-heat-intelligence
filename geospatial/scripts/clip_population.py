import os
import rasterio
from rasterio.windows import from_bounds

SOURCE = r"C:\Users\ADMIN\ind_pop_2023_CN_100m_R2025A_v1.tif"

OUTPUT_DIR = os.path.join(
    "geospatial",
    "outputs",
    "population"
)

os.makedirs(OUTPUT_DIR, exist_ok=True)

AOIS = {
    "mumbai": {
        "bounds": (72.80, 18.95, 72.95, 19.20)
    },
    "dhanbad": {
        "bounds": (86.30, 23.70, 86.55, 23.90)
    }
}

with rasterio.open(SOURCE) as src:

    print("CRS:", src.crs)
    print("Resolution:", src.res)

    for city, cfg in AOIS.items():

        bounds = cfg["bounds"]

        window = from_bounds(
            *bounds,
            transform=src.transform
        )

        data = src.read(1, window=window)

        profile = src.profile.copy()

        profile.update(
            width=data.shape[1],
            height=data.shape[0],
            transform=src.window_transform(window)
        )

        output_file = os.path.join(
            OUTPUT_DIR,
            f"{city}_population_2023.tif"
        )

        with rasterio.open(output_file, "w", **profile) as dst:
            dst.write(data, 1)

        print(f"Created -> {output_file}")
        print(f"Shape -> {data.shape}")
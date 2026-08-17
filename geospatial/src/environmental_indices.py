import ee
from geospatial.src.landsat import get_aoi

def mask_s2_clouds(image):
    """
    Masks clouds in Sentinel-2 using the Scene Classification Layer (SCL).
    Classes:
    4: Vegetation
    5: Not-vegetated
    6: Water
    7: Unclassified
    8: Cloud Medium Probability
    9: Cloud High Probability
    10: Thin Cirrus
    11: Snow/Ice
    We want to keep 4, 5, 6, 7 and maybe 1, 2, 3 (though 3 is cloud shadows, usually mask it).
    Let's just mask 3, 8, 9, 10, 11.
    """
    scl = image.select('SCL')
    # Create mask for pixels to EXCLUDE
    cloud_shadow_mask = scl.eq(3)
    cloud_med_mask = scl.eq(8)
    cloud_high_mask = scl.eq(9)
    cirrus_mask = scl.eq(10)
    snow_mask = scl.eq(11)

    # Combine masks
    bad_pixels = cloud_shadow_mask.Or(cloud_med_mask).Or(cloud_high_mask).Or(cirrus_mask).Or(snow_mask)

    # Keep pixels that are NOT bad
    return image.updateMask(bad_pixels.Not())

def get_sentinel2_indices(city_key, start_date, end_date):
    """
    Fetches Sentinel-2 imagery for the given city and date range,
    calculates NDVI, NDBI, and NDWI, and returns a median composite.
    """
    aoi = get_aoi(city_key)

    collection = (
        ee.ImageCollection("COPERNICUS/S2_SR_HARMONIZED")
        .filterBounds(aoi)
        .filterDate(start_date, end_date)
        .map(mask_s2_clouds)
    )

    def add_indices(img):
        # NDVI = (NIR - Red) / (NIR + Red) -> (B8 - B4) / (B8 + B4)
        ndvi = img.normalizedDifference(['B8', 'B4']).rename('NDVI_Mean')

        # NDBI = (SWIR1 - NIR) / (SWIR1 + NIR) -> (B11 - B8) / (B11 + B8)
        ndbi = img.normalizedDifference(['B11', 'B8']).rename('NDBI_Mean')

        # NDWI = (Green - NIR) / (Green + NIR) -> (B3 - B8) / (B3 + B8)
        ndwi = img.normalizedDifference(['B3', 'B8']).rename('NDWI_Mean')

        return img.addBands([ndvi, ndbi, ndwi])

    with_indices = collection.map(add_indices)

    # Median composite of the indices
    composite = with_indices.select(['NDVI_Mean', 'NDBI_Mean', 'NDWI_Mean']).median()
    return composite

def get_land_cover(city_key):
    """
    Fetches ESA WorldCover v200 (2021) and returns the 'Map' band.
    """
    aoi = get_aoi(city_key)
    dataset = ee.ImageCollection("ESA/WorldCover/v200").filterBounds(aoi)
    # It's an image collection with typically one image per tile for 2021
    # We take the mosaic to ensure full coverage of the AOI
    image = dataset.mosaic().select('Map').rename('Land_Cover_Class')

    return image

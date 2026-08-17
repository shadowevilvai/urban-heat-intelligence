"""
Land Surface Temperature (LST) processor for Landsat 8 and 9.
"""

import ee
import datetime
from geospatial.Config.study_areas import DEFAULT_DATE_RANGE, STUDY_AREAS
from geospatial.src.landsat import get_landsat_collection, get_aoi
from geospatial.src.environmental_indices import get_sentinel2_indices, get_land_cover

def apply_qa_mask(image):
    """
    Apply QA_PIXEL bitmask for Landsat 8/9 Collection 2 Level 2.
    Mask bits:
    0: Fill
    1: Dilated Cloud
    2: Cirrus
    3: Cloud
    4: Cloud Shadow
    5: Snow/Ice
    """
    qa = image.select('QA_PIXEL')

    # Bits 0-5 mask: 1 + 2 + 4 + 8 + 16 + 32 = 63
    mask = qa.bitwiseAnd(63).eq(0)

    return image.updateMask(mask)

def apply_st_scaling(image):
    """
    Convert ST_B10 to Celsius using scaling and offset.
    temperature_kelvin = ST_B10 * 0.00341802 + 149.0
    temperature_celsius = temperature_kelvin - 273.15
    """
    st_b10 = image.select('ST_B10')
    temp_c = st_b10.multiply(0.00341802).add(149.0).subtract(273.15)

    # Rename to LST_Celsius
    temp_c = temp_c.rename('LST_Celsius')

    return image.addBands(temp_c, overwrite=True)

def get_lst_composite(city_key, start_date=None, end_date=None,
                      calc_anomaly=True, baseline_start_year=2014, baseline_end_year=2023,
                      include_environmental=True):
    """
    Generate median LST composite for a given city.
    Optionally computes the historical anomaly and includes other environmental indices.
    """
    start_date = start_date or DEFAULT_DATE_RANGE["start"]
    end_date = end_date or DEFAULT_DATE_RANGE["end"]

    l8 = get_landsat_collection(city_key, satellite="landsat8", start_date=start_date, end_date=end_date)
    l9 = get_landsat_collection(city_key, satellite="landsat9", start_date=start_date, end_date=end_date)

    merged = l8.merge(l9)

    # Apply processing
    processed = merged.map(apply_qa_mask).map(apply_st_scaling)

    # Return median composite of LST_Celsius
    composite = processed.select('LST_Celsius').median()
    scene_count = merged.size().getInfo()

    # Calculate temporal valid_pixel_percent
    valid_count = processed.select('LST_Celsius').count().rename('count')
    total_count = merged.select('QA_PIXEL').count().rename('count')
    # Avoid division by zero by masking total_count > 0, though count() should handle this
    valid_percent = valid_count.divide(total_count.where(total_count.eq(0), 1)).multiply(100).rename('Valid_Pixel_Percent')
    composite = composite.addBands(valid_percent)

    if calc_anomaly:
        dt_start = datetime.datetime.strptime(start_date, "%Y-%m-%d")
        dt_end = datetime.datetime.strptime(end_date, "%Y-%m-%d")

        all_baseline_imgs = None
        for year in range(baseline_start_year, baseline_end_year + 1):
            start_month_day = dt_start.strftime('%m-%d')
            if start_month_day == '02-29' and not (year % 4 == 0 and (year % 100 != 0 or year % 400 == 0)):
                start_month_day = '02-28'

            end_month_day = dt_end.strftime('%m-%d')
            if end_month_day == '02-29' and not (year % 4 == 0 and (year % 100 != 0 or year % 400 == 0)):
                end_month_day = '02-28'

            bs_date = f"{year}-{start_month_day}"
            be_date = f"{year}-{end_month_day}"

            l8_base = get_landsat_collection(city_key, "landsat8", bs_date, be_date)
            l9_base = get_landsat_collection(city_key, "landsat9", bs_date, be_date)

            merged_base = l8_base.merge(l9_base)
            if all_baseline_imgs is None:
                all_baseline_imgs = merged_base
            else:
                all_baseline_imgs = all_baseline_imgs.merge(merged_base)

        if all_baseline_imgs is not None:
            baseline_processed = all_baseline_imgs.map(apply_qa_mask).map(apply_st_scaling)
            baseline_composite = baseline_processed.select('LST_Celsius').median().rename('LST_Baseline_Celsius')
            anomaly = composite.select('LST_Celsius').subtract(baseline_composite).rename('LST_Anomaly_Celsius')
            composite = composite.addBands([baseline_composite, anomaly])

    if include_environmental:
        s2_indices = get_sentinel2_indices(city_key, start_date, end_date)
        land_cover = get_land_cover(city_key)
        composite = composite.addBands([s2_indices, land_cover])

    return composite, scene_count

def compute_statistics(composite, city_key):
    """
    Compute LST statistics for the given composite over the city's AOI.
    """
    aoi = get_aoi(city_key)

    stats = composite.reduceRegion(
        reducer=ee.Reducer.minMax().combine(
            reducer2=ee.Reducer.mean(), sharedInputs=True
        ).combine(
            reducer2=ee.Reducer.median(), sharedInputs=True
        ).combine(
            reducer2=ee.Reducer.count(), sharedInputs=True
        ),
        geometry=aoi,
        scale=30,
        maxPixels=1e9
    ).getInfo()

    return {
        "min_c": stats.get('LST_Celsius_min'),
        "max_c": stats.get('LST_Celsius_max'),
        "mean_c": stats.get('LST_Celsius_mean'),
        "median_c": stats.get('LST_Celsius_median'),
        "valid_pixel_count": stats.get('LST_Celsius_count')
    }

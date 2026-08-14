"""
Land Surface Temperature (LST) processor for Landsat 8 and 9.
"""

import ee
from geospatial.Config.study_areas import DEFAULT_DATE_RANGE, STUDY_AREAS
from geospatial.src.landsat import get_landsat_collection, get_aoi

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

def get_lst_composite(city_key, start_date=None, end_date=None):
    """
    Generate median LST composite for a given city.
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
    return composite, merged.size().getInfo()

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

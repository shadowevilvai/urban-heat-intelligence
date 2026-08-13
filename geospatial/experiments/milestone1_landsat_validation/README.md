# Milestone 1: Landsat Data Source Validation

## Objective
Verify the availability of Landsat 8/9 Collection 2 Level 2 imagery for our Area of Interest (AOI) within the specified timeframe. This experiment satisfies the requirements of P1 Milestone 1 as defined in the project documentation.

## Running the Experiment

1. Ensure you have the Google Earth Engine Python API installed:
   ```bash
   pip install earthengine-api
   ```

2. If this is your first time using Earth Engine on this machine, authenticate:
   ```bash
   earthengine authenticate
   ```

3. Run the validation script:
   ```bash
   python validate_landsat.py
   ```

4. Check the generated `validation_result.json` file for the outputs (dataset ID, scene counts, cloud information, and usable scene counts).

## Important Notes
- The AOI used here is a temporary bounding box in Mumbai for fast validation. **The final AOI requires team confirmation.**
- The date range (2023-03-01 to 2023-05-31) is temporary and **requires team confirmation.**
- LST calculation is intentionally omitted from this step, as this is strictly a data availability check.

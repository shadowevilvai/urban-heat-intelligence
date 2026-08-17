# ml/demo.py
import json
from tests.test_fixtures import MOCK_HOTSPOT_GEOJSON
from api_handler import process_hotspot_feature

# 1. Grab a fake hotspot feature from our mock data (simulating P1 output)
raw_feature = MOCK_HOTSPOT_GEOJSON["features"][0]

# 2. Run it through our new P2 engine
enriched_feature = process_hotspot_feature(raw_feature)

# 3. Print the result nicely formatted!
print(json.dumps(enriched_feature, indent=2))

# Backend Phase 0 Audit

## 1. Executive Summary
The Urban Heat Intelligence project is progressing into the Backend Phase. Currently, the P1 (Geospatial), P2 (Risk/Context), and P3 (Optimization/Simulation) engines are locked, implemented, and validated purely as Python modules within the `ml/` directory. The primary objective of the backend is to expose these ML models via a well-structured, performant API for the frontend to consume, without duplicating any scientific logic or violating the established P1 → P2 → P3 source-of-truth boundaries. This audit recommends a **Python/FastAPI** architecture to seamlessly orchestrate the existing Python-based Pydantic schemas and ML engines.

## 2. Current Repository State
- **Branch:** `feature/backend`
- **P1 Data:** Stored statically as GeoJSON files in `geospatial/outputs/lst/` (Mumbai: 2294 features, Dhanbad: 2989 features).
- **P2 & P3 Logic:** Fully implemented in `ml/`. 
- **Frontend:** Exists in `frontend/` as a Vite + React + TypeScript application.
- **Backend:** Empty (only `backend/.gitkeep` exists).

## 3. Existing Backend Inventory
- **Code:** No existing backend code, controllers, or routes.
- **Dependencies:** No backend dependencies defined yet.
- **APIs:** No existing APIs.
- **Mock/Hardcoded:** The `ml/tests/` and `scratch/` directories contain mock setups and scripts for testing, but no production web server exists.

## 4. Frontend Dependency Inventory
- **Framework:** React 19 (via Vite) in `frontend/`.
- **Styling:** TailwindCSS v4.
- **Mapping:** `maplibre-gl` and `react-map-gl`.
- **API Utilities:** `@tanstack/react-query` is installed, indicating the frontend expects REST-like queries and caching.
- **Components:** `FeaturePanel.tsx` currently renders P1 data and placeholders for P2 data (`hotspot_score`, `confidence`). It handles a `SpatialFeature` type mapped directly to P1 output. 
- **Backend Assumptions:** Frontend uses relative or configurable endpoints (not hardcoded to a specific backend yet), but expects JSON responses matching the P1/P2 structural logic.

## 5. P1 → P2 → P3 Execution Trace
**A. Obtaining P1:**
- Read GeoJSON from `geospatial/outputs/lst/mumbai_lst_spatial.geojson`. Features are dictionaries containing P1 `properties`.

**B. Passing P1 to Canonical P2:**
- Use `ml/api_handler.py`. Function: `process_hotspot_feature(feature_dict)`.

**C. Producing the P2 Result:**
- `process_hotspot_feature` validates via `P1Feature` schema, runs `adapt_p1_to_p2`, normalizes via `preprocess_features`, and calculates risk via `calculate_risk`. It returns a dictionary representing the canonical P2 output (including `p2_analysis`).

**D. Passing P2 into P3:**
- P3 is invoked via `ml/optimization/optimizer.py` calling `default_optimizer.optimize(request, hotspots_data)`.
- `hotspots_data` is a list of tuples: `(hotspot_id, p1_dict, p2_dict)`.

**E. Exact P3 Schema Required:**
- `ml.optimization.schemas.OptimizeRequest` (requires `resource_budget` and a list of `interventions`).

**F. Exact P3 Result Returned:**
- `ml.optimization.schemas.OptimizeResponse` (contains portfolio objective, total expected cooling, and detailed `hotspot_allocations`).

**G. Process:**
- Everything runs synchronously in a single Python process. No separate service is strictly required for the ML engines.

**H. Path/Import Implications:**
- The backend must manipulate `sys.path` or use a proper Python package structure to import from the sibling `ml/` directory.

## 6. Current Data Flow
Currently, there is no end-to-end data flow because the backend is missing. The P1/P2/P3 models only flow via localized test scripts (e.g., `scratch/run_real_data.py`).

## 7. Recommended Backend Architecture
**Recommendation:** **Python with FastAPI**
- **Why:** 
  1. **Native Integration:** P1/P2/P3 are written in Python and heavily leverage Pydantic (`ml/optimization/schemas.py`, `ml/schemas.py`). FastAPI natively uses Pydantic for request/response validation, allowing us to directly expose the existing schemas as API contracts.
  2. **Performance:** FastAPI is asynchronous and high-performance, suitable for serving ~5,000 spatial features.
  3. **Maintainability:** Avoids rewriting complex optimization (SciPy HiGHS solver) and simulation logic into Node.js/TypeScript. 

## 8. Proposed API Architecture
The API should follow a stateless, RESTful design, exposing resources for cities, spatial map data, and optimization scenarios.

- **`GET /api/health`**: System status.
- **`GET /api/cities`**: List available cities.
- **`GET /api/cities/{city_id}/map`**: Fetch GeoJSON for map rendering.
- **`GET /api/hotspots/{city_id}/{feature_id}`**: Fetch canonical P1/P2 data for a specific feature.
- **`POST /api/optimization/optimize`**: Run P3 optimization across a city or selected hotspots.

## 9. Endpoint Specification

### `GET /api/cities/{city_id}/map`
- **Purpose**: Serve the P1 GeoJSON features for map rendering.
- **Params**: `city_id` (e.g., "mumbai").
- **Response**: GeoJSON FeatureCollection.
- **Behavior**: Should return a simplified version of P1 + basic P2 (risk category) to keep payload sizes small.

### `GET /api/hotspots/{city_id}/{feature_id}`
- **Purpose**: Retrieve detailed P1 observation and canonical P2 risk analysis.
- **Params**: `city_id`, `feature_id`.
- **Response**: Canonical P2 dictionary output from `ml.api_handler.process_hotspot_feature`.
- **Behavior**: Fetches P1 feature, runs canonical P2 on-the-fly (or from cache), and returns it.

### `POST /api/optimization/optimize`
- **Purpose**: Run the P3 optimizer over a set of hotspots.
- **Body**: `OptimizeRequest` (budget, target hotspots, enabled interventions).
- **Response**: `OptimizeResponse`.
- **Behavior**: Fetches P1/P2 data for requested hotspots, passes them to `default_optimizer.optimize`, and returns the results.

## 10. Request/Response Contracts
- Backend will strictly use the Pydantic schemas defined in `ml/optimization/schemas.py` for all P3 requests and responses.
- Backend will use the dictionary output from `ml/api_handler.py` as the contract for P2 hotspot details.

## 11. Map Data Strategy
**Recommendation: Option D - Hybrid Approach**
- **Total Features:** ~5,283 (Mumbai + Dhanbad).
- **Strategy:** Serve a lightweight GeoJSON FeatureCollection via `/api/cities/{city_id}/map`. The `properties` should only contain `feature_id`, `risk_category`, `hotspot_context`, and essential map-rendering indicators (e.g., `lst_c`). 
- When a user clicks a hotspot on the frontend, the frontend calls `/api/hotspots/{city_id}/{feature_id}` to retrieve the comprehensive scientific data, provenance, and contributors.
- **Why:** Preserves scientific completeness in the detail view while ensuring fast MapLibre vector tile generation and minimal payload size (sub-megabyte) on initial load.

## 12. P1/P2/P3 Source-of-Truth Boundaries
- **P1:** Owns geometry, observations (LST), derived indicators (NDVI), and provenance. Backend merely reads this.
- **P2:** Owns risk scores, vulnerabilities, and context classification. Backend MUST call `api_handler.py` to get this; frontend MUST NOT calculate it.
- **P3:** Owns suitability, bounds, simulation, and allocation. Backend MUST call `optimizer.py`; frontend MUST NOT simulate cooling.
- **Backend:** Owns routing, caching, and HTTP transport. MUST NOT recreate ML math.
- **Frontend:** Owns map rendering, UI state, and user interaction.

*Violation Check:* The frontend currently mocks `hotspot_score` in `FeaturePanel.tsx`. This must be updated to consume the backend API once available.

## 13. Performance & Caching Strategy
- **GeoJSON Caching:** The backend should load the P1 GeoJSON files into memory at startup. Reading from disk on every map request will bottleneck.
- **P2 Caching:** P2 calculations are deterministic. The backend should cache the canonical P2 output per `feature_id` (e.g., using `functools.lru_cache` or a simple dict) since the underlying P1 data is static.
- **P3 Execution:** Optimization involves SciPy linear programming which is computationally intensive. Optimization requests should NOT be cached aggressively if user inputs (budget, constraints) change dynamically, but repeated identical requests can be cached.

## 14. Error Handling Strategy
- **404 Not Found**: Unknown `city_id` or `feature_id`.
- **400 Bad Request**: Invalid optimization budget, unknown intervention type, or malformed P3 request schema.
- **422 Unprocessable Entity**: FastAPIs default for Pydantic validation failures.
- **500 Internal Server Error**: LP solver failures, unexpected P2/P3 exceptions.
- **Response Structure**:
  ```json
  {
    "error": "Not Found",
    "message": "Feature ID not found in Mumbai dataset.",
    "code": 404
  }
  ```

## 15. Security Audit
- **Current State:** The repository contains no exposed secrets in tracked files. `.env.example` is clean. 
- **CORS:** Backend must explicitly configure CORS to allow requests from the Vite frontend (usually `http://localhost:5173`).
- **Path Traversal:** File loading logic for `geospatial/outputs/lst/*.geojson` must validate `city_id` against a strict whitelist (e.g., `["mumbai", "dhanbad"]`) to prevent arbitrary file reads.

## 16. Configuration Strategy
- **Backend Environment:** Will require a `.env` file within `backend/`.
- **Keys needed:**
  - `FRONTEND_URL` (for CORS).
  - `DATA_DIR` (relative path to `../geospatial/outputs/lst`).
  - `ENVIRONMENT` (dev/prod).

## 17. Testing Strategy
- **Unit Tests (`backend/tests/`)**:
  - Test FastAPI route handlers with mocked ML functions.
  - Test `city_id` validation and 404 logic.
- **Integration Tests**:
  - `P1 -> Backend -> P2`: Verify `/api/hotspots/{city_id}/{feature_id}` perfectly matches `api_handler.py` output.
  - `P1 -> Backend -> P3`: Verify `/api/optimization/optimize` accurately pipes data to `default_optimizer` and returns expected constraints.
- **Regression**: The backend tests must enforce that the API outputs do not deviate mathematically from the locked P1/P2/P3 model outputs.

## 18. Deployment Considerations
- **Python Version**: Ensure consistency with the `ml/` environment (Python 3.10+).
- **Docker**: A `Dockerfile` will be required to containerize the FastAPI app, copying both `backend/`, `ml/`, and `geospatial/` directories into the image.

## 19. Risks / Open Questions
- **Risk:** Path resolution between `backend/` and `ml/`. If deployed improperly, the backend won't find the ML modules.
- **Risk:** P3 Optimization over 3,000 hotspots simultaneously might cause HTTP timeouts if the SciPy HiGHS solver takes too long. 
- **Open Question:** Should optimization be restricted to a sub-selection of hotspots (e.g., top 100 highest risk) to guarantee sub-second API response times?

## 20. Backend Implementation Roadmap
1. Initialize FastAPI project in `backend/`.
2. Configure CORS, error handlers, and logging.
3. Implement in-memory Data Access Layer (DAL) to load GeoJSON on startup.
4. Build `/api/cities/{city_id}/map` endpoint.
5. Build `/api/hotspots/{city_id}/{feature_id}` endpoint incorporating `ml/api_handler.py`.
6. Build `/api/optimization/optimize` endpoint incorporating `ml/optimization/optimizer.py`.
7. Write backend integration tests.

## 21. Explicit Non-Goals
- Do NOT rewrite or duplicate P2 risk normalization logic.
- Do NOT rewrite or duplicate P3 suitability rules or optimization bounds.
- Do NOT implement database persistence (PostgreSQL/MongoDB) for P1 data; it remains static GeoJSON.
- Do NOT fabricate fake hotspot data for testing.

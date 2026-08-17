from fastapi import APIRouter, HTTPException
from backend.api_schemas import OptimizationTransportRequest
from backend.config import settings
from backend.data_store import data_store

from ml.optimization.schemas import OptimizeRequest, OptimizeResponse
from ml.optimization.optimizer import default_optimizer
import logging
import time

logger = logging.getLogger(__name__)
router = APIRouter()

@router.post("/optimize", response_model=OptimizeResponse)
def optimize_hotspots(request: OptimizationTransportRequest):
    if len(request.hotspot_ids) > settings.max_optimization_hotspots:
        raise HTTPException(
            status_code=400,
            detail={
                "error": "limit_exceeded",
                "message": f"Optimization request exceeds maximum allowed hotspots ({settings.max_optimization_hotspots}).",
                "code": 400
            }
        )

    city_id = request.city_id
    if city_id not in data_store.allowed_cities:
        raise HTTPException(status_code=404, detail="City not found")
        
    # Gather canonical P1 and P2 data for the requested hotspots
    hotspots_data = []
    for hs_id in request.hotspot_ids:
        detail = data_store.get_hotspot_detail(city_id, hs_id)
        if not detail:
            raise HTTPException(
                status_code=404, 
                detail={
                    "error": "not_found",
                    "message": f"Feature {hs_id} not found in city {city_id}.",
                    "code": 404
                }
            )
            
        hotspots_data.append((hs_id, detail["feature"]["properties"], detail["risk"]))
        
    # Build canonical request
    canonical_request = OptimizeRequest(
        hotspot_ids=request.hotspot_ids,
        resource_budget=request.resource_budget,
        interventions=request.interventions
    )
    
    start_time = time.time()
    try:
        response = default_optimizer.optimize(canonical_request, hotspots_data)
        execution_time = time.time() - start_time
        logger.info(f"Optimization completed in {execution_time:.3f} seconds for {len(request.hotspot_ids)} hotspots.")
        return response
    except ValueError as ve:
        raise HTTPException(
            status_code=400,
            detail={
                "error": "invalid_request",
                "message": str(ve),
                "code": 400
            }
        )
    except Exception as e:
        logger.error(f"Optimization failed: {e}")
        raise HTTPException(
            status_code=500,
            detail={
                "error": "internal_error",
                "message": "Optimization failed due to an internal error.",
                "code": 500
            }
        )

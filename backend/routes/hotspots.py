from fastapi import APIRouter, HTTPException
from backend.data_store import data_store
from backend.api_schemas import HotspotDetailResponse

router = APIRouter()

@router.get("/{city_id}/{feature_id}", response_model=HotspotDetailResponse)
def get_hotspot_detail(city_id: str, feature_id: str):
    if city_id not in data_store.allowed_cities:
        raise HTTPException(status_code=404, detail="City not found")
        
    detail = data_store.get_hotspot_detail(city_id, feature_id)
    if not detail:
        raise HTTPException(status_code=404, detail="Feature not found")
        
    return detail

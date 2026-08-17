from fastapi import APIRouter, HTTPException
from backend.data_store import data_store
from backend.api_schemas import MapFeatureCollection

router = APIRouter()

@router.get("")
def list_cities():
    if not data_store._initialized:
        raise HTTPException(status_code=503, detail="Data store not initialized")
    return list(data_store.cities.values())

@router.get("/{city_id}/map", response_model=MapFeatureCollection)
def get_city_map(city_id: str):
    if city_id not in data_store.allowed_cities:
        raise HTTPException(status_code=404, detail="City not found")
        
    feature_collection = data_store.get_city_map(city_id)
    if not feature_collection:
        raise HTTPException(status_code=404, detail="Data for city not found")
        
    return feature_collection

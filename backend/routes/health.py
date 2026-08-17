from fastapi import APIRouter
from backend.data_store import data_store

router = APIRouter()

@router.get("")
def health_check():
    return {
        "status": "ok",
        "environment": "development", # In a real app this would read from settings
        "loaded_cities": data_store.allowed_cities,
        "dataset_loaded": data_store._initialized
    }

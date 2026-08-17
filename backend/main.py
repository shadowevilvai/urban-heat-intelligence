import sys
import pathlib

# Ensure we can import 'ml' directly
root_dir = pathlib.Path(__file__).parent.parent.resolve()
if str(root_dir) not in sys.path:
    sys.path.append(str(root_dir))

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import logging

from backend.config import settings
from backend.data_store import data_store

from backend.routes.health import router as health_router
from backend.routes.cities import router as cities_router
from backend.routes.hotspots import router as hotspots_router
from backend.routes.optimization import router as optimization_router

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def lifespan(app: FastAPI):
    logger.info("Initializing DataStore...")
    data_store.initialize()
    logger.info("DataStore initialized successfully.")
    yield
    logger.info("Shutting down...")

app = FastAPI(title="Urban Heat Intelligence API", lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[settings.frontend_url],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(health_router, prefix="/api/health", tags=["health"])
app.include_router(cities_router, prefix="/api/cities", tags=["cities"])
app.include_router(hotspots_router, prefix="/api/hotspots", tags=["hotspots"])
app.include_router(optimization_router, prefix="/api/optimization", tags=["optimization"])

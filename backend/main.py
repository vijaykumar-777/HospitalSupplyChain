"""FastAPI application entry point."""
import logging
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from backend.database import engine, Base
from backend.models import *  # noqa — ensure all models register with Base
from backend.routers import orders, suppliers, inventory, purchase_orders, grn, predictions, disaster
from backend.settings import ENABLE_SCHEDULER
from backend.services.scheduler import start_scheduler, stop_scheduler

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    Base.metadata.create_all(bind=engine)
    if ENABLE_SCHEDULER:
        start_scheduler()
    logger.info("Hospital Supply Chain API started")
    yield
    # Shutdown
    if ENABLE_SCHEDULER:
        stop_scheduler()
    logger.info("Hospital Supply Chain API stopped")


app = FastAPI(
    title="Hospital Supply Chain API",
    description="Delivery Delay & Disaster Prediction System",
    version="1.0.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Register routers
app.include_router(orders.router)
app.include_router(suppliers.router)
app.include_router(inventory.router)
app.include_router(purchase_orders.router)
app.include_router(grn.router)
app.include_router(predictions.router)
app.include_router(disaster.router)


@app.get("/")
def root():
    return {"status": "ok", "service": "Hospital Supply Chain API", "version": "1.0.0"}


@app.get("/api/health")
def health():
    return {"status": "healthy"}

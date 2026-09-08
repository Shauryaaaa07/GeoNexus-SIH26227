from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
import os

from api.semantic_routes import router as semantic_router
from api.analysis_routes import router as analysis_router
from api.location_routes import router as location_router
from api.satellite_routes import router as satellite_router
from api.change_routes import router as change_router

app = FastAPI(
    title="SIH26227 Satellite Change Detection API",
    description="Backend API for satellite imagery search and multi-temporal change analysis.",
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

os.makedirs("data/images", exist_ok=True)

app.mount(
    "/images",
    StaticFiles(directory="data/images"),
    name="images"
)

app.include_router(location_router)
app.include_router(satellite_router)
app.include_router(change_router)
app.include_router(analysis_router)
app.include_router(semantic_router)


@app.get("/")
def read_root():
    return {
        "status": "online",
        "service": "SIH26227 Satellite Change Detection API"
    }
from fastapi import APIRouter
from fastapi.responses import FileResponse
import os

router = APIRouter()

@router.get("/api/map-data/lakes")
async def get_lakes_geojson():
    file_path = os.path.join(os.path.dirname(__file__), "..", "data", "lakes", "lakes.geojson")
    if os.path.exists(file_path):
        return FileResponse(file_path, media_type="application/json")
    return {"type": "FeatureCollection", "features": []}

@router.get("/api/map-data/rivers")
async def get_rivers_geojson():
    file_path = os.path.join(os.path.dirname(__file__), "..", "data", "rivers", "rivers.geojson")
    if os.path.exists(file_path):
        return FileResponse(file_path, media_type="application/json")
    return {"type": "FeatureCollection", "features": []}

@router.get("/api/map-data/relationships")
async def get_relationships():
    file_path = os.path.join(os.path.dirname(__file__), "..", "data", "lake_river_relationships.json")
    if os.path.exists(file_path):
        return FileResponse(file_path, media_type="application/json")
    return {"relationships": []}

@router.get("/api/map-data")
async def get_map_data():
    return {
        "message": "Use /api/map-data/lakes, /api/map-data/rivers, and /api/map-data/relationships"
    }

from fastapi import APIRouter
from app.core.database import get_db

router = APIRouter()

@router.get("/lakes")
async def get_lakes():
    db = get_db()
    lakes_cursor = db["lakes"].find({})
    features = []
    
    async for lake in lakes_cursor:
        features.append({
            "type": "Feature",
            "geometry": {
                "type": "Point",
                "coordinates": [lake["longitude"], lake["latitude"]]
            },
            "properties": {
                "id": lake["id"],
                "name": lake["name"],
                "glacier_name": lake.get("glacier_name", ""),
                "country": lake.get("country", ""),
                "region": lake.get("region", ""),
                "elevation": lake.get("elevation", 0),
                "area_km2": lake.get("lake_area", 0),
                "basin": lake.get("basin", ""),
                "risk": lake.get("current_risk", "UNKNOWN"),
                "connected_river": lake.get("connected_river", "")
            }
        })
        
    return {"type": "FeatureCollection", "features": features}

@router.get("/rivers")
async def get_rivers():
    db = get_db()
    rivers_cursor = db["rivers"].find({})
    features = []
    
    async for river in rivers_cursor:
        geojson_path = river.get("geojson_path")
        if not geojson_path:
            continue
            
        features.append({
            "type": "Feature",
            "geometry": geojson_path,
            "properties": {
                "id": river["id"],
                "name": river["name"],
                "country": river.get("country", ""),
                "basin": river.get("basin", "")
            }
        })
        
    return {"type": "FeatureCollection", "features": features}

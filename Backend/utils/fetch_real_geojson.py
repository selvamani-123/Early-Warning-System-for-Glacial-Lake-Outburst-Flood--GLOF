import httpx
import json
import os
import asyncio

async def fetch_overpass_geojson(query: str, output_path: str):
    print(f"Fetching real GeoJSON data for {output_path} via Overpass API...")
    url = "https://overpass-api.de/api/interpreter"
    
    try:
        # Overpass query to get JSON
        async with httpx.AsyncClient(timeout=60.0) as client:
            resp = await client.post(url, data={"data": query})
            resp.raise_for_status()
            osm_data = resp.json()
            
        # Very simplified conversion from OSM JSON to GeoJSON
        # Real HydroRIVERS/HydroLAKES would be processed via GDAL/ogr2ogr
        features = []
        nodes = {node["id"]: [node["lon"], node["lat"]] for node in osm_data.get("elements", []) if node["type"] == "node"}
        
        for element in osm_data.get("elements", []):
            if element["type"] == "way":
                coords = [nodes[n] for n in element["nodes"] if n in nodes]
                if coords:
                    is_polygon = coords[0] == coords[-1] and len(coords) >= 4
                    geom_type = "Polygon" if is_polygon else "LineString"
                    geometry_coords = [coords] if is_polygon else coords
                    
                    features.append({
                        "type": "Feature",
                        "properties": element.get("tags", {}),
                        "geometry": {
                            "type": geom_type,
                            "coordinates": geometry_coords
                        }
                    })
                    
        geojson = {
            "type": "FeatureCollection",
            "features": features
        }
        
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        with open(output_path, "w", encoding="utf-8") as f:
            json.dump(geojson, f, indent=2)
        print(f"Successfully saved {len(features)} features to {output_path}")
        
    except Exception as e:
        print(f"Failed to fetch data for {output_path}: {e}")

async def main():
    # Bounding box around a glacial region (e.g., Sikkim Himalayas near South Lhonak)
    bbox = "27.7,88.1,28.0,88.4"
    
    lakes_query = f"""
    [out:json][timeout:25];
    (
      way["natural"="water"]({bbox});
      way["waterway"="glacier"]({bbox});
    );
    out body;
    >;
    out skel qt;
    """
    
    rivers_query = f"""
    [out:json][timeout:25];
    (
      way["waterway"="river"]({bbox});
      way["waterway"="stream"]({bbox});
    );
    out body;
    >;
    out skel qt;
    """
    
    await fetch_overpass_geojson(lakes_query, "../data/lakes/lakes.geojson")
    await fetch_overpass_geojson(rivers_query, "../data/rivers/rivers.geojson")

if __name__ == "__main__":
    asyncio.run(main())

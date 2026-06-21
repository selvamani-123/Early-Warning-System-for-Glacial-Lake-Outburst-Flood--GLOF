from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.staticfiles import StaticFiles
import logging

from utils.database import connect_to_mongo, close_mongo_connection
from utils.background_jobs import start_scheduler
from routes import predictions, analytics, alerts, map_data, websocket

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(
    title="GLOF Sentinel API",
    description="Early Warning System for Glacial Lake Outburst Floods powered by Machine Learning",
    version="2.0.0"
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# MongoDB Lifecycle
@app.on_event("startup")
async def startup_db_client():
    await connect_to_mongo()
    start_scheduler()

@app.on_event("shutdown")
async def shutdown_db_client():
    await close_mongo_connection()

# Include Routers
app.include_router(predictions.router)
app.include_router(analytics.router)
app.include_router(alerts.router)
app.include_router(map_data.router)
app.include_router(websocket.router)

@app.exception_handler(Exception)
async def global_exception_handler(request, exc):
    logger.error(f"Global error: {exc}")
    return JSONResponse(
        status_code=500,
        content={"message": "An unexpected error occurred."}
    )

# Serve Vanilla HTML Frontend
app.mount("/", StaticFiles(directory="../Frontend", html=True), name="static")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)

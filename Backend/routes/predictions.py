from fastapi import APIRouter
from models.domain import PredictionRequest, PredictionResponse
from models.db_models import DBPrediction
from services.ml_service import ml_service
from services.alert_engine import AlertEngine
from utils.database import get_db

router = APIRouter()

@router.post("/api/predict", response_model=PredictionResponse)
async def predict_risk(req: PredictionRequest):
    # ML Inference
    risk, probability, feature_importance = ml_service.predict(req)
    
    # Store prediction
    db_pred = DBPrediction(
        risk=risk,
        probability=probability,
        inputs=req.model_dump()
    )
    
    db = get_db()
    if db is not None:
        await db.predictions.insert_one(db_pred.model_dump())
        
    # Process potential alerts
    # In a real system, we'd pass the specific lake ID if it was part of the request
    await AlertEngine.process_prediction(risk, "Global_API_Req")
        
    return PredictionResponse(risk=risk, probability=probability, feature_importance=feature_importance)

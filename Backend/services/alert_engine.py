from utils.database import get_db
from models.db_models import DBAlert

class AlertEngine:
    @staticmethod
    async def process_prediction(risk: str, lake_id: str):
        """
        Determines if an alert should be generated based on risk.
        Saves alert to DB.
        """
        if risk == "LOW":
            return None
            
        messages = {
            "MODERATE": f"Advisory: Elevated risk conditions detected at {lake_id}.",
            "HIGH": f"Warning: High risk of GLOF at {lake_id}. Monitor closely.",
            "CRITICAL": f"Emergency: CRITICAL risk at {lake_id}. Evacuation recommended."
        }
        
        alert = DBAlert(
            severity=risk,
            message=messages.get(risk, "Unknown Risk.")
        )
        
        # Save to DB
        db = get_db()
        if db is not None:
            await db.alerts.insert_one(alert.model_dump())
            
        return alert

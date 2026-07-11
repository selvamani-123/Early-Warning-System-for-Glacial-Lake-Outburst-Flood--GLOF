import logging
from app.services.ai_risk_engine import ai_risk_engine
from app.services.river_impact import river_impact_service
from app.models.domain.risk import RiskAssessment
from typing import Dict, Any

logger = logging.getLogger(__name__)

class DecisionSupportService:
    def evaluate_lake_situation(self, lake_id: str, weather_data: Dict[str, Any], lake_data: Dict[str, Any]) -> RiskAssessment:
        """
        Layer 6: Decision Support
        Answers what is happening, why, and which rivers/settlements are affected.
        """
        # 1. Ask AI Risk Engine for current risk estimate (Layer 4)
        risk_assessment = ai_risk_engine.assess_risk(lake_id, weather_data, lake_data)
        
        # 2. Map lake to downstream rivers (Layer 5)
        affected_rivers = river_impact_service.get_downstream_rivers(lake_id)
        risk_assessment.affected_rivers = affected_rivers
        
        # 3. Enhance recommended actions based on settlements
        for river in affected_rivers:
            settlements = river_impact_service.get_vulnerable_settlements(river)
            for settlement in settlements:
                risk_assessment.recommended_actions.append(
                    f"Notify local authorities in {settlement.name} ({settlement.distance_from_source_km}km downstream)."
                )

        return risk_assessment

decision_support_service = DecisionSupportService()

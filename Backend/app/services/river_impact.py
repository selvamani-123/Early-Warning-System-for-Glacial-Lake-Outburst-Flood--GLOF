import logging
from typing import List
from app.models.domain.river import Settlement

logger = logging.getLogger(__name__)

class RiverImpactService:
    def get_downstream_rivers(self, lake_id: str) -> List[str]:
        """
        Identify which rivers are directly connected downstream of the given lake.
        """
        # Mock logic
        if lake_id == "south_lhonak":
            return ["Teesta River", "Teesta Basin"]
        return ["Unknown River System"]

    def get_vulnerable_settlements(self, river_name: str) -> List[Settlement]:
        """
        Retrieve settlements along the impact zone of a river.
        """
        if river_name == "Teesta River":
            return [
                Settlement(name="Chungthang", distance_from_source_km=15.0),
                Settlement(name="Mangan", distance_from_source_km=30.0)
            ]
        return []

river_impact_service = RiverImpactService()

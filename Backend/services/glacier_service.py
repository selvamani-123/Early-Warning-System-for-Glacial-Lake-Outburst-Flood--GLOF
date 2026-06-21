class GlacierService:
    @staticmethod
    def get_glacier_data(lake_id: str):
        """
        Retrieves static/dynamic glacier data from our cache/database.
        In production, this could query GLIMS or NASA EarthData endpoints.
        """
        # Hardcoded static data for demonstration based on our dataset_builder
        # In a real system, we'd query MongoDB or GLIMS API based on coordinates
        
        glaciers = {
            "Imja Tsho": {"lat": 27.89, "lon": 86.92, "elevation": 5010, "lake_area": 1.28, "glacier_area": 4.5},
            "Tsho Rolpa": {"lat": 27.88, "lon": 86.48, "elevation": 4580, "lake_area": 1.54, "glacier_area": 12.0},
        }
        
        return glaciers.get(lake_id, {"lat": 0, "lon": 0, "elevation": 5000, "lake_area": 1.0, "glacier_area": 5.0})

from datetime import datetime
import math

class DataValidator:
    @staticmethod
    def is_valid_location(lat: float, lon: float) -> bool:
        if lat is None or lon is None: return False
        if not (-90 <= lat <= 90): return False
        if not (-180 <= lon <= 180): return False
        return True

    @staticmethod
    def is_valid_numeric(value: float) -> bool:
        if value is None: return False
        if math.isnan(value) or math.isinf(value): return False
        return True

    @staticmethod
    def validate_weather(temp: float, rainfall: float) -> bool:
        if not DataValidator.is_valid_numeric(temp): return False
        if not DataValidator.is_valid_numeric(rainfall): return False
        # Earth historical extreme checks
        if temp < -89.2 or temp > 56.7: return False 
        if rainfall < 0: return False
        return True
        
    @staticmethod
    def validate_discharge(discharge: float) -> bool:
        if not DataValidator.is_valid_numeric(discharge): return False
        if discharge < 0: return False
        return True

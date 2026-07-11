import joblib
import logging
import os
import random
import asyncio
from typing import Dict, Any, List, Optional
from datetime import datetime
from pydantic import BaseModel, Field
from app.services.environmental_stress import calculate_environmental_stress

# We might want to redefine RiskAssessment here or import it if the schema differs slightly
# Since the user asked for assessment_mode, risk_trend, etc., we'll add them to the returned dict.

logger = logging.getLogger(__name__)

# The model is strictly loaded from Backend/glof_model.pkl
MODEL_PATH = os.path.join(os.path.dirname(__file__), '..', '..', 'glof_model.pkl')

class FeatureContribution(BaseModel):
    feature: str
    contribution_percent: float

class DecisionSupport(BaseModel):
    overall_situation: str
    current_status: str
    why_occurred: str
    recommended_actions: List[str]
    affected_river: str
    affected_settlements: List[str]
    last_update_time: datetime

class AssessmentResult(BaseModel):
    lake_id: str
    timestamp: datetime
    assessment_mode: str
    risk_level: str
    risk_trend: str
    environmental_stress_score: float
    environmental_stress_category: str
    confidence_score: float
    probabilities: Dict[str, float]
    feature_contributions: List[FeatureContribution]
    explanation: str
    decision_support: DecisionSupport
    engineered_features: Dict[str, float]

class AIRiskEngine:
    def __init__(self):
        self.model = None
        self._load_model()

    def _load_model(self):
        try:
            if os.path.exists(MODEL_PATH):
                self.model = joblib.load(MODEL_PATH)
                logger.info(f"Successfully loaded ML model from {MODEL_PATH}")
            else:
                logger.warning(f"ML model not found at {MODEL_PATH}. Falling back to Rule Engine Mode.")
        except Exception as e:
            logger.error(f"Failed to load AI model: {e}")

    def engineer_features(self, weather: Dict[str, Any], lake_graph: Dict[str, Any]) -> Dict[str, float]:
        """
        Step 3: Feature Engineering
        Computes the derived features precisely as defined in MODEL_VALIDATION_REPORT.txt
        """
        lake_meta = lake_graph.get("lake", {})
        glacier_meta = lake_graph.get("glacier", {})
        weather_hist = lake_graph.get("weather_history", {})
        
        T = weather.get("temperature", 0.0)
        rainfall = weather.get("rainfall", 0.0)
        elev = lake_meta.get("elevation", 4000.0)
        lake_area = lake_meta.get("lake_area", 1.0)
        
        # Historical Baselines
        hist_rainfall = weather_hist.get("annual_precip_mm", 1000.0) / 365.0 # Daily avg
        hist_rainfall = max(hist_rainfall, 1.0) # Avoid div zero
        hist_temp = weather_hist.get("avg_annual_temp_c", 0.0)
        
        # 1. Melt Rate Index: max(0,T) x (elev/5000) x 0.1
        melt_rate_index = max(0, T) * (elev / 5000.0) * 0.1
        
        # 2. Rainfall Intensity: rainfall / historical daily avg (or 5.0 as per report)
        rainfall_intensity = rainfall / 5.0
        
        # 3. Water Accumulation Score: (rainfall + melt*50) / max(0.1, lake_area)
        water_accumulation_score = (rainfall + melt_rate_index * 50) / max(0.1, lake_area)
        
        # 4. Seasonal Index
        month = datetime.utcnow().month
        season_mult = 1.5 if month in [6,7,8,9] else (1.2 if month in [5,10] else 1.0)
        seasonal_index = season_mult * (1 + max(0, T) / 20.0)
        
        # 5. Temperature Anomaly
        temp_anomaly = T - hist_temp
        
        # 6. Rainfall Anomaly
        rainfall_anomaly = rainfall - hist_rainfall

        return {
            "rainfall": rainfall,
            "temperature": T,
            "humidity": weather.get("humidity", 50.0),
            "lake_area": lake_area,
            "glacier_area": glacier_meta.get("area_km2", 10.0),
            "elevation": elev,
            "melt_rate_index": melt_rate_index,
            "rainfall_intensity": rainfall_intensity,
            "water_accumulation_score": water_accumulation_score,
            "seasonal_index": seasonal_index,
            "temp_anomaly": temp_anomaly,
            "rainfall_anomaly": rainfall_anomaly
        }

    def _rule_engine_inference(self, features: Dict[str, float]) -> Dict[str, Any]:
        """
        Fallback Scientific Rule Engine based strictly on Section 12 of the Model Validation Report.
        """
        ri = features["rainfall_intensity"]
        was = features["water_accumulation_score"]
        mri = features["melt_rate_index"]
        
        if (ri > 5.0 and was > 50) or (mri > 2.0 and was > 60):
            risk = "CRITICAL"
            probs = {"LOW": 0.0, "MODERATE": 0.05, "HIGH": 0.15, "CRITICAL": 0.8}
            conf = 95.0
        elif (ri > 3.0 and was > 30) or (mri > 1.5 and was > 40):
            risk = "HIGH"
            probs = {"LOW": 0.05, "MODERATE": 0.15, "HIGH": 0.7, "CRITICAL": 0.1}
            conf = 88.0
        elif ri > 1.5 or was > 15 or mri > 1.0:
            risk = "MODERATE"
            probs = {"LOW": 0.2, "MODERATE": 0.7, "HIGH": 0.1, "CRITICAL": 0.0}
            conf = 82.0
        else:
            risk = "LOW"
            probs = {"LOW": 0.9, "MODERATE": 0.1, "HIGH": 0.0, "CRITICAL": 0.0}
            conf = 90.0
            
        return {"risk_level": risk, "confidence": conf, "probabilities": probs}

    def _generate_xai(self, features: Dict[str, float], risk_level: str, esi_category: str, lake_graph: Dict[str, Any]) -> tuple[str, List[FeatureContribution]]:
        # Map values to importance percentages based on Risk Level driving factors
        contributions = []
        if features["rainfall_intensity"] > 1.5:
            contributions.append(FeatureContribution(feature="Rainfall Intensity", contribution_percent=40.0))
        if features["water_accumulation_score"] > 15:
            contributions.append(FeatureContribution(feature="Water Accumulation", contribution_percent=30.0))
        if features["melt_rate_index"] > 1.0:
            contributions.append(FeatureContribution(feature="Melt Rate Index", contribution_percent=20.0))
        if features["temp_anomaly"] > 2.0:
            contributions.append(FeatureContribution(feature="Temperature Anomaly", contribution_percent=10.0))
            
        if not contributions:
            contributions = [FeatureContribution(feature="Baseline Conditions", contribution_percent=100.0)]
            
        # Natural Language Explanation comparing against baselines
        hist_events = lake_graph.get("historical_events", [])
        if hist_events:
            ai_reason = "Historical patterns indicate elevated GLOF risk." if risk_level in ["HIGH", "CRITICAL"] else "Historical conditions matching catastrophic events have not yet been fully reached."
        else:
            ai_reason = "No major historical GLOFs recorded for this specific lake to match against."
            
        explanation = (
            f"Current AI Risk: {risk_level}\n"
            f"Reason: {ai_reason}\n\n"
            f"Environmental Stress: {esi_category}\n"
            f"Reason: Current temperature anomaly is {features['temp_anomaly']:.1f}°C above baselines, and rainfall intensity is {features['rainfall_intensity']:.1f}x the norm, indicating {'unusually unstable' if esi_category in ['HIGH', 'EXTREME'] else 'stable'} conditions.\n\n"
            f"Overall Interpretation: The AI predicts {risk_level} risk. "
        )
        
        if esi_category in ["HIGH", "EXTREME"] and risk_level in ["LOW", "MODERATE"]:
            explanation += "However, environmental conditions are deteriorating rapidly. Closer monitoring is strongly recommended."
        elif esi_category in ["LOW", "MODERATE"] and risk_level in ["HIGH", "CRITICAL"]:
            explanation += "Despite stable environmental conditions, the AI identifies hidden patterns of instability warranting caution."
        else:
            explanation += "The environmental physical indicators strongly align with the AI prediction."
            
        return explanation, contributions

    async def assess_lake(self, lake_id: str, lake_graph: Dict[str, Any], current_weather: Dict[str, float]) -> AssessmentResult:
        # Step 3 & 4: Feature Engineering
        features = self.engineer_features(current_weather, lake_graph)
        
        # Step 5: Inference
        if self.model is not None:
            assessment_mode = "ML Mode"
            # Extract features in the exact order expected by the model
            feature_vector = [
                features["rainfall"], features["temperature"], features["humidity"],
                features["lake_area"], features["glacier_area"], features["elevation"],
                features["melt_rate_index"], features["rainfall_intensity"],
                features["water_accumulation_score"], features["seasonal_index"]
            ]
            
            
            loop = asyncio.get_running_loop()
            prediction_result = await loop.run_in_executor(None, self.model.predict, [feature_vector])
            prediction = prediction_result[0]
            
            # Handle numeric prediction if model returns ints
            risk_map = {0: "LOW", 1: "MODERATE", 2: "HIGH", 3: "CRITICAL"}
            risk_level = risk_map.get(prediction, prediction) if isinstance(prediction, (int, float)) else prediction
            
            try:
                probs_arr = await loop.run_in_executor(None, self.model.predict_proba, [feature_vector])
                probs_arr = probs_arr[0]
                probabilities = {"LOW": probs_arr[0], "MODERATE": probs_arr[1], "HIGH": probs_arr[2], "CRITICAL": probs_arr[3]}
            except:
                probabilities = {"LOW": 0.0, "MODERATE": 0.0, "HIGH": 0.0, "CRITICAL": 0.0}
                
            confidence = max(probabilities.values()) * 100 if probabilities else 85.0
            
        else:
            assessment_mode = "Rule Engine Mode"
            res = self._rule_engine_inference(features)
            risk_level = res["risk_level"]
            confidence = res["confidence"]
            probabilities = res["probabilities"]

        # Environmental Stress Engine Layer
        esi_score, esi_category = calculate_environmental_stress(features)

        # Step 6: Explainable AI
        explanation, feature_contribs = self._generate_xai(features, risk_level, esi_category, lake_graph)
        
        # Step 7: Decision Support
        river = lake_graph.get("connected_river", {})
        river_name = river.get("name", "Unknown River")
        settlements = lake_graph.get("downstream_settlements", [])
        settlement_names = [s.get("name", "Unknown") for s in settlements]
        
        # Dual-Layer Recommendation Logic
        overall_situation = "Stable"
        if risk_level == "LOW" and esi_category in ["LOW", "MODERATE"]:
            overall_situation = "Stable"
            actions = ["Continue normal monitoring."]
        elif risk_level == "MODERATE" and esi_category in ["HIGH", "EXTREME"]:
            overall_situation = "Escalating"
            actions = ["Current conditions are becoming increasingly unstable.", "Increase monitoring frequency.", "Acquire recent satellite imagery.", "Review emergency preparedness."]
        elif risk_level in ["HIGH", "CRITICAL"] or esi_category == "EXTREME":
            overall_situation = "Critical"
            actions = ["Immediate field assessment recommended.", "Prepare emergency response teams.", "Issue precautionary warnings to downstream authorities."]
        elif risk_level == "MODERATE":
            overall_situation = "Watch"
            actions = ["Increase satellite observation frequency.", "Alert local authorities for potential flooding."]
        else:
            overall_situation = "Watch"
            actions = ["Monitor shifting environmental indicators."]
            
        ds = DecisionSupport(
            overall_situation=overall_situation,
            current_status=risk_level,
            why_occurred=explanation,
            recommended_actions=actions,
            affected_river=river_name,
            affected_settlements=settlement_names,
            last_update_time=datetime.utcnow()
        )
        
        # Determine Risk Trend by comparing with previous assessment
        risk_trend = "Stable"
        prev_assessment = lake_graph.get("previous_assessment", {})
        if prev_assessment:
            prev_risk = prev_assessment.get("risk_level", "LOW")
            risk_order = {"LOW": 1, "MODERATE": 2, "HIGH": 3, "CRITICAL": 4}
            prev_val = risk_order.get(prev_risk, 1)
            curr_val = risk_order.get(risk_level, 1)
            
            if curr_val > prev_val:
                if curr_val - prev_val >= 2:
                    risk_trend = "Rapid Increase"
                else:
                    risk_trend = "Increasing"
            elif curr_val < prev_val:
                if prev_val - curr_val >= 2:
                    risk_trend = "Rapid Decrease"
                else:
                    risk_trend = "Decreasing"
            else:
                risk_trend = "Stable"
        else:
            if risk_level in ["HIGH", "CRITICAL"] and features["rainfall_intensity"] > 2.0:
                risk_trend = "Increasing"

        return AssessmentResult(
            lake_id=lake_id,
            timestamp=datetime.utcnow(),
            assessment_mode=assessment_mode,
            risk_level=risk_level,
            risk_trend=risk_trend,
            environmental_stress_score=esi_score,
            environmental_stress_category=esi_category,
            confidence_score=confidence,
            probabilities=probabilities,
            feature_contributions=feature_contribs,
            explanation=explanation,
            decision_support=ds,
            engineered_features=features
        )

ai_risk_engine = AIRiskEngine()

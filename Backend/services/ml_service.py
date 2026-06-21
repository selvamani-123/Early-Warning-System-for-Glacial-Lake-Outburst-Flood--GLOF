import joblib
import pandas as pd
import os
from training.feature_engineering import apply_feature_engineering
from models.domain import PredictionRequest

class MLService:
    def __init__(self):
        self.model = None
        self.features = None
        self.load_model()

    def load_model(self):
        model_path = "glof_model.pkl"
        features_path = "glof_model_features.pkl"
        if os.path.exists(model_path):
            self.model = joblib.load(model_path)
            self.features = joblib.load(features_path)
            print("Successfully loaded ML model for GLOF Sentinel.")
        else:
            print("Warning: glof_model.pkl not found. Please run the training pipeline.")

    def predict(self, req: PredictionRequest):
        if not self.model:
            return "UNKNOWN", 0.0

        # Convert request to dataframe
        data = {
            "rainfall": req.rainfall,
            "temperature": req.temperature,
            "elevation": req.elevation,
            "lake_area": req.lake_area,
            "glacier_area": req.glacier_area,
            "humidity": req.humidity,
            "month": req.month if req.month else 7
        }
        
        df = pd.DataFrame([data])
        
        # Feature Engineering
        df = apply_feature_engineering(df)
        
        # Ensure column order matches training
        X = df[self.features]
        
        # Predict
        prediction = self.model.predict(X)[0]
        
        # Get probability
        probs = self.model.predict_proba(X)[0]
        max_prob = max(probs) * 100
        
        # Get feature importances if available
        importances = {}
        if hasattr(self.model, "feature_importances_"):
            total = sum(self.model.feature_importances_)
            for feature, imp in zip(self.features, self.model.feature_importances_):
                importances[feature] = round((imp / total) * 100, 2)
        
        return prediction, round(max_prob, 2), importances

ml_service = MLService()

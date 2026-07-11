import pandas as pd

def generate_risk_labels(df: pd.DataFrame) -> pd.DataFrame:
    """
    Generates risk labels (LOW, MODERATE, HIGH, CRITICAL) based on scientific thresholds 
    for the derived features and base environmental conditions.
    
    Rules for GLOF Risk:
    - CRITICAL: Extreme rainfall intensity (> 5.0) AND high water accumulation (> 50), 
                OR extreme melt rate AND high accumulation.
    - HIGH: High rainfall intensity (> 3.0) AND moderate water accumulation (> 30).
    - MODERATE: Rainfall intensity (> 1.5) OR elevated water accumulation (> 15).
    - LOW: Default state.
    """
    df = df.copy()
    
    def determine_risk(row):
        acc = row.get('water_accumulation_score', 0)
        rain_int = row.get('rainfall_intensity', 0)
        melt = row.get('melt_rate_index', 0)
        
        # Risk thresholds
        if (rain_int > 5.0 and acc > 50) or (melt > 2.0 and acc > 60):
            return "CRITICAL"
        elif (rain_int > 3.0 and acc > 30) or (melt > 1.5 and acc > 40):
            return "HIGH"
        elif rain_int > 1.5 or acc > 15 or melt > 1.0:
            return "MODERATE"
        else:
            return "LOW"

    # Apply rules
    df['risk'] = df.apply(determine_risk, axis=1)
    
    # Also attach a numeric severity for plotting if needed
    severity_map = {"LOW": 0, "MODERATE": 1, "HIGH": 2, "CRITICAL": 3}
    df['risk_numeric'] = df['risk'].map(severity_map)
    
    return df

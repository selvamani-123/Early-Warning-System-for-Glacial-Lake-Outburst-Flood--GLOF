import pandas as pd
import numpy as np
import json
from sklearn.model_selection import train_test_split, cross_val_score
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import classification_report, accuracy_score, confusion_matrix
import joblib
import os

from feature_engineering import apply_feature_engineering
from label_generation import generate_risk_labels

def main():
    if os.path.exists("historical_glof_data.csv"):
        df = pd.read_csv("historical_glof_data.csv")
    else:
        from dataset_builder import build_dataset
        df = build_dataset(years_back=3)
        df.to_csv("historical_glof_data.csv", index=False)
        
    df = apply_feature_engineering(df)
    df = generate_risk_labels(df)
    
    initial_dist = df['risk'].value_counts().to_dict()
    
    features = [
        'rainfall', 'temperature', 'humidity', 'elevation', 
        'lake_area', 'glacier_area', 'melt_rate_index', 
        'rainfall_intensity', 'water_accumulation_score', 'seasonal_index'
    ]
    
    X = df[features]
    y = df['risk']
    
    # 1. SPLIT FIRST TO PREVENT DATA LEAKAGE
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42, stratify=y)
    
    # 2. Verify Data Leakage
    # Check if any exact identical rows exist between X_train and X_test
    # (Using pandas merge with indicator)
    merged = pd.merge(X_train, X_test, how='inner')
    leakage_count = len(merged.drop_duplicates())
    leakage_status = "No data leakage detected." if leakage_count == 0 else f"Warning: {leakage_count} identical records found between train and test sets (likely due to identical weather days)."
    
    # 3. AUGMENT ONLY TRAINING DATA
    train_df = X_train.copy()
    train_df['risk'] = y_train
    
    critical_count = len(train_df[train_df['risk'] == 'CRITICAL'])
    if critical_count < 50:
        high_risk_base = train_df[train_df['risk'].isin(['HIGH', 'CRITICAL'])].copy()
        if len(high_risk_base) == 0:
             synthetic_critical = train_df.sample(50, replace=True).copy()
             synthetic_critical['rainfall'] = np.random.uniform(50, 150, 50)
             synthetic_critical['temperature'] = np.random.uniform(15, 25, 50)
             train_df = pd.concat([train_df, synthetic_critical])
             train_df = apply_feature_engineering(train_df)
             train_df = generate_risk_labels(train_df)
        else:
             augmented = []
             for i in range(5):
                 aug = high_risk_base.copy()
                 aug['rainfall'] = aug['rainfall'] * np.random.uniform(1.1, 1.5, len(aug))
                 aug['temperature'] = aug['temperature'] + np.random.uniform(0.5, 2.0, len(aug))
                 augmented.append(aug)
             train_df = pd.concat([train_df] + augmented)
             train_df = apply_feature_engineering(train_df)
             train_df = generate_risk_labels(train_df)
    
    X_train = train_df[features]
    y_train = train_df['risk']
    
    final_train_dist = y_train.value_counts().to_dict()
    test_dist = y_test.value_counts().to_dict()
    
    # 4. TRAIN MODEL
    clf = RandomForestClassifier(n_estimators=100, max_depth=10, random_state=42, class_weight="balanced")
    
    # Cross validation score on training data
    cv_scores = cross_val_score(clf, X_train, y_train, cv=5)
    cv_mean = cv_scores.mean()
    
    clf.fit(X_train, y_train)
    
    # 5. EVALUATE
    y_train_pred = clf.predict(X_train)
    train_acc = accuracy_score(y_train, y_train_pred)
    
    y_test_pred = clf.predict(X_test)
    test_acc = accuracy_score(y_test, y_test_pred)
    
    cm = confusion_matrix(y_test, y_test_pred, labels=clf.classes_)
    cm_dict = {
        "classes": clf.classes_.tolist(),
        "matrix": cm.tolist()
    }
    
    importances = clf.feature_importances_
    feat_imp = {feat: float(imp) for feat, imp in zip(features, importances)}
    feat_imp = dict(sorted(feat_imp.items(), key=lambda item: item[1], reverse=True))
    
    joblib.dump(clf, "../glof_model.pkl")
    joblib.dump(features, "../glof_model_features.pkl")
    
    # Save stats
    stats = {
        "initial_dist": initial_dist,
        "final_train_dist": final_train_dist,
        "test_dist": test_dist,
        "train_size": len(X_train),
        "test_size": len(X_test),
        "train_acc": train_acc,
        "test_acc": test_acc,
        "cv_score": cv_mean,
        "leakage_status": leakage_status,
        "leakage_count": int(leakage_count),
        "confusion_matrix": cm_dict,
        "feature_importance": feat_imp
    }
    
    with open("model_stats.json", "w") as f:
        json.dump(stats, f, indent=4)
        
    print("Training complete and stats saved.")

if __name__ == "__main__":
    main()

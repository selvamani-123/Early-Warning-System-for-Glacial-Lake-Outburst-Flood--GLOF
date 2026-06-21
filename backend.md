# GLOF Sentinel Backend & AI System Requirements

## Project Overview

Build a backend for GLOF Sentinel, an AI-powered Glacial Lake Outburst Flood (GLOF) Risk Assessment Platform.

The system should predict flood risk using environmental data, weather patterns, glacier information, and lake characteristics instead of relying on physical IoT sensors.

The backend must:

* Collect real-world environmental data
* Process glacier and lake metadata
* Train and serve an AI model
* Generate risk predictions
* Store prediction history
* Generate alerts
* Provide REST APIs and WebSocket updates to the frontend

---

# Core Objective

Predict GLOF Risk Levels:

* LOW
* MODERATE
* HIGH
* CRITICAL

based on environmental conditions.

The system should estimate risk using:

* Temperature
* Rainfall
* Glacier characteristics
* Lake characteristics
* Elevation
* Derived environmental indicators

---

# Technology Stack

## Backend

* Python 3.11+
* FastAPI
* Uvicorn

## Database

* MongoDB Atlas

## Machine Learning

* Scikit-Learn
* RandomForestClassifier
* Pandas
* NumPy
* Joblib

## Maps

* OpenStreetMap
* GeoJSON Layers

## Weather Source

* Open-Meteo API

---

# Data Sources

## Open-Meteo

Collect:

* Temperature
* Rainfall
* Humidity
* Weather Conditions

---

## NASA EarthData

Collect:

* Glacier Information
* Elevation Data
* Lake Information

---

## GLIMS

Collect:

* Glacier Metadata
* Glacier Area
* Glacier Coordinates
* Glacier Region Information

---

## Historical Flood Datasets

Collect:

* Flood Events
* Flood Severity
* Historical Environmental Conditions

Sources may include:

* Kaggle
* Research Papers
* Public Hydrology Datasets

---

# Machine Learning Requirements

## Model

Use:

RandomForestClassifier

Reason:

* Suitable for tabular environmental data
* Fast training
* Easy deployment
* Easy explainability

---

## Training Features

Use the following features:

* rainfall
* temperature
* elevation
* lake_area
* glacier_area
* humidity
* estimated_melt_rate

---

## Derived Features

Create:

### Melt Rate Index

Based on:

* Temperature
* Elevation

---

### Rainfall Intensity

Based on:

* Current Rainfall
* Historical Average

---

### Water Accumulation Score

Based on:

* Rainfall
* Lake Area
* Melt Rate

---

### Seasonal Index

Based on:

* Month
* Temperature Patterns

---

## Prediction Output

Return:

{
"risk": "HIGH",
"probability": 87
}

Risk Categories:

* LOW
* MODERATE
* HIGH
* CRITICAL

---

# Dataset Preparation

Create a unified dataset containing:

* Weather Data
* Glacier Metadata
* Lake Metadata
* Historical Flood Records

Final dataset format:

rainfall

temperature

humidity

elevation

lake_area

glacier_area

estimated_melt_rate

risk

---

# Model Training Pipeline

1. Load Dataset

2. Clean Dataset

3. Create Derived Features

4. Train/Test Split

5. Train RandomForestClassifier

6. Evaluate Accuracy

7. Save Model

Output:

glof_model.pkl

---

# FastAPI Backend Requirements

Load model.pkl during startup.

Expose REST APIs.

---

## Dashboard Summary

GET /api/dashboard-summary

Return:

* Active Lakes
* High Risk Lakes
* Critical Risk Lakes
* Last Update

---

## Prediction Endpoint

POST /api/predict

Input:

{
"rainfall":80,
"temperature":13,
"elevation":5200,
"lake_area":2.8,
"glacier_area":1.6,
"humidity":65
}

Output:

{
"risk":"HIGH",
"probability":84
}

---

## Alerts Endpoint

GET /api/alerts

Return:

Historical alerts.

---

## Map Endpoint

GET /api/map-data

Return:

* Lake Coordinates
* River Coordinates
* Risk Zones

---

## Analytics Endpoint

GET /api/analytics

Return:

* Historical Predictions
* Risk Distribution
* Alert Statistics

---

# MongoDB Collections

## lakes

Store:

* lake name
* coordinates
* elevation
* area

---

## weather_cache

Store:

* temperature
* rainfall
* humidity
* timestamp

---

## predictions

Store:

* prediction result
* probability
* timestamp

---

## alerts

Store:

* severity
* message
* timestamp

---

# Alert Engine

Generate alerts automatically.

Rules:

LOW

No Alert

MODERATE

Advisory

HIGH

Warning

CRITICAL

Emergency Alert

Store all alerts in MongoDB.

---

# WebSocket Service

Endpoint:

/ws/telemetry

Push:

* New Predictions
* Risk Changes
* Alerts
* Dashboard Updates

in real time.

---

# Map Requirements

Use:

* OpenStreetMap
* Leaflet.js
* GeoJSON River Layers

Display:

* Glacial Lakes
* Rivers
* Risk Zones
* Monitored Locations

---

# Deliverables

Backend must provide:

* FastAPI Application
* MongoDB Integration
* Open-Meteo Integration
* NASA/GLIMS Data Processing
* Dataset Builder
* Random Forest Training Pipeline
* model.pkl Generation
* Prediction Service
* Alert Engine
* WebSocket Updates
* Analytics APIs

The final system should operate as an environmental intelligence platform capable of estimating GLOF risk using real-world weather and glacier-related data without requiring physical IoT sensors.

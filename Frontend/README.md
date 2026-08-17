# 💻 GLOF Sentinel — Interactive Web Frontend

[![JavaScript](https://img.shields.io/badge/JavaScript-ES6+-yellow.svg?logo=javascript)](https://developer.mozilla.org/en-US/docs/Web/JavaScript)
[![HTML5](https://img.shields.io/badge/HTML5-Semantic-E34F26.svg?logo=html5)](https://developer.mozilla.org/en-US/docs/Web/HTML)
[![CSS3](https://img.shields.io/badge/CSS3-Glassmorphism-1572B6.svg?logo=css3)](https://developer.mozilla.org/en-US/docs/Web/CSS)

The **Frontend** of GLOF Sentinel is a lightweight, ultra-responsive Glassmorphism web application built with HTML5, CSS3, ES6 JavaScript, Leaflet GIS maps, and Chart.js telemetry charts.

---

## 🎨 Pages Overview

- `index.html`: Main Command Dashboard & System Status
- `lake_intelligence.html`: Glacial Lake Expansion & Bathymetry Tracking
- `river_intelligence.html`: Hydrodynamic Flow Discharge & Peak Arrival Models
- `monitoring.html`: Real-Time Satellite Telemetry & Sensor Streams
- `analytics.html`: Machine Learning Hazard Risk Engine & Predictor
- `alerts.html`: Early Warning Alert Console & Multi-Channel Dispatch
- `history.html`: Historical GLOF Disaster Analysis & Pattern Matching
- `registry.html`: Inventory of Monitored Glacial Lakes

---

## 🚀 How to Run Locally

### Option A: Unified FastAPI Server (Recommended)
When running the FastAPI backend (`uvicorn main:app --host 0.0.0.0 --port 8000 --reload`), the frontend is automatically mounted and served at:
👉 **[http://localhost:8000](http://localhost:8000)**

### Option B: Independent Static Web Server
You can also host the frontend using any static web server (such as Python `http.server`, VS Code Live Server, or Nginx):

```bash
# From the Frontend directory
python -m http.server 3000
```
Open **[http://localhost:3000](http://localhost:3000)** in your browser.

---

## ☁️ Deployment

This directory includes `vercel.json` pre-configured to proxy `/api/v1` requests to your deployed Render backend API. Simply connect this directory to Vercel for instant static hosting.

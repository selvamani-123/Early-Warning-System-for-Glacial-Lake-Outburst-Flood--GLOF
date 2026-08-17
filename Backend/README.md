# ⚙️ GLOF Sentinel — Backend API & ML Service

[![FastAPI](https://img.shields.io/badge/FastAPI-0.104.1-009688.svg?logo=fastapi)](https://fastapi.tiangolo.com/)
[![Python](https://img.shields.io/badge/Python-3.10%20%7C%203.11-blue.svg?logo=python)](https://www.python.org/)
[![MongoDB](https://img.shields.io/badge/MongoDB-Atlas%20%2F%20Motor-47A248.svg?logo=mongodb)](https://www.mongodb.com/)

The **Backend** service of GLOF Sentinel powers the asynchronous REST APIs, real-time Machine Learning hazard risk engine, APScheduler telemetry background service, and MongoDB data persistence layer.

---

## 🚀 Quick Setup & Execution

### 1. Create Virtual Environment & Install Dependencies

```bash
# From the Backend directory
python -m venv venv

# On Windows:
venv\Scripts\activate

# On macOS / Linux:
source venv/bin/activate

# Install requirements
pip install -r requirements.txt
```

### 2. Configure Environment Variables

Create `.env` in this directory:

```env
MONGODB_URI=mongodb://localhost:27017
DB_NAME=glof_sentinel
ENVIRONMENT=development
ALLOWED_ORIGINS=http://localhost:8000,http://127.0.0.1:8000,http://localhost:3000
```

### 3. Seed Database

Populate initial telemetry for 50+ real glacial lakes and historical disaster events:

```bash
python -m app.scripts.seed_db
```

### 4. Launch FastAPI Server

```bash
uvicorn main:app --host 0.0.0.0 --port 8000 --reload
```

- **Interactive API Docs**: [http://localhost:8000/docs](http://localhost:8000/docs)
- **ReDoc API Docs**: [http://localhost:8000/redoc](http://localhost:8000/redoc)

---

## 🤖 Offline Machine Learning Pipeline

The `offline_training/` directory contains tools to generate synthetic datasets, perform feature engineering, and train the GLOF hazard classification model:

```bash
# Re-train model and generate updated glof_model.pkl
python offline_training/train_model.py
```

---

## 🛠️ Tech Stack & Dependencies

- **FastAPI**: Asynchronous web framework
- **Motor / PyMongo**: Async MongoDB driver
- **Scikit-Learn & Pandas**: Random forest model & feature handling
- **APScheduler**: Automated background satellite/weather polling
- **Pydantic v2**: Data validation & domain schemas

# Clinical AI Project

Clinical AI Project is a full-stack diagnostic web application built around a trained CatBoost model and a clinical dataset. It provides an interactive frontend for manual disease prediction, patient lookup, doctor recommendations, and operational monitoring, backed by a Python API that serves model inference and dataset-driven insights.

The project is structured for deployment with:

- `frontend/` on Vercel
- `backend/` on Render

## Overview

The application combines:

- AI-assisted manual diagnosis from clinical input values
- patient record lookup by `Patient_ID`
- specialist recommendation data for mapped diseases
- operational dashboards for disease mix and feature importance
- a deployable React + Flask architecture suitable for cloud hosting

## Tech Stack

### Frontend

- React 18
- Vite
- plain CSS

### Backend

- Flask
- Flask-CORS
- python-dotenv
- pandas
- CatBoost
- scikit-learn
- gunicorn

### Model Assets

- `catboost_model.cbm`
- `label_encoder.pkl`
- `clinical_dataset.csv`

## Project Structure

```text
Clinical_AI_Project/
├─ backend/
│  ├─ app.py
│  ├─ model_service.py
│  ├─ requirements.txt
│  └─ .env.example
├─ frontend/
│  ├─ src/
│  │  ├─ App.jsx
│  │  ├─ main.jsx
│  │  └─ styles.css
│  ├─ .env.example
│  ├─ package.json
│  ├─ vite.config.js
│  └─ vercel.json
├─ render.yaml
├─ catboost_model.cbm
├─ label_encoder.pkl
├─ clinical_dataset.csv
└─ README.md
```

## Features

### Frontend

- tabbed workspace UI
- `Command Center` dashboard
- `Diagnosis Lab` for manual prediction
- `Patient Records` for search by patient ID
- `Care Network` for specialist recommendations

### Backend API

- health check endpoint
- clinical overview metrics
- disease list endpoint
- doctor recommendation endpoint
- patient lookup endpoint
- manual diagnosis inference endpoint

## How It Works

### Manual Diagnosis

The frontend submits clinical input values to the backend endpoint:

```text
POST /api/diagnosis/manual
```

The backend:

- normalizes the input
- encodes categorical values like gender
- loads the CatBoost model and label encoder
- predicts disease and confidence
- computes autoimmune score and risk
- returns lab analysis and feature-importance summaries

### Patient Lookup

The frontend requests:

```text
GET /api/patients/<patient_id>
```

The backend finds the row in the dataset, runs prediction on that patient, and returns both stored patient data and model output.

## Local Development

### Prerequisites

- Python 3.13 recommended for deployment compatibility
- Node.js 20+ or newer
- npm

## Backend Setup

```powershell
cd backend
pip install -r requirements.txt
copy .env.example .env
python app.py
```

The backend runs by default at:

```text
http://localhost:8000
```

### Backend Environment Variables

Create `backend/.env` from `backend/.env.example`.

```env
PORT=8000
FRONTEND_ORIGIN=http://localhost:5173
```

Notes:

- `PORT` is used locally and by Render
- `FRONTEND_ORIGIN` controls allowed frontend origins for CORS
- multiple frontend origins are supported as comma-separated values

Example:

```env
FRONTEND_ORIGIN=https://your-frontend.vercel.app,https://your-preview.vercel.app
```

## Frontend Setup

```powershell
cd frontend
npm install
copy .env.example .env
npm run dev
```

The frontend dev server usually runs at:

```text
http://localhost:5173
```

### Frontend Environment Variables

Create `frontend/.env` from `frontend/.env.example`.

```env
VITE_API_BASE_URL=http://localhost:8000
```

Notes:

- this should point to your backend base URL
- trailing slashes are safely normalized by the frontend

## Build Commands

### Frontend Production Build

```powershell
cd frontend
npm run build
```

### Backend Syntax Check

```powershell
python -m py_compile backend\app.py backend\model_service.py
```

## Deployment

### Deploy Backend to Render

This repository already includes [render.yaml](./render.yaml).

### Render Settings

- Runtime: `Python`
- Build command: `pip install -r backend/requirements.txt`
- Start command: `gunicorn --chdir backend app:app`

### Render Environment Variables

- `FRONTEND_ORIGIN=https://your-frontend.vercel.app`

If you use both production and preview Vercel URLs:

```env
FRONTEND_ORIGIN=https://your-frontend.vercel.app,https://your-preview.vercel.app
```

### Deploy Frontend to Vercel

### Vercel Settings

- Framework preset: `Vite`
- Root directory: `frontend`

### Vercel Environment Variables

- `VITE_API_BASE_URL=https://your-backend.onrender.com`

## Frontend and Backend Connection

The connection between Vercel and Render is based on these two variables:

- Vercel frontend uses `VITE_API_BASE_URL`
- Render backend allows the frontend through `FRONTEND_ORIGIN`

For production, make sure:

1. `VITE_API_BASE_URL` points to the Render backend URL
2. `FRONTEND_ORIGIN` matches the Vercel frontend URL

Example:

```env
# Vercel
VITE_API_BASE_URL=https://clinical-ai-backend.onrender.com

# Render
FRONTEND_ORIGIN=https://clinical-ai.vercel.app
```

## API Reference

### Health

```http
GET /api/health
```

### Overview

```http
GET /api/overview
```

### Diseases

```http
GET /api/diseases
```

### Doctors

```http
GET /api/doctors?disease=Diabetes
```

### Patient Lookup

```http
GET /api/patients/<patient_id>
```

### Manual Diagnosis

```http
POST /api/diagnosis/manual
Content-Type: application/json
```

Example request body:

```json
{
  "Age": 34,
  "Gender": "Male",
  "WBC_Count": 5300,
  "Neutrophils_%": 58,
  "Hemoglobin": 14.5,
  "MCV": 89,
  "ALT": 35,
  "AST": 29,
  "Creatinine": 0.9,
  "Glucose_Fasting": 110,
  "CRP": 8,
  "ANA_Positive": 0
}
```

## Important Files

- Backend entrypoint: [backend/app.py](./backend/app.py)
- Backend model logic: [backend/model_service.py](./backend/model_service.py)
- Backend dependencies: [backend/requirements.txt](./backend/requirements.txt)
- Frontend app: [frontend/src/App.jsx](./frontend/src/App.jsx)
- Frontend styles: [frontend/src/styles.css](./frontend/src/styles.css)
- Render config: [render.yaml](./render.yaml)

## Notes

- The original Streamlit app remains in `app.py` for reference, but the deployable web architecture uses `frontend/` and `backend/`
- the model runs on the backend, not in the browser
- `.env` files are intentionally ignored by git

## Current Status

- frontend build verified
- backend syntax verified
- repository prepared for Vercel + Render deployment

## License

Add a license file if you want to distribute this project publicly.

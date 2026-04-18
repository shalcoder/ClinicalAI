# Clinical AI Project

This project now has two deployable parts:

- `backend/`: Flask API for prediction, patient lookup, doctors, and dashboard metrics. Deploy this on Render.
- `frontend/`: React + Vite application for the production UI. Deploy this on Vercel.

## Local development

### Backend

```powershell
cd backend
pip install -r requirements.txt
python app.py
```

The API runs on `http://localhost:8000`.

### Frontend

```powershell
cd frontend
npm install
copy .env.example .env
npm run dev
```

Set `VITE_API_BASE_URL` in `frontend/.env` to your backend URL.

## Deploy backend to Render

1. Push the repository to GitHub.
2. In Render, create a new `Blueprint` or `Web Service` from the repo.
3. If using the included blueprint, Render will read [render.yaml](./render.yaml).
4. Set `FRONTEND_ORIGIN` to your Vercel domain, for example `https://your-frontend.vercel.app`.

Render build settings if entered manually:

- Build command: `pip install -r backend/requirements.txt`
- Start command: `gunicorn --chdir backend app:app`

## Deploy frontend to Vercel

1. Import the same repository into Vercel.
2. Set the root directory to `frontend`.
3. Framework preset: `Vite`.
4. Add environment variable `VITE_API_BASE_URL` with your Render backend URL, for example `https://your-backend.onrender.com`.
5. Deploy.

## API endpoints

- `GET /api/health`
- `GET /api/overview`
- `GET /api/diseases`
- `GET /api/doctors?disease=Diabetes`
- `GET /api/patients/<patient_id>`
- `POST /api/diagnosis/manual`

Example manual diagnosis payload:

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

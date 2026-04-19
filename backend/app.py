from __future__ import annotations

import os

from flask import Flask, jsonify, request
from flask_cors import CORS
from dotenv import load_dotenv

from model_service import build_diagnosis_response, find_patient, get_allowed_origins, get_diseases, get_doctors, get_overview


load_dotenv()

app = Flask(__name__)
CORS(
    app,
    resources={r"/api/*": {"origins": get_allowed_origins()}},
    supports_credentials=False,
)


@app.get("/")
def root():
    return jsonify({"service": "clinical-ai-backend", "status": "ok"})


@app.get("/api/health")
def health_check():
    return jsonify({"status": "ok", "allowed_origins": get_allowed_origins()})


@app.get("/api/overview")
def overview():
    return jsonify(get_overview())


@app.get("/api/diseases")
def diseases():
    return jsonify({"items": get_diseases()})


@app.get("/api/doctors")
def doctors():
    return jsonify({"items": get_doctors(request.args.get("disease"))})


@app.get("/api/patients/<patient_id>")
def patient_lookup(patient_id: str):
    patient_data = find_patient(patient_id)
    if patient_data is None:
        return jsonify({"error": "Patient not found"}), 404
    return jsonify(patient_data)


@app.post("/api/diagnosis/manual")
def manual_diagnosis():
    payload = request.get_json(silent=True) or {}
    required_fields = [
        "Age",
        "Gender",
        "WBC_Count",
        "Neutrophils_%",
        "Hemoglobin",
        "MCV",
        "ALT",
        "AST",
        "Creatinine",
        "Glucose_Fasting",
        "CRP",
        "ANA_Positive",
    ]
    missing = [field for field in required_fields if field not in payload]
    if missing:
        return jsonify({"error": "Missing required fields", "missing": missing}), 400
    return jsonify(build_diagnosis_response(payload))


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.getenv("PORT", "8000")), debug=True)

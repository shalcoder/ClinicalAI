from __future__ import annotations

import os
import pickle
from functools import lru_cache
from pathlib import Path

import pandas as pd
from catboost import CatBoostClassifier


BASE_DIR = Path(__file__).resolve().parent.parent
MODEL_PATH = BASE_DIR / "catboost_model.cbm"
ENCODER_PATH = BASE_DIR / "label_encoder.pkl"
DATASET_PATH = BASE_DIR / "clinical_dataset.csv"

DOCTOR_DATA = [
    {"disease": "Diabetes", "doctor": "Dr. Sharma", "clinic": "Apollo Chennai", "experience": "12 years", "lat": 13.0827, "lon": 80.2707},
    {"disease": "Diabetes", "doctor": "Dr. Kumar", "clinic": "Fortis Chennai", "experience": "15 years", "lat": 13.0674, "lon": 80.2376},
    {"disease": "Anemia", "doctor": "Dr. Rao", "clinic": "MIOT Chennai", "experience": "10 years", "lat": 13.0604, "lon": 80.2496},
    {"disease": "Anemia", "doctor": "Dr. Priya", "clinic": "SIMS Chennai", "experience": "9 years", "lat": 13.0452, "lon": 80.2201},
    {"disease": "Kidney_Disorder", "doctor": "Dr. Mehta", "clinic": "Global Hospitals", "experience": "18 years", "lat": 13.0358, "lon": 80.2326},
    {"disease": "Kidney_Disorder", "doctor": "Dr. Arvind", "clinic": "SRM Medical Center", "experience": "11 years", "lat": 13.0123, "lon": 80.1987},
    {"disease": "Autoimmune_Disease", "doctor": "Dr. Iyer", "clinic": "CMC Chennai", "experience": "14 years", "lat": 13.0796, "lon": 80.2570},
    {"disease": "Autoimmune_Disease", "doctor": "Dr. Nandakumar", "clinic": "Apollo Madurai", "experience": "20 years", "lat": 9.9252, "lon": 78.1198},
]

NORMAL_RANGES = {
    "Glucose_Fasting": (70, 100),
    "Hemoglobin": (13, 17),
    "Creatinine": (0.6, 1.3),
    "CRP": (0, 5),
    "WBC_Count": (4000, 11000),
}

MEDICATION_MAP = {
    "Diabetes": "Metformin, Insulin",
    "Anemia": "Iron Supplements",
    "Kidney_Disorder": "ACE Inhibitors",
    "Autoimmune_Disease": "Steroids",
}


def encode_gender(value: str) -> int:
    return 0 if str(value).strip().lower() == "male" else 1


def calculate_autoimmune_score(ana: int, crp: float, wbc: float, neut: float, hb: float) -> int:
    score = 0
    if ana == 1:
        score += 40
    if crp > 10:
        score += 20
    if wbc < 4000:
        score += 15
    if neut < 40:
        score += 15
    if hb < 10:
        score += 10
    return min(score, 100)


def classify_autoimmune(ana: int, crp: float, wbc: float) -> str:
    if ana == 1 and crp > 10 and wbc < 4000:
        return "Systemic Lupus Erythematosus (SLE)"
    if ana == 1 and crp > 10:
        return "Rheumatoid Arthritis"
    if ana == 1 and wbc < 4000:
        return "Autoimmune Neutropenia"
    if crp > 15:
        return "Inflammatory Autoimmune Condition"
    if ana == 1:
        return "Early Autoimmune Detection"
    return "Negative for Autoimmune Disease"


def _status_for_value(value: float, low: float, high: float) -> str:
    if value < low:
        return "Low"
    if value > high:
        return "High"
    return "Normal"


@lru_cache(maxsize=1)
def load_dataset() -> pd.DataFrame:
    return pd.read_csv(DATASET_PATH)


@lru_cache(maxsize=1)
def load_model() -> CatBoostClassifier:
    model = CatBoostClassifier()
    model.load_model(str(MODEL_PATH))
    return model


@lru_cache(maxsize=1)
def load_label_encoder():
    with ENCODER_PATH.open("rb") as handle:
        return pickle.load(handle)


@lru_cache(maxsize=1)
def get_feature_columns() -> list[str]:
    return load_dataset().drop(columns=["Patient_ID", "Diagnosis"]).columns.tolist()


def _build_feature_frame(payload: dict) -> pd.DataFrame:
    features = {
        "Age": float(payload["Age"]),
        "Gender": encode_gender(payload["Gender"]),
        "WBC_Count": float(payload["WBC_Count"]),
        "Neutrophils_%": float(payload["Neutrophils_%"]),
        "Hemoglobin": float(payload["Hemoglobin"]),
        "MCV": float(payload["MCV"]),
        "ALT": float(payload["ALT"]),
        "AST": float(payload["AST"]),
        "Creatinine": float(payload["Creatinine"]),
        "Glucose_Fasting": float(payload["Glucose_Fasting"]),
        "CRP": float(payload["CRP"]),
        "ANA_Positive": int(payload["ANA_Positive"]),
    }
    columns = get_feature_columns()
    return pd.DataFrame([[features[column] for column in columns]], columns=columns)


def _predict_features(features_df: pd.DataFrame) -> tuple[str, float]:
    pred = load_model().predict(features_df)
    prob = load_model().predict_proba(features_df)
    disease = load_label_encoder().inverse_transform(pred.astype(int))[0]
    confidence = round(float(max(prob[0])) * 100, 2)
    return disease, confidence


def get_lab_analysis(values: dict) -> list[dict]:
    analysis = []
    for test, (low, high) in NORMAL_RANGES.items():
        value = float(values[test])
        analysis.append({"lab_test": test, "value": round(value, 2), "normal_range": f"{low}-{high}", "status": _status_for_value(value, low, high)})
    return analysis


def get_feature_importance(limit: int = 8) -> list[dict]:
    importance = load_model().get_feature_importance()
    pairs = [
        {"feature": feature, "importance": round(float(score), 4)}
        for feature, score in zip(get_feature_columns(), importance, strict=False)
        if feature != "Age"
    ]
    return sorted(pairs, key=lambda item: item["importance"], reverse=True)[:limit]


def build_diagnosis_response(payload: dict) -> dict:
    features_df = _build_feature_frame(payload)
    disease, confidence = _predict_features(features_df)
    glucose = float(payload["Glucose_Fasting"])
    crp = float(payload["CRP"])
    wbc = float(payload["WBC_Count"])
    neut = float(payload["Neutrophils_%"])
    hb = float(payload["Hemoglobin"])
    ana = int(payload["ANA_Positive"])

    risk_score = None
    stage = None
    if disease not in ["Normal", "Autoimmune_Disease"]:
        risk_score = round((glucose / 300) * 100, 2)
        if risk_score < 40:
            stage = "Stage 1 (Mild)"
        elif risk_score < 70:
            stage = "Stage 2 (Moderate)"
        else:
            stage = "Stage 3 (Severe)"

    autoimmune_score = calculate_autoimmune_score(ana, crp, wbc, neut, hb)
    autoimmune_risk = "Low" if autoimmune_score < 30 else "Moderate" if autoimmune_score < 60 else "High"

    return {
        "diagnosis": disease,
        "confidence": confidence,
        "risk_score": risk_score,
        "stage": stage,
        "recommended_medication": MEDICATION_MAP.get(disease, "Consult Specialist"),
        "autoimmune": {
            "score": autoimmune_score,
            "risk_level": autoimmune_risk,
            "condition": classify_autoimmune(ana, crp, wbc),
        },
        "lab_analysis": get_lab_analysis(features_df.iloc[0].to_dict()),
        "feature_importance": get_feature_importance(),
    }


def find_patient(patient_id: str) -> dict | None:
    patient = load_dataset()[load_dataset()["Patient_ID"] == patient_id]
    if patient.empty:
        return None
    row = patient.iloc[0].copy()
    raw_values = row.to_dict()
    row["Gender"] = encode_gender(raw_values["Gender"])
    features_df = pd.DataFrame([row[get_feature_columns()]])
    diagnosis, confidence = _predict_features(features_df)
    return {
        "patient": raw_values,
        "prediction": {
            "diagnosis": diagnosis,
            "confidence": confidence,
            "lab_analysis": get_lab_analysis(features_df.iloc[0].to_dict()),
            "feature_importance": get_feature_importance(),
        },
    }


def get_overview() -> dict:
    df = load_dataset()
    diagnosis_counts = (
        df["Diagnosis"].value_counts().rename_axis("diagnosis").reset_index(name="count").to_dict(orient="records")
    )
    return {
        "summary": {
            "records": int(len(df)),
            "avg_age": round(float(df["Age"].mean()), 1),
            "avg_glucose": round(float(df["Glucose_Fasting"].mean()), 1),
            "avg_crp": round(float(df["CRP"].mean()), 1),
            "avg_hemoglobin": round(float(df["Hemoglobin"].mean()), 1),
        },
        "diagnosis_distribution": diagnosis_counts,
        "top_features": get_feature_importance(6),
    }


def get_doctors(disease: str | None = None) -> list[dict]:
    return DOCTOR_DATA if not disease else [doctor for doctor in DOCTOR_DATA if doctor["disease"] == disease]


def get_diseases() -> list[str]:
    return sorted(load_dataset()["Diagnosis"].unique().tolist())


def get_allowed_origins() -> list[str] | str:
    raw_value = os.getenv("FRONTEND_ORIGIN", "").strip()
    if not raw_value:
        return ["http://localhost:5173", "http://127.0.0.1:5173"]

    origins = [item.strip() for item in raw_value.split(",") if item.strip()]
    return origins or "*"

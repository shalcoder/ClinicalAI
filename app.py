import streamlit as st
import pandas as pd
import numpy as np
import pickle
import plotly.express as px
import io
from catboost import CatBoostClassifier
from sklearn.model_selection import train_test_split
from sklearn.metrics import confusion_matrix
from sklearn.metrics import accuracy_score
from sklearn.preprocessing import LabelEncoder
from sklearn.ensemble import RandomForestClassifier
from sklearn.svm import SVC
from sklearn.pipeline import make_pipeline
from sklearn.preprocessing import StandardScaler
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet
from sklearn.preprocessing import MinMaxScaler

# =========================
# AUTOIMMUNE SCORE FUNCTION
# =========================
def calculate_autoimmune_score(ana, crp, wbc, neut, hb):
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

# =========================
# AUTOIMMUNE FUNCTIONS
# =========================
def classify_autoimmune(ana, crp, wbc):
    if ana == 1 and crp > 10 and wbc < 4000:
        return "Systemic Lupus Erythematosus (SLE)"
    elif ana == 1 and crp > 10:
        return "Rheumatoid Arthritis"
    elif ana == 1 and wbc < 4000:
        return "Autoimmune Neutropenia"
    elif crp > 15:
        return "Inflammatory Autoimmune Condition"
    elif ana == 1:
        return "Early Autoimmune Detection"
    else:
        return "Negative for Autoimmune Disease"

# ======================================
# PAGE CONFIG
# ======================================
st.set_page_config(page_title="Hospital AI System", layout="wide")
if "prediction_done" not in st.session_state:
    st.session_state["prediction_done"] = False

# ======================================
# LOGIN SYSTEM
# ======================================
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False

users = {"admin": "admin123", "doctor": "doctor123"}

if not st.session_state.logged_in:
    st.title("Hospital AI Login")

    username = st.text_input("Username")
    password = st.text_input("Password", type="password")

    if st.button("Login"):
        if username in users and users[username] == password:
            st.session_state.logged_in = True
            st.rerun()
        else:
            st.error("Invalid credentials")

    st.stop()

# ======================================
# LOAD MODEL
# ======================================
model = CatBoostClassifier()
model.load_model("catboost_model.cbm")

with open("label_encoder.pkl", "rb") as f:
    label_encoder = pickle.load(f)

df = pd.read_csv("clinical_dataset.csv")
feature_columns = df.drop(columns=["Patient_ID", "Diagnosis"]).columns

def encode_gender(g):
    return 0 if str(g).lower() == "male" else 1

def predict(features_df):
    pred = model.predict(features_df)
    prob = model.predict_proba(features_df)
    disease = label_encoder.inverse_transform(pred.astype(int))[0]
    confidence = round(max(prob[0]) * 100, 2)
    return disease, confidence

# ======================================
# SIDEBAR NAVIGATION
# ======================================
page = st.sidebar.radio(
    "Navigation",
    ["Diagnosis", "Doctor Dashboard", "AI Dashboard"]
)

# ======================================
# DOCTOR MASTER DATA
# ======================================
doctor_data = pd.DataFrame({
    "Disease": [
        "Diabetes","Diabetes",
        "Anemia","Anemia",
        "Kidney_Disorder","Kidney_Disorder",
        "Autoimmune_Disease","Autoimmune_Disease"
    ],
    "Doctor": [
        "Dr. Sharma","Dr. Kumar",
        "Dr. Rao","Dr. Priya",
        "Dr. Mehta","Dr. Arvind",
        "Dr. Iyer","Dr. Nandakumar"
    ],
    "Clinic": [
        "Apollo Chennai","Fortis Chennai",
        "MIOT Chennai","SIMS Chennai",
        "Global Hospitals","SRM Medical Center",
        "CMC Chennai","Apollo Madurai"
    ],
    "Experience": [
        "12 years","15 years",
        "10 years","9 years",
        "18 years","11 years",
        "14 years","20 years"
    ],
    "Lat": [
        13.0827,13.0674,
        13.0604,13.0452,
        13.0358,13.0123,
        13.0796,9.9252
    ],
    "Lon": [
        80.2707,80.2376,
        80.2496,80.2201,
        80.2326,80.1987,
        80.2570,78.1198
    ]
})

# ======================================
# DOCTOR DASHBOARD
# ======================================
if page == "Doctor Dashboard":

    st.title("Doctor Dashboard")

    selected_disease = st.selectbox(
        "Select Disease",
        doctor_data["Disease"].unique()
    )

    disease_docs = doctor_data[doctor_data["Disease"] == selected_disease]

    selected_doc = st.selectbox(
        "Select Doctor",
        disease_docs["Doctor"].values
    )

    doc_info = disease_docs[disease_docs["Doctor"] == selected_doc].iloc[0]

    st.subheader("Doctor Profile")
    st.write("Name:", doc_info["Doctor"])
    st.write("Clinic:", doc_info["Clinic"])
    st.write("Specialization:", doc_info["Disease"])
    st.write("Experience:", doc_info["Experience"])

    st.subheader("Clinic Location")
    st.map(pd.DataFrame({
        "latitude": [doc_info["Lat"]],
        "longitude": [doc_info["Lon"]]
    }))

# ======================================
# DIAGNOSIS PAGE
# ======================================
if page == "Diagnosis":

    st.title("AI Diagnosis System")

    mode = st.radio(
    "Select Mode",
    ["Search by Patient ID", "Manual Input"],
    key="diagnosis_mode"
)

    if mode == "Search by Patient ID":

       pid = st.text_input("Enter Patient ID")

       if st.button("Analyze Patient",key="search_btn"):

        patient = df[df["Patient_ID"] == pid]

        if patient.empty:
            st.error("Patient not found")

        else:
            row = patient.iloc[0].copy()

            # ===============================
            # PATIENT PROFILE
            # ===============================
            st.markdown("## Patient Profile")
            c1, c2, c3 = st.columns(3)
            c1.metric("Patient ID", row["Patient_ID"])
            c2.metric("Age", row["Age"])
            c3.metric("Gender", row["Gender"])

            row["Gender"] = encode_gender(row["Gender"])
            features_df = pd.DataFrame([row[feature_columns]])

            # ===============================
            # PREDICTION
            # ===============================
            disease, confidence = predict(features_df)

            st.markdown("## AI Diagnosis Result")
            colA, colB = st.columns(2)
            colA.metric("Predicted Disease", disease)
            colB.metric("AI Confidence", f"{confidence}%")

            # ===============================
            # LAB ANALYSIS
            # ===============================
            st.markdown("## Lab Analysis Table")

            normal_ranges = {
                "Glucose_Fasting": (70, 100),
                "Hemoglobin": (13, 17),
                "Creatinine": (0.6, 1.3),
                "CRP": (0, 5),
                "WBC_Count": (4000, 11000)
            }

            lab_analysis = []
            for test, (low, high) in normal_ranges.items():
                value = row[test]

                if value < low:
                    status = "Low"
                elif value > high:
                    status = "High"
                else:
                    status = "Normal"

                lab_analysis.append({
                    "Lab Test": test,
                    "Value": round(value, 2),
                    "Normal Range": f"{low}-{high}",
                    "Status": status
                })

            st.dataframe(pd.DataFrame(lab_analysis), use_container_width=True)

            # ===============================
            # EXPLAINABLE AI (INSIDE SAME BLOCK ✅)
            # ===============================
            st.markdown("## Explainable AI")

            importance = model.get_feature_importance()

            importance_df = pd.DataFrame({
                "Feature": feature_columns,
                "Importance": importance
            }).sort_values(by="Importance", ascending=False)

            # REMOVE AGE
            importance_df = importance_df[importance_df["Feature"] != "Age"]

            top_features = importance_df.head(8)

            fig1 = px.bar(
                top_features,
                x="Importance",
                y="Feature",
                orientation='h',
                title="Top Feature Importance" , color="Importance"
            )

            st.plotly_chart(fig1, use_container_width=True)

            fig2 = px.pie(
                top_features,
                names="Feature",
                values="Importance",
                title="Feature Contribution"
            )
            st.plotly_chart(fig2, use_container_width=True)



# ===========================
# MANUAL INPUT
# ===========================

disease = None
confidence = None
risk_score = None
stage = None

if page == "Diagnosis":

    mode = st.session_state.get("diagnosis_mode")

    if mode != "Manual Input":
        st.session_state["prediction_done"] = False

    if mode == "Manual Input":

        col1, col2 = st.columns(2)

        with col1:
            age = st.number_input("Age", 18, 100)
            gender = st.selectbox("Gender", ["Male", "Female"])
            wbc = st.number_input("WBC Count", 3000, 20000)
            neut = st.number_input("Neutrophils %", 30.0, 95.0)
            hb = st.number_input("Hemoglobin", 7.0, 18.0)
            mcv = st.number_input("MCV", 60.0, 110.0)

        with col2:
            alt = st.number_input("ALT", 5.0, 200.0)
            ast = st.number_input("AST", 5.0, 200.0)
            creat = st.number_input("Creatinine", 0.3, 3.0)
            glucose = st.number_input("Glucose", 60.0, 300.0)
            crp = st.number_input("CRP", 0.0, 50.0)
            ana = st.selectbox("ANA Positive", [0, 1])

        if st.button("Predict Disease", key="manual_btn"):

            # =========================
            # DATA PREP
            # =========================
            data = {
                "Age": age,
                "Gender": encode_gender(gender),
                "WBC_Count": wbc,
                "Neutrophils_%": neut,
                "Hemoglobin": hb,
                "MCV": mcv,
                "ALT": alt,
                "AST": ast,
                "Creatinine": creat,
                "Glucose_Fasting": glucose,
                "CRP": crp,
                "ANA_Positive": ana
            }

            features_df = pd.DataFrame([data])
            features_df = features_df[feature_columns]

            # =========================
            # PREDICTION
            # =========================
            disease, confidence = predict(features_df)

            st.session_state["disease"] = disease
            st.session_state["confidence"] = confidence
            st.session_state["prediction_done"] = True

            # =========================
            # NORMAL RISK (ONLY NON-AUTOIMMUNE)
            # =========================
            if disease not in ["Normal", "Autoimmune_Disease"]:
                risk_score = round((glucose / 300) * 100, 2)

                if risk_score < 40:
                    stage = "Stage 1 (Mild)"
                elif risk_score < 70:
                    stage = "Stage 2 (Moderate)"
                else:
                    stage = "Stage 3 (Severe)"
            else:
                risk_score = None
                stage = None

            # =========================
            # AUTOIMMUNE CALCULATION
            # =========================
            autoimmune_score = calculate_autoimmune_score(ana, crp, wbc, neut, hb)

            if autoimmune_score < 30:
                autoimmune_risk = "Low"
            elif autoimmune_score < 60:
                autoimmune_risk = "Moderate"
            else:
                autoimmune_risk = "High"

            autoimmune_type = classify_autoimmune(ana, crp, wbc)

            # =========================
            # UI DISPLAY
            # =========================
            col1, col2 = st.columns(2)

            # ===== LEFT: AI DIAGNOSIS =====
            with col1:
                st.header("AI Diagnosis")

                st.write("Predicted Disease :", disease)
                
                medication_map = {
                    "Diabetes": "Metformin, Insulin",
                    "Anemia": "Iron Supplements",
                    "Kidney_Disorder": "ACE Inhibitors",
                    "Autoimmune_Disease": "Steroids"
                }

                if disease != "Autoimmune_Disease":
                    st.write("Stage :", stage if stage else "N/A")

                st.write("Recommended Medication :",
                         medication_map.get(disease, "Consult Specialist"))
            

            # ===== RIGHT: AUTOIMMUNE =====
            with col2:
                st.header("Autoimmune Risk Assessment")

                st.write("Autoimmune Score:", autoimmune_score, "%")
                st.write("Risk Level:", autoimmune_risk)
                st.write("Condition:", autoimmune_type)

                if disease == "Autoimmune_Disease":
                    st.success("Autoimmune is Positive")

                elif autoimmune_score > 60:
                    st.warning("⚠ High autoimmune risk detected")

            # =========================
            # STORE SESSION
            # =========================
            st.session_state["risk_score"] = risk_score
            st.session_state["stage"] = stage
            st.session_state["autoimmune_score"] = autoimmune_score
            st.session_state["autoimmune_type"] = autoimmune_type

    
if st.session_state.get("diagnosis_mode") == "Manual Input" and st.session_state.get("prediction_done"):

    if st.button("Generate Patient PDF",key="manual_pdf_btn"):

        import io
        import matplotlib.pyplot as plt
        import numpy as np
        from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, Image
        from reportlab.lib import colors
        from reportlab.lib.styles import getSampleStyleSheet

        buffer = io.BytesIO()
        doc = SimpleDocTemplate(buffer)
        styles = getSampleStyleSheet()
        content = []

        # =========================
        # HEADER
        # =========================
        content.append(Paragraph("<b>AI CLINICAL DIAGNOSTIC REPORT</b>", styles['Title']))
        content.append(Spacer(1, 15))

        # =========================
        # STAGE FIX
        # =========================
        stage_value = st.session_state.get("stage")
        if not stage_value or stage_value == "None":
            stage_value = "N/A"

        # =========================
        # SUMMARY
        # =========================
        summary_data = [
            ["Field", "Value"],
            ["Disease", st.session_state.get("disease", "N/A")],
            ["Confidence", f"{st.session_state.get('confidence','N/A')} %"],
            ["Stage", stage_value]
        ]

        table = Table(summary_data)
        table.setStyle(TableStyle([
            ('BACKGROUND',(0,0),(-1,0),colors.grey),
            ('GRID',(0,0),(-1,-1),1,colors.black)
        ]))

        content.append(Paragraph("<b>Patient Summary</b>", styles['Heading2']))
        content.append(table)
        content.append(Spacer(1, 15))

        # =========================
        # LAB DATA
        # =========================
        normal_ranges = {
            "Glucose": (70, 100),
            "Hemoglobin": (13, 17),
            "Creatinine": (0.6, 1.3),
            "CRP": (0, 5),
            "WBC": (4000, 11000)
        }

        patient_values = {
            "Glucose": glucose,
            "Hemoglobin": hb,
            "Creatinine": creat,
            "CRP": crp,
            "WBC": wbc
        }

        lab_table = [["Parameter", "Patient", "Normal Range", "Status"]]

        for k in patient_values:
            val = patient_values[k]
            low, high = normal_ranges[k]

            if val < low:
                status = "Low"
            elif val > high:
                status = "High"
            else:
                status = "Normal"

            lab_table.append([k, str(val), f"{low}-{high}", status])

        table = Table(lab_table)
        table.setStyle(TableStyle([
            ('GRID',(0,0),(-1,-1),1,colors.black),
            ('BACKGROUND',(0,0),(-1,0),colors.darkblue),
            ('TEXTCOLOR',(0,0),(-1,0),colors.white),
        ]))

        content.append(Paragraph("<b>Clinical Parameters</b>", styles['Heading2']))
        content.append(table)
        content.append(Spacer(1, 15))

        # =========================
        # FIXED GRAPH
        # =========================
        features = list(patient_values.keys())
        patient_vals = []
        normal_vals = []

        for key in features:
            val = patient_values[key]
            low, high = normal_ranges[key]

            mid = (low + high) / 2
            range_span = (high - low)

            norm_val = 0.5 + (val - mid) / (range_span * 2)
            norm_val = max(0.1, min(0.9, norm_val))

            patient_vals.append(norm_val)
            normal_vals.append(0.5)

        plt.figure()
        plt.plot(features, patient_vals, marker='o', linewidth=2, label='Patient')
        plt.plot(features, normal_vals, linestyle='--', linewidth=2, label='Normal')

        plt.ylim(0, 1)
        plt.xticks(rotation=20)
        plt.title("Patient vs Normal Comparison")
        plt.legend()

        chart_path = "chart.png"
        plt.savefig(chart_path, bbox_inches='tight')
        plt.close()

        content.append(Paragraph("<b>Patient vs Normal Comparison</b>", styles['Heading2']))
        content.append(Image(chart_path, width=400, height=200))
        content.append(Spacer(1, 20))

        # =========================
        # 🔥 WORKING GAUGE FIX
        # =========================
        score = st.session_state.get("autoimmune_score", 0)

        fig, ax = plt.subplots(figsize=(4,2))

        colors_list = ['green','lightgreen','yellow','orange','red']
        ranges = [0,20,40,60,80,100]

        for i in range(len(ranges)-1):
            theta = np.linspace(np.pi*(1-ranges[i]/100), np.pi*(1-ranges[i+1]/100), 100)
            ax.plot(np.cos(theta), np.sin(theta), linewidth=20, color=colors_list[i])

        angle = np.pi * (1 - score/100)
        ax.arrow(0,0,0.7*np.cos(angle),0.7*np.sin(angle),
                 head_width=0.05, head_length=0.1, fc='black')

        ax.set_aspect('equal')
        ax.axis('off')

        gauge_path = "gauge.png"
        plt.savefig(gauge_path, bbox_inches='tight')
        plt.close()

        content.append(Paragraph("<b>Autoimmune Risk Meter</b>", styles['Heading2']))
        content.append(Image(gauge_path, width=300, height=180))
        content.append(Spacer(1, 10))

        # =========================
        # DETAILS
        # =========================
        risk_level = st.session_state.get("risk_level", "N/A")
        autoimmune_type = st.session_state.get("autoimmune_type", "N/A")
        disease = st.session_state.get("disease", "N/A")

        content.append(Paragraph(
            f"Score: {score}%<br/>"
            f"Risk Level: {risk_level}<br/>"
            f"Condition: {autoimmune_type}",
            styles['Normal']
        ))

        content.append(Spacer(1, 10))

        # =========================
        # DOCTOR
        # =========================
        doctor_map = {
            "Autoimmune_Disease": "Consult Rheumatologist",
            "Anemia": "Consult Hematologist",
            "Diabetes": "Consult Endocrinologist",
            "Kidney_Disorder": "Consult Nephrologist"
        }

        doctor = doctor_map.get(disease, "Consult Specialist")

        content.append(Paragraph("<b>Recommended Doctor</b>", styles['Heading2']))
        content.append(Paragraph(doctor, styles['Normal']))

        # =========================
        # MEDICATION
        # =========================
        medication_map = {
            "Autoimmune_Disease": "Steroids + Immunosuppressants",
            "Anemia": "Iron Supplements",
            "Diabetes": "Metformin / Insulin",
            "Kidney_Disorder": "ACE Inhibitors"
        }

        treatment = medication_map.get(disease, "Consult Specialist")

        content.append(Paragraph("<b>Recommended Medication</b>", styles['Heading2']))
        content.append(Paragraph(treatment, styles['Normal']))

        # =========================
        # BUILD
        # =========================
        doc.build(content)

        st.download_button(
            "Download Report",
            buffer.getvalue(),
            file_name="Final_Report.pdf",
            mime="application/pdf"
        )

# ===============================
# AI DASHBOARD (UPGRADED)
# ===============================
if page == "AI Dashboard":

    st.title("AI Clinical Dashboard")

    uploaded_file = st.file_uploader("Upload Dataset", type=["csv"],key="ai_dataset_uploader")

    if uploaded_file:

        df_dash = pd.read_csv(uploaded_file)

        st.success("Dataset Loaded")

        st.dataframe(df_dash.head())

        # ==============================
        # DISTRIBUTION
        # ==============================
        if "Diagnosis" in df_dash.columns:
            fig = px.histogram(df_dash, x="Diagnosis", color="Diagnosis", title="Disease Distribution")
            st.plotly_chart(fig)

        # ==============================
        # TRAIN ALL MODELS
        # ==============================
        if st.button("Train All Models",key="ai_train_btn"):

            df_train = df_dash.copy()

            # Encode
            for col in df_train.select_dtypes(include=["object"]).columns:
                df_train[col] = LabelEncoder().fit_transform(df_train[col])

            X = df_train.drop(columns=["Patient_ID", "Diagnosis"], errors='ignore')
            y = df_train["Diagnosis"]

            X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.25, random_state=42, stratify=y)

            models = {
                "CatBoost": CatBoostClassifier(verbose=False),
                "Random Forest": RandomForestClassifier(),
                "SVM": make_pipeline(StandardScaler(), SVC(kernel="rbf", C=10, gamma=0.1, probability=True))
            }

            results = {}

            for name, model in models.items():
                model.fit(X_train, y_train)
                pred = model.predict(X_test)
                acc = accuracy_score(y_test, pred)
                results[name] = round(acc * 100, 2)

            # ==============================
            # SHOW RESULTS
            # ==============================
            result_df = pd.DataFrame(results.items(), columns=["Model", "Accuracy (%)"])

            st.subheader("Model Comparison")
            st.dataframe(result_df)

            fig = px.bar(result_df, x="Model", y="Accuracy (%)", color="Model")
            st.plotly_chart(fig)

            # ==============================
            # CONFUSION MATRIX (CatBoost)
            # ==============================
            st.subheader("Confusion Matrix")

            best_model = models["CatBoost"]
            y_pred = best_model.predict(X_test)

            cm = confusion_matrix(y_test, y_pred)
            fig = px.imshow(cm, text_auto=True)
            st.plotly_chart(fig)

            # ==============================
            # FEATURE IMPORTANCE
            # ==============================

            st.subheader("Clinical Overview")

            clinical_features = [
                "Glucose_Fasting",
                "Hemoglobin",
                "Creatinine",
                "CRP",
                "WBC_Count"
            ]

            clinical_df = df_dash[clinical_features]

            from sklearn.preprocessing import MinMaxScaler
            scaler = MinMaxScaler()

            scaled = scaler.fit_transform(clinical_df)

            scaled_df = pd.DataFrame(scaled, columns=clinical_features)

            mean_values = scaled_df.mean().sort_values(ascending=True)

            mean_df = mean_values.reset_index()
            mean_df.columns = ["Feature", "Score"]

            fig = px.bar(
                mean_df,
                x="Score",
                y="Feature",
                orientation="h",
                color="Score",
                title="Clinical Parameter Status"
            )

            st.plotly_chart(fig, use_container_width=True)

            st.subheader("Clinical Interpretation")

            for _, row in mean_df.iterrows():
                if row["Score"] > 0.7:
                    status = "🔴 High Risk"
                elif row["Score"] > 0.4:
                    status = "🟡 Moderate"
                else:
                    status = "🟢 Normal"

                st.write(f"{row['Feature']}: {status}")

      

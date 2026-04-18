import pandas as pd
import numpy as np

np.random.seed(42)

n_normal = 2000
n_diabetes = 1000
n_anemia = 800
n_kidney = 700
n_autoimmune = 500

def base_data(n):
    return pd.DataFrame({
        "Age": np.random.randint(18, 85, n),
        "Gender": np.random.choice(["Male", "Female"], n),
        "WBC_Count": np.random.normal(7500, 1500, n),
        "Neutrophils_%": np.random.normal(60, 8, n),
        "Hemoglobin": np.random.normal(13.5, 1.5, n),
        "MCV": np.random.normal(88, 6, n),
        "ALT": np.random.normal(30, 10, n),
        "AST": np.random.normal(28, 8, n),
        "Creatinine": np.random.normal(1.0, 0.2, n),
        "Glucose_Fasting": np.random.normal(95, 15, n),
        "CRP": np.random.normal(3, 2, n),
        "ANA_Positive": np.random.binomial(1, 0.1, n)
    })

# Create datasets separately

normal = base_data(n_normal)
normal["Diagnosis"] = "Normal"

diabetes = base_data(n_diabetes)
diabetes["Glucose_Fasting"] = np.random.uniform(180, 250, n_diabetes)
diabetes["Diagnosis"] = "Diabetes"

anemia = base_data(n_anemia)
anemia["Hemoglobin"] = np.random.uniform(6, 9, n_anemia)
anemia["Diagnosis"] = "Anemia"

kidney = base_data(n_kidney)
kidney["Creatinine"] = np.random.uniform(2.0, 3.0, n_kidney)
kidney["Diagnosis"] = "Kidney_Disorder"

autoimmune = base_data(n_autoimmune)
autoimmune["ANA_Positive"] = 1
autoimmune["CRP"] = np.random.uniform(10, 30, n_autoimmune)
autoimmune["Diagnosis"] = "Autoimmune_Disease"

# Combine
df = pd.concat([normal, diabetes, anemia, kidney, autoimmune])

df = df.sample(frac=1).reset_index(drop=True)

df.insert(0, "Patient_ID", ["P" + str(100000+i) for i in range(len(df))])

df.to_csv("clinical_dataset.csv", index=False)

print(df["Diagnosis"].value_counts())
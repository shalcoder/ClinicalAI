import pandas as pd
import pickle
from catboost import CatBoostClassifier

# Load model
model = CatBoostClassifier()
model.load_model("catboost_model.cbm")

with open("label_encoder.pkl", "rb") as f:
    label_encoder = pickle.load(f)

df = pd.read_csv("clinical_dataset.csv")

def encode_gender(value):
    return 0 if value.lower() == "male" else 1

def predict_row(row):

    row = row.copy()
    row["Gender"] = encode_gender(str(row["Gender"]))

    features = row.drop(["Patient_ID", "Diagnosis"])
    pred = model.predict(features.values.reshape(1, -1))
    disease = label_encoder.inverse_transform(pred.astype(int))[0]

    return disease

def search_by_id():
    pid = input("Enter Patient ID: ")
    patient = df[df["Patient_ID"] == pid]

    if patient.empty:
        print("Patient not found")
        return

    patient_row = patient.iloc[0]
    prediction = predict_row(patient_row)

    print("\n===== PATIENT REPORT =====")
    print("Predicted Disease:", prediction)
    print("Actual Disease:", patient_row["Diagnosis"])

def manual_input():

    data = {}

    for col in df.columns:
        if col not in ["Patient_ID", "Diagnosis"]:
            if col == "Gender":
                data["Gender"] = encode_gender(input("Enter Gender (Male/Female): "))
            else:
                data[col] = float(input(f"Enter {col}: "))

    temp_df = pd.DataFrame([data])
    pred = model.predict(temp_df.values.reshape(1, -1))
    disease = label_encoder.inverse_transform(pred.astype(int))[0]

    print("\nPredicted Disease:", disease)

if __name__ == "__main__":

    print("\n===== CLINICAL AI SYSTEM =====")
    print("1. Search by Patient ID")
    print("2. Manual Input")

    choice = input("Select option: ")

    if choice == "1":
        search_by_id()
    elif choice == "2":
        manual_input()
    else:
        print("Invalid Option")
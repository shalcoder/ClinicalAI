import pandas as pd
import pickle
from catboost import CatBoostClassifier
from sklearn.preprocessing import LabelEncoder
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score, classification_report

# Load dataset
df = pd.read_csv("clinical_dataset.csv")

# Encode Gender
df["Gender"] = df["Gender"].map({"Male": 0, "Female": 1})

X = df.drop(columns=["Patient_ID", "Diagnosis"])
y = df["Diagnosis"]

label_encoder = LabelEncoder()
y_encoded = label_encoder.fit_transform(y)

X_train, X_test, y_train, y_test = train_test_split(
    X, y_encoded,
    test_size=0.25,
    random_state=42,
    stratify=y_encoded
)

model = CatBoostClassifier(
    iterations=800,
    depth=8,
    learning_rate=0.05,
    loss_function="MultiClass",
    auto_class_weights="Balanced",
    random_state=42,
    verbose=False
)

model.fit(X_train, y_train)

y_pred = model.predict(X_test)

print("Accuracy:", accuracy_score(y_test, y_pred))
print(classification_report(y_test, y_pred))

model.save_model("catboost_model.cbm")

with open("label_encoder.pkl", "wb") as f:
    pickle.dump(label_encoder, f)

print("Model Saved Successfully")
print("\nClass Distribution:")
print(df["Diagnosis"].value_counts())
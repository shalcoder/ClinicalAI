import pandas as pd

# Read UTF-16 encoded CSV
df = pd.read_csv(
    "clinical_autoimmune_advanced_5000.csv",
    encoding="utf-16"
)

# Save clean UTF-8 version
df.to_csv("clinical_autoimmune_clean.csv", index=False, encoding="utf-8")

print("CSV cleaned successfully")
print(df.shape)
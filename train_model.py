
import os
import pandas as pd
import joblib

from sklearn.model_selection import train_test_split
from sklearn.compose import ColumnTransformer
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder, StandardScaler
from sklearn.impute import SimpleImputer
from sklearn.linear_model import LogisticRegression
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import (
    accuracy_score,
    precision_score,
    recall_score,
    f1_score,
    confusion_matrix,
    classification_report,
    roc_auc_score
)

# --------------------------------------------------
# 1. FILE PATHS
# --------------------------------------------------

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

DATA_PATH = os.path.join(BASE_DIR, "diabetic_data.csv")
MODEL_DIR = os.path.join(BASE_DIR, "ml_models")
MODEL_PATH = os.path.join(MODEL_DIR, "best_model.joblib")

# --------------------------------------------------
# 2. FEATURES USED BY THE DJANGO APPLICATION
# Keep these names and their order consistent
# with patients/views.py
# --------------------------------------------------

NUMERIC_FEATURES = [
    "time_in_hospital",
    "num_lab_procedures",
    "num_procedures",
    "num_medications",
    "number_outpatient",
    "number_emergency",
    "number_inpatient",
    "number_diagnoses"
]

CATEGORICAL_FEATURES = [
    "race",
    "gender",
    "age",
    "admission_type_id",
    "max_glu_serum",
    "A1Cresult",
    "insulin",
    "diabetesMed"
]

FEATURES = NUMERIC_FEATURES + CATEGORICAL_FEATURES
TARGET_COLUMN = "readmitted"

# --------------------------------------------------
# 3. LOAD DATASET
# --------------------------------------------------

print("\nLoading diabetes dataset...")

if not os.path.exists(DATA_PATH):
    raise FileNotFoundError(
        f"Dataset not found: {DATA_PATH}\n"
        "Place diabetic_data.csv inside the ML_Project folder."
    )

df = pd.read_csv(DATA_PATH, low_memory=False)

print("Dataset loaded successfully.")
print("Original dataset shape:", df.shape)

# Check required columns
required_columns = FEATURES + [TARGET_COLUMN]

missing_columns = [
    column for column in required_columns
    if column not in df.columns
]

if missing_columns:
    raise ValueError(
        "The dataset is missing these required columns: "
        + ", ".join(missing_columns)
    )

# --------------------------------------------------
# 4. CLEAN DATA
# --------------------------------------------------

data = df[required_columns].copy()

# Remove rows without a target value
data = data.dropna(subset=[TARGET_COLUMN])

# Positive class: readmission within 30 days
# Negative class: readmitted after 30 days or not readmitted
data["target"] = (
    data[TARGET_COLUMN].astype(str).str.strip() == "<30"
).astype(int)

X = data[FEATURES].copy()
y = data["target"].copy()

# Convert numeric columns into numbers
for column in NUMERIC_FEATURES:
    X[column] = pd.to_numeric(
        X[column].replace("?", pd.NA),
        errors="coerce"
    )

# Clean categorical columns
for column in CATEGORICAL_FEATURES:
    X[column] = (
        X[column]
        .astype("string")
        .fillna("Unknown")
        .str.strip()
        .replace({"?": "Unknown", "": "Unknown"})
        .astype(str)
    )

print("\nData cleaning completed.")
print("Features:", len(FEATURES))
print("Total usable records:", len(X))
print("\nTarget distribution:")
print(y.value_counts().rename({
    0: "No readmission within 30 days",
    1: "Readmitted within 30 days"
}))

# --------------------------------------------------
# 5. SPLIT DATA
# --------------------------------------------------

X_train, X_test, y_train, y_test = train_test_split(
    X,
    y,
    test_size=0.20,
    random_state=42,
    stratify=y
)

print("\nTraining records:", len(X_train))
print("Testing records:", len(X_test))

# --------------------------------------------------
# 6. PREPROCESSING
# --------------------------------------------------

numeric_transformer = Pipeline(steps=[
    ("imputer", SimpleImputer(strategy="median")),
    ("scaler", StandardScaler())
])

categorical_transformer = Pipeline(steps=[
    ("imputer", SimpleImputer(strategy="most_frequent")),
    ("encoder", OneHotEncoder(handle_unknown="ignore"))
])

preprocessor = ColumnTransformer(
    transformers=[
        ("numeric", numeric_transformer, NUMERIC_FEATURES),
        ("categorical", categorical_transformer,
         CATEGORICAL_FEATURES)
    ]
)

# --------------------------------------------------
# 7. TRAIN AND COMPARE MODELS
# --------------------------------------------------

models = {
    "Logistic Regression": LogisticRegression(
        max_iter=1000,
        class_weight="balanced",
        random_state=42
    ),

    "Random Forest": RandomForestClassifier(
        n_estimators=150,
        class_weight="balanced",
        random_state=42,
        n_jobs=-1
    )
}

best_model = None
best_model_name = None
best_f1 = -1
results = []

for model_name, classifier in models.items():

    print("\n" + "=" * 50)
    print("Training:", model_name)
    print("=" * 50)

    pipeline = Pipeline(steps=[
        ("preprocessor", preprocessor),
        ("classifier", classifier)
    ])

    pipeline.fit(X_train, y_train)

    # Predictions
    y_pred = pipeline.predict(X_test)
    y_probability = pipeline.predict_proba(X_test)[:, 1]

    # Evaluation metrics
    accuracy = accuracy_score(y_test, y_pred)
    precision = precision_score(
        y_test, y_pred, zero_division=0
    )
    recall = recall_score(
        y_test, y_pred, zero_division=0
    )
    f1 = f1_score(
        y_test, y_pred, zero_division=0
    )
    auc = roc_auc_score(y_test, y_probability)

    print(f"Accuracy  : {accuracy * 100:.2f}%")
    print(f"Precision : {precision * 100:.2f}%")
    print(f"Recall    : {recall * 100:.2f}%")
    print(f"F1 Score  : {f1 * 100:.2f}%")
    print(f"ROC-AUC   : {auc:.4f}")

    print("\nConfusion Matrix:")
    print(confusion_matrix(y_test, y_pred))

    print("\nClassification Report:")
    print(classification_report(
        y_test,
        y_pred,
        target_names=[
            "No readmission within 30 days",
            "Readmitted within 30 days"
        ],
        zero_division=0
    ))

    results.append({
        "Model": model_name,
        "Accuracy (%)": round(accuracy * 100, 2),
        "Precision (%)": round(precision * 100, 2),
        "Recall (%)": round(recall * 100, 2),
        "F1 Score (%)": round(f1 * 100, 2),
        "ROC-AUC": round(auc, 4)
    })

    # Select the model using F1 score rather than
    # accuracy alone because readmissions are imbalanced.
    if f1 > best_f1:
        best_f1 = f1
        best_model = pipeline
        best_model_name = model_name

# --------------------------------------------------
# 8. DISPLAY MODEL COMPARISON
# --------------------------------------------------

print("\n" + "=" * 60)
print("MODEL COMPARISON")
print("=" * 60)

results_df = pd.DataFrame(results)
print(results_df.to_string(index=False))

# --------------------------------------------------
# 9. SAVE THE BEST MODEL
# --------------------------------------------------

os.makedirs(MODEL_DIR, exist_ok=True)

joblib.dump(best_model, MODEL_PATH)

print("\nBest model:", best_model_name)
print("Selection metric: F1 score")
print(f"Best F1 score: {best_f1 * 100:.2f}%")
print("\nModel saved successfully at:")
print(MODEL_PATH)

print("\nTraining completed successfully!")

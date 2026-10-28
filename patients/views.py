
import os
import joblib
import pandas as pd

from django.conf import settings
from django.shortcuts import render, redirect, get_object_or_404

from .forms import PatientForm
from .models import Patient


MODEL_PATH = os.path.join(
    settings.BASE_DIR,
    "ml_models",
    "best_model.joblib"
)

model = (
    joblib.load(MODEL_PATH)
    if os.path.exists(MODEL_PATH)
    else None
)

NUMERIC_FEATURES = [
    "time_in_hospital",
    "num_lab_procedures",
    "num_procedures",
    "num_medications",
    "number_outpatient",
    "number_emergency",
    "number_inpatient",
    "number_diagnoses",
]

CATEGORICAL_FEATURES = [
    "race",
    "gender",
    "age",
    "admission_type_id",
    "max_glu_serum",
    "A1Cresult",
    "insulin",
    "diabetesMed",
]


def home(request):
    return render(request, "home.html", {
        "total_patients": Patient.objects.count(),
        "high_risk": Patient.objects.filter(
            risk_level="High"
        ).count(),
        "model_ready": model is not None,
    })


def predict(request):
    if model is None:
        return render(request, "error.html", {
            "message": (
                "Model not found. Run python train_model.py "
                "before making predictions."
            )
        })

    if request.method == "POST":
        form = PatientForm(request.POST)

        if form.is_valid():
            d = form.cleaned_data

            # Prepare precisely the same feature columns as training.
            row = {
                col: d[col]
                for col in NUMERIC_FEATURES + CATEGORICAL_FEATURES
            }

            input_data = pd.DataFrame([row])

            for col in NUMERIC_FEATURES:
                input_data[col] = pd.to_numeric(
                    input_data[col], errors="coerce"
                )

            for col in CATEGORICAL_FEATURES:
                input_data[col] = (
                    input_data[col]
                    .fillna("Unknown")
                    .replace("?", "Unknown")
                    .astype(str)
                )

            # Column order must match the training feature order.
            input_data = input_data[
                NUMERIC_FEATURES + CATEGORICAL_FEATURES
            ]

            probability = float(
                model.predict_proba(input_data)[0, 1]
            )

            predicted = probability >= 0.5
            risk_level = "High" if predicted else "Lower"

            patient = Patient.objects.create(
                name=d["name"],
                age=d["age"],
                gender=d["gender"],
                race=d["race"],
                admission_type_id=d["admission_type_id"],
                time_in_hospital=d["time_in_hospital"],
                num_lab_procedures=d["num_lab_procedures"],
                num_procedures=d["num_procedures"],
                num_medications=d["num_medications"],
                number_outpatient=d["number_outpatient"],
                number_emergency=d["number_emergency"],
                number_inpatient=d["number_inpatient"],
                number_diagnoses=d["number_diagnoses"],
                max_glu_serum=d["max_glu_serum"],
                A1Cresult=d["A1Cresult"],
                insulin=d["insulin"],
                diabetesMed=d["diabetesMed"],
                risk_probability=round(probability * 100, 2),
                risk_level=risk_level,
                predicted_readmission=predicted,
            )

            return redirect(
                "report",
                patient_id=patient.id
            )

    else:
        form = PatientForm()

    return render(request, "predict.html", {
        "form": form
    })


def patients_list(request):
    return render(request, "patients.html", {
        "patients": Patient.objects.order_by("-created_at")
    })


def report(request, patient_id):
    patient = get_object_or_404(Patient, id=patient_id)

    return render(request, "report.html", {
        "patient": patient
    })

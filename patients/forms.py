
from django import forms


AGE_CHOICES = [
    ("[0-10)", "0–10 years"),
    ("[10-20)", "10–20 years"),
    ("[20-30)", "20–30 years"),
    ("[30-40)", "30–40 years"),
    ("[40-50)", "40–50 years"),
    ("[50-60)", "50–60 years"),
    ("[60-70)", "60–70 years"),
    ("[70-80)", "70–80 years"),
    ("[80-90)", "80–90 years"),
    ("[90-100)", "90–100 years"),
]

RACE_CHOICES = [
    ("Caucasian", "Caucasian"),
    ("AfricanAmerican", "African American"),
    ("Asian", "Asian"),
    ("Hispanic", "Hispanic"),
    ("Other", "Other"),
    ("Unknown", "Unknown / Missing"),
]

GENDER_CHOICES = [
    ("Female", "Female"),
    ("Male", "Male"),
    ("Unknown/Invalid", "Unknown / Invalid"),
]

GLUCOSE_CHOICES = [
    ("None", "Not measured"),
    ("Norm", "Normal"),
    (">200", "Above 200"),
    (">300", "Above 300"),
]

A1C_CHOICES = [
    ("None", "Not measured"),
    ("Norm", "Normal"),
    (">7", "Above 7"),
    (">8", "Above 8"),
]

INSULIN_CHOICES = [
    ("No", "No change"),
    ("Down", "Decreased"),
    ("Steady", "Steady"),
    ("Up", "Increased"),
]


class PatientForm(forms.Form):

    name = forms.CharField(
        max_length=100,
        label="Patient Name"
    )

    age = forms.ChoiceField(
        choices=AGE_CHOICES,
        label="Age Group"
    )

    gender = forms.ChoiceField(
        choices=GENDER_CHOICES,
        label="Gender"
    )

    race = forms.ChoiceField(
        choices=RACE_CHOICES,
        label="Race"
    )

    admission_type_id = forms.ChoiceField(
        choices=[
            (str(i), f"Admission Type {i}")
            for i in range(1, 9)
        ],
        label="Admission Type ID"
    )

    time_in_hospital = forms.IntegerField(
        min_value=1,
        max_value=14,
        label="Time in Hospital (Days)"
    )

    num_lab_procedures = forms.IntegerField(
        min_value=0,
        label="Number of Lab Procedures"
    )

    num_procedures = forms.IntegerField(
        min_value=0,
        label="Number of Procedures"
    )

    num_medications = forms.IntegerField(
        min_value=0,
        label="Number of Medications"
    )

    number_outpatient = forms.IntegerField(
        min_value=0,
        label="Previous Outpatient Visits"
    )

    number_emergency = forms.IntegerField(
        min_value=0,
        label="Previous Emergency Visits"
    )

    number_inpatient = forms.IntegerField(
        min_value=0,
        label="Previous Inpatient Visits"
    )

    number_diagnoses = forms.IntegerField(
        min_value=1,
        label="Number of Diagnoses"
    )

    max_glu_serum = forms.ChoiceField(
        choices=GLUCOSE_CHOICES,
        label="Maximum Glucose Serum"
    )

    A1Cresult = forms.ChoiceField(
        choices=A1C_CHOICES,
        label="HbA1c Result"
    )

    insulin = forms.ChoiceField(
        choices=INSULIN_CHOICES,
        label="Insulin Treatment"
    )

    diabetesMed = forms.ChoiceField(
        choices=[
            ("Yes", "Yes"),
            ("No", "No"),
        ],
        label="Diabetes Medication"
    )


from django.db import models


class Patient(models.Model):
    name = models.CharField(max_length=100)
    age = models.CharField(max_length=20)
    gender = models.CharField(max_length=20)
    race = models.CharField(max_length=40, default="Unknown")
    admission_type_id = models.CharField(max_length=10)

    time_in_hospital = models.IntegerField()
    num_lab_procedures = models.IntegerField()
    num_procedures = models.IntegerField()
    num_medications = models.IntegerField()
    number_outpatient = models.IntegerField()
    number_emergency = models.IntegerField()
    number_inpatient = models.IntegerField()
    number_diagnoses = models.IntegerField()

    max_glu_serum = models.CharField(max_length=20)
    A1Cresult = models.CharField(max_length=20)
    insulin = models.CharField(max_length=20)
    diabetesMed = models.CharField(max_length=10)

    risk_probability = models.FloatField()
    risk_level = models.CharField(max_length=20)
    predicted_readmission = models.BooleanField()

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name

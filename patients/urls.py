from django.urls import path
from . import views

urlpatterns = [
    path("", views.home, name="home"),
    path("predict/", views.predict, name="predict"),
    path("patients/", views.patients_list, name="patients"),
    path("report/<int:patient_id>/", views.report, name="report"),
]
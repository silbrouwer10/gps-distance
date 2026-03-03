from django.urls import path
from . import views

app_name = 'gpsapp'

urlpatterns = [
    path('', views.upload_csv_view, name='upload'),
    path("generate-pdf/", views.generate_pdf_view, name="generate_pdf"),
]
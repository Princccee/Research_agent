from django.contrib import admin
from django.urls import path, include
from .views import main, download_pdf

urlpatterns = [
    path('main/', main, name="main"),
    path("download_pdf/", download_pdf, name="download_pdf"),
]

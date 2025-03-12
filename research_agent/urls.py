from django.contrib import admin
from django.urls import path, include
from .views import research

urlpatterns = [
    path('research/', research, name = "research"),
]

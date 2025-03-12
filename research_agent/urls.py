from django.contrib import admin
from django.urls import path, include
from .views import research, main

urlpatterns = [
    path('research/', research, name = "research"),
    # path('use_case/', get_usecases, name="use_cases"),
    path('main/', main, name="main")
]

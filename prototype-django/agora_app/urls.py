"""
API URLs
"""
from django.urls import path
from . import views

urlpatterns = [
    path('saldos/', views.saldos_api, name='saldos-api'),
]

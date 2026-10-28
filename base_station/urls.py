from django.urls import path

from . import views

app_name = 'base_station'

urlpatterns = [
    path('metrics/', views.BaseStationMetricsView.as_view(), name='metrics'),
]

from django.urls import path

from . import views


app_name = 'open5gs'

urlpatterns = [
    path('', views.index, name='index'),
    path('subscriber/', views.subscriber, name='create'),
    path('subscriber/<str:imsi>/edit/', views.subscriber, name='edit'),
    path(
        'subscriber/<str:imsi>/delete/', views.delete_subscriber, name='delete'
    ),
]

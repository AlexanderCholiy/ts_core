from django.urls import path

from . import views


app_name = 'open5gs'

urlpatterns = [
    path('', views.index, name='index'),
    path('subscriber/', views.subscriber, name='create'),
    path('subscriber/<int:imsi>/edit/', views.subscriber, name='edit'),
    path(
        'subscriber/<int:imsi>/delete/', views.delete_subscriber, name='delete'
    ),
]

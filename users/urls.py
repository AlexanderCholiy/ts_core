from django.urls import path

from . import views


app_name = 'users'

urlpatterns = [
    path('', views.index, name='index'),
    path('register/', views.register, name='register'),
    path('activate/<uidb64>/<token>/', views.activate, name='activate'),
    path('change-email/', views.change_email, name='change_email'),
]

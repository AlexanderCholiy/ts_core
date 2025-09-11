from django.urls import path

from . import views

app_name = 'users'

urlpatterns = [
    path('register/', views.register, name='register'),
    path('activate/<uidb64>/<token>/', views.activate, name='activate'),
    path('change-email/', views.change_email, name='change_email'),
    path(
        'confirm-email-change/<uidb64>/<token>/',
        views.confirm_email_change, name='confirm_email_change'
    ),
    path('profile/', views.profile, name='profile'),
]

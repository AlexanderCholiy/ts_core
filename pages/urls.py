from django.urls import path

from .views import AboutTemplateView

app_name = 'pages'

urlpatterns = [
    path('about/', AboutTemplateView.as_view(), name='about'),
]

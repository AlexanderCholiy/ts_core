from django.urls import path

from links.views import resource_iframe_view

app_name = 'links'

urlpatterns = [
    path('resource/<int:pk>/', resource_iframe_view, name='iframe_detail'),
]

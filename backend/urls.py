import debug_toolbar
from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.contrib.auth import views as auth_views
from django.urls import include, path, re_path
from drf_yasg import openapi
from drf_yasg.views import get_schema_view
from rest_framework import permissions

from users.forms import AuthForm
from users.views import CustomPasswordResetView, CustomLoginView


handler400 = 'core.views.bad_request'
handler403 = 'core.views.permission_denied'
handler404 = 'core.views.page_not_found'
handler500 = 'core.views.server_error'
handler429 = 'core.views.too_many_requests'

schema_view = get_schema_view(
    openapi.Info(
        title='NT API',
        default_version='v1',
        description='Документация для проекта NT',
        contact=openapi.Contact(email='alexander.choliy@gmail.com'),
        license=openapi.License(name='BSD License'),
    ),
    public=True,
    permission_classes=(permissions.AllowAny,),
)

swagger_urls = [
    re_path(
        r'^api/swagger(?P<format>\.json|\.yaml)$',
        schema_view.without_ui(cache_timeout=0),
        name='schema-json',
    ),
    re_path(
        r'^api/swagger/$',
        schema_view.with_ui('swagger', cache_timeout=0),
        name='schema-swagger-ui',
    ),
    re_path(
        r'^api/redoc/$',
        schema_view.with_ui('redoc', cache_timeout=0),
        name='schema-redoc',
    ),
]

auth_urlpatterns = [
    path(
        'login/',
        CustomLoginView.as_view(form_class=AuthForm),
        name='login',
    ),
    path(
        'logout/',
        auth_views.LogoutView.as_view(next_page='login'),
        name='logout',
    ),
    path(
        'password_change/',
        auth_views.PasswordChangeView.as_view(),
        name='password_change',
    ),
    path(
        'password_change/done/',
        auth_views.PasswordChangeDoneView.as_view(),
        name='password_change_done',
    ),
    path(
        'password_reset/',
        CustomPasswordResetView.as_view(),
        name='password_reset',
    ),
    path(
        'password_reset/done/',
        auth_views.PasswordResetDoneView.as_view(),
        name='password_reset_done',
    ),
    path(
        'reset/<uidb64>/<token>/',
        auth_views.PasswordResetConfirmView.as_view(),
        name='password_reset_confirm',
    ),
    path(
        'reset/done/',
        auth_views.PasswordResetCompleteView.as_view(),
        name='password_reset_complete',
    ),
]

app_urls = [
    path('', include('open5gs.urls')),
    path('users/', include('users.urls')),
    path('admin/', admin.site.urls),
    path('pages/', include('pages.urls')),
]

urlpatterns = swagger_urls + auth_urlpatterns + app_urls

if settings.DEBUG:
    urlpatterns += (path('__debug__/', include(debug_toolbar.urls)),)
    urlpatterns += static(
        settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += swagger_urls

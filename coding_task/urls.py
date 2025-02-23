# coding_task/urls.py
from django.contrib import admin
from django.urls import path, include
from drf_spectacular.views import (
    SpectacularAPIView,
    SpectacularRedocView,
    SpectacularSwaggerView,
)

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/', include('coding_task.api.urls')),
    path('schema/', SpectacularAPIView.as_view(), name='schema'),
    path('', SpectacularRedocView.as_view(url='/schema/'), name='redoc'),
    path('swagger/', SpectacularSwaggerView.as_view(url='/schema/'), name='swagger-ui'),
]


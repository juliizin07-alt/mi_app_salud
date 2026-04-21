from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),

    # 🔥 ESTA LÍNEA ES CLAVE
    path('', include('mi_app_salud.urls')),
]
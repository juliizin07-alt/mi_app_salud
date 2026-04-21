from django.contrib import admin
from django.urls import path
from salud.views import inicio, registro, registrar_estado, historial_paciente
from django.contrib.auth import views as auth_views
from django.urls import path, include

urlpatterns = [
    path('', include('tu_app.urls')),
]

urlpatterns = [
    path('admin/', admin.site.urls),

    path('', inicio, name='inicio'),

    path('login/', auth_views.LoginView.as_view(), name='login'),
    path('logout/', auth_views.LogoutView.as_view(), name='logout'),

    path('registro/', registro, name='registro'),

    path('estado/<int:paciente_id>/<str:estado>/', registrar_estado, name='estado'),

    # 👇 ESTA LÍNEA TE FALTA
    path('historial/<int:paciente_id>/', historial_paciente, name='historial'),
]
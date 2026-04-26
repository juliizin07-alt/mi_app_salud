from django.urls import path
from . import views

urlpatterns = [
    path('', views.lista_pacientes, name='inicio'),
    path('actualizar-estado/<int:paciente_id>/', views.actualizar_estado, name='actualizar_estado'),

    # API
    path('api/pacientes/', views.api_pacientes, name='api_pacientes'),
    path('api/cambiar-estado/<int:paciente_id>/', views.api_cambiar_estado, name='api_cambiar_estado'),
]
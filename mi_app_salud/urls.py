# urls.py

from django.urls import path
from . import views

urlpatterns = [
path(
    'historial/<int:paciente_id>/',
    views.historial_paciente,
    name='historial_paciente'
),
    # WEB
    path('', views.lista_pacientes, name='inicio'),
    path('crear-paciente/', views.crear_paciente, name='crear_paciente'),
    path(
        'crear-recordatorio/<int:paciente_id>/',
        views.crear_recordatorio,
        name='crear_recordatorio'
    ),

    # API
    path(
        'api/pacientes/',
        views.api_pacientes,
        name='api_pacientes'
    ),

    path(
        'api/cambiar-estado/<int:paciente_id>/',
        views.api_cambiar_estado,
        name='api_cambiar_estado'
    ),

    path(
        'api/segundo-contacto/',
        views.segundo_contacto,
        name='segundo_contacto'
    ),

    path(
        'api/tercer-contacto/',
        views.tercer_contacto,
        name='tercer_contacto'
    ),
]
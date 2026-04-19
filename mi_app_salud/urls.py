from django.urls import path
from . import views

urlpatterns = [
    path('', views.inicio, name='inicio'),

    path('historial/<int:paciente_id>/', views.historial_paciente, name='historial'),

    # ⭐ ESTE ES EL NUEVO (EL IMPORTANTE)
    path('estado/<int:paciente_id>/<str:estado>/', views.cambiar_estado, name='cambiar_estado'),
]
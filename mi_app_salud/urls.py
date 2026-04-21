from django.urls import path
from . import views

urlpatterns = [
    path('', views.lista_pacientes, name='inicio'),

    path('actualizar-estado/<int:paciente_id>/', views.actualizar_estado, name='actualizar_estado'),
]
path('estado/<int:paciente_id>/<str:estado>/', views.actualizar_estado, name='actualizar_estado'),
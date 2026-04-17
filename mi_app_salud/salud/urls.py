from django.urls import path
from . import views

urlpatterns = [
    path('', views.inicio, name='inicio'),

    path(
        'estado/<int:paciente_id>/<str:estado>/',
        views.registrar_medicacion,
        name='registrar_medicacion'
    ),
]
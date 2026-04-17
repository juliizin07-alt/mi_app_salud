from django.shortcuts import render, get_object_or_404, redirect
from .models import Paciente, RegistroSalud


def inicio(request):
    pacientes = Paciente.objects.all()
    return render(request, 'inicio.html', {'pacientes': pacientes})


def registrar_medicacion(request, paciente_id, estado):
    paciente = get_object_or_404(Paciente, id=paciente_id)

    RegistroSalud.objects.create(
        paciente=paciente,
        estado=estado
    )

    return redirect('inicio')
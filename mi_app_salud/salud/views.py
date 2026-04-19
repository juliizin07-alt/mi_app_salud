from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.decorators import login_required
from .models import Paciente, RegistroSalud


# 🏠 DASHBOARD PRINCIPAL
@login_required
def inicio(request):
    pacientes = Paciente.objects.all()

    alertas = []

    for paciente in pacientes:
        ultimo = paciente.registros.last()

        if ultimo:
            if ultimo.estado_fisico == "CRITICO":
                alertas.append(f"{paciente.nombre} está en estado CRÍTICO")
            elif ultimo.estado_fisico == "DOLOR":
                alertas.append(f"{paciente.nombre} tiene dolor")

    return render(request, 'inicio.html', {
        'pacientes': pacientes,
        'alertas': alertas
    })


# 🆕 REGISTRO DE USUARIO
def registro(request):
    if request.method == "POST":
        form = UserCreationForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('login')
    else:
        form = UserCreationForm()

    return render(request, 'registro.html', {'form': form})


# 🔄 ACTUALIZAR ESTADO
@login_required
def registrar_estado(request, paciente_id, estado):
    paciente = get_object_or_404(Paciente, id=paciente_id)

    RegistroSalud.objects.create(
        paciente=paciente,
        estado_fisico=estado,
        estado_emocional="NEUTRO"  # podés cambiar esto después
    )

    return redirect('inicio')


# 📋 HISTORIAL DEL PACIENTE
@login_required
def historial_paciente(request, paciente_id):
    paciente = get_object_or_404(Paciente, id=paciente_id)
    registros = paciente.registros.all().order_by('-fecha')

    return render(request, 'historial.html', {
        'paciente': paciente,
        'registros': registros
    })
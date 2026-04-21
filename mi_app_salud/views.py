from django.shortcuts import render, get_object_or_404, redirect
from django.http import JsonResponse
from django.contrib.auth.decorators import login_required

from .models import Paciente, RegistroSalud, Recordatorio
from .forms import PacienteForm


# 🏠 LISTA PRINCIPAL (UCI)
@login_required
def lista_pacientes(request):
    pacientes = list(Paciente.objects.all())

    def prioridad(p):
        ultimo = p.registros.order_by('-fecha').first()

        if not ultimo:
            return 2

        estado = ultimo.estado_fisico.upper().strip()

        if estado == "CRITICO":
            return 0
        if estado == "DOLOR":
            return 1
        return 2

    pacientes.sort(key=prioridad)

    return render(request, 'mi_app_salud/inicio.html', {
        'pacientes': pacientes
    })


# ⚡ CAMBIAR ESTADO (UCI CORE)
@login_required
def cambiar_estado(request, paciente_id, estado):
    paciente = get_object_or_404(Paciente, id=paciente_id)

    estado = estado.upper().strip()

    RegistroSalud.objects.create(
        paciente=paciente,
        estado_fisico=estado,
        estado_emocional="NEUTRO"
    )

    return JsonResponse({
        "ok": True,
        "estado": estado
    })


# 🧑‍⚕️ CREAR PACIENTE
@login_required
def crear_paciente(request):
    form = PacienteForm(request.POST or None)

    if form.is_valid():
        form.save()
        return redirect('inicio')

    return render(request, 'mi_app_salud/crear_paciente.html', {
        'form': form
    })


# 📝 RECORDATORIOS
@login_required
def crear_recordatorio(request, paciente_id):
    paciente = get_object_or_404(Paciente, id=paciente_id)

    if request.method == "POST":
        texto = request.POST.get("texto")
        if texto:
            Recordatorio.objects.create(
                paciente=paciente,
                texto=texto
            )

    return redirect('inicio')
from django.shortcuts import get_object_or_404, redirect
from .models import Paciente, RegistroSalud

def actualizar_estado(request, paciente_id):
    paciente = get_object_or_404(Paciente, id=paciente_id)

    if request.method == 'POST':
        estado = request.POST.get('estado')

        RegistroSalud.objects.create(
            paciente=paciente,
            estado=estado
        )

    return redirect('inicio')

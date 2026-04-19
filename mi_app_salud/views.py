from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse

from .models import Paciente, RegistroSalud, Recordatorio
from .forms import PacienteForm


# 🏠 DASHBOARD PRINCIPAL
@login_required
def inicio(request):
    pacientes = Paciente.objects.all()
    alertas = []

    for p in pacientes:
        ultimo = p.registros.order_by('-fecha').first()

        if ultimo:
            estado = ultimo.estado_fisico.upper().strip()
            p.ultimo_estado = estado

            # 🎨 estado visual tipo app
            if estado == "CRITICO":
                p.estado_color = "red"
                alertas.append(f"🚨 {p.nombre} crítico")

            elif estado == "DOLOR":
                p.estado_color = "yellow"
                alertas.append(f"⚠️ {p.nombre} con dolor")

            else:
                p.estado_color = "green"

        else:
            p.ultimo_estado = "SIN REGISTRO"
            p.estado_color = "gray"

    return render(request, 'mi_app_salud/inicio.html', {
        'pacientes': pacientes,
        'alertas': alertas
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


# ⚡ CAMBIAR ESTADO (AJAX REAL)
@login_required
def cambiar_estado(request, paciente_id, estado):
    paciente = get_object_or_404(Paciente, id=paciente_id)

    estado = estado.upper().strip()
    ESTADOS_VALIDOS = ["OK", "DOLOR", "CRITICO"]

    if estado not in ESTADOS_VALIDOS:
        return JsonResponse({"ok": False})

    registro = RegistroSalud.objects.create(
        paciente=paciente,
        estado_fisico=estado,
        estado_emocional="NEUTRO"
    )

    return JsonResponse({
        "ok": True,
        "paciente_id": paciente.id,
        "estado": estado,
        "id_registro": registro.id
    })


# 📋 HISTORIAL PACIENTE
@login_required
def historial_paciente(request, paciente_id):
    paciente = get_object_or_404(Paciente, id=paciente_id)

    registros = paciente.registros.order_by('-fecha')

    return render(request, 'mi_app_salud/historial.html', {
        'paciente': paciente,
        'registros': registros
    })


# ➕ CREAR RECORDATORIO
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


# ✔ TOGGLE RECORDATORIO
@login_required
def toggle_recordatorio(request, id):
    r = get_object_or_404(Recordatorio, id=id)
    r.hecho = not r.hecho
    r.save()
    return redirect('inicio')
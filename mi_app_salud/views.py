from django.shortcuts import render, get_object_or_404, redirect
from django.http import JsonResponse
from django.contrib.auth.decorators import login_required

from .models import Paciente, RegistroSalud, Recordatorio
from .forms import PacienteForm
from .clinical_engine import evaluar_paciente
from .alerts import enviar_whatsapp


# =========================
# 📡 API - LISTA PACIENTES
# =========================
def api_pacientes(request):
    pacientes = Paciente.objects.all()
    data = []

    for p in pacientes:
        ultimo = p.registros.order_by('-fecha').first()
        estado = ultimo.estado_fisico if ultimo else "SIN DATOS"

        data.append({
            "id": p.id,
            "nombre": p.nombre,
            "estado": estado
        })

    return JsonResponse({"pacientes": data})


# =========================
# 🏠 LISTA PRINCIPAL (UCI)
# =========================
@login_required
def lista_pacientes(request):
    pacientes = Paciente.objects.all()

    def prioridad(p):
        ultimo = p.registros.order_by('-fecha').first()

        if not ultimo:
            return 2

        estado = ultimo.estado_fisico.upper().strip()

        if estado == "CRITICO":
            return 0
        elif estado == "DOLOR":
            return 1
        return 2

    pacientes = sorted(pacientes, key=prioridad)

    return render(request, 'mi_app_salud/inicio.html', {
        'pacientes': pacientes
    })


# =========================
# ⚡ API CAMBIAR ESTADO
# =========================
from django.shortcuts import get_object_or_404
from django.http import JsonResponse

from .models import Paciente, RegistroSalud
from .clinical_engine import evaluar_paciente
from .alerts import enviar_whatsapp


def api_cambiar_estado(request, paciente_id):
    # 🧍‍♂️ Obtener paciente
    paciente = get_object_or_404(Paciente, id=paciente_id)

    # 📥 Datos desde frontend
    estado = request.GET.get("estado")
    ubicacion = request.GET.get("ubicacion", "No disponible")

    # 🚨 Validación
    if not estado:
        return JsonResponse({"error": "Falta estado"}, status=400)

    estado = estado.upper().strip()

    # 📝 Guardar registro
    RegistroSalud.objects.create(
        paciente=paciente,
        estado_fisico=estado,
        estado_emocional="NEUTRO"
    )

    # 🧠 Evaluación clínica
    historial = RegistroSalud.objects.filter(paciente=paciente)
    decision = evaluar_paciente(paciente, estado, historial)

    print("🧠 DECISIÓN:", decision)

    # 🚨 ALERTA REAL (con ubicación)
    if decision["nivel"] >= 3:
        mensaje = f"""
🚨 ALERTA MÉDICA

Paciente: {paciente.nombre}
Estado: {estado}

📍 Ubicación:
{ubicacion}

⚠️ Requiere atención inmediata
"""
        enviar_whatsapp(mensaje)
        print("📲 WhatsApp enviado")

    return JsonResponse({
        "ok": True,
        "paciente": paciente.nombre,
        "estado": estado,
        "ubicacion": ubicacion,
        "decision": decision
    })
    if not estado:
        return JsonResponse({"error": "Falta estado"})

    estado = estado.upper().strip()

    # guardar registro
    RegistroSalud.objects.create(
        paciente=paciente,
        estado_fisico=estado,
        estado_emocional="NEUTRO"
    )

    # historial
    historial = RegistroSalud.objects.filter(paciente=paciente)

    # IA / lógica clínica
    decision = evaluar_paciente(paciente, estado, historial)

    print("🧠 DECISIÓN:", decision)

    # 🚨 ESCALAMIENTO PROFESIONAL
    if decision["nivel"] == 4:
        mensaje = f"""
🚨 EMERGENCIA
Paciente: {paciente.nombre}
Estado: {estado}

⚠️ Requiere atención inmediata
📍 Ubicación: pendiente integración GPS
"""
        enviar_whatsapp(mensaje)

    elif decision["nivel"] == 3:
        mensaje = f"""
🔴 CRÍTICO
Paciente: {paciente.nombre}
Estado: {estado}

⚠️ Revisar urgente
"""
        enviar_whatsapp(mensaje)

    return JsonResponse({
        "ok": True,
        "paciente": paciente.nombre,
        "estado": estado,
        "decision": decision
    })


# =========================
# 🧑‍⚕️ CREAR PACIENTE
# =========================
@login_required
def crear_paciente(request):
    form = PacienteForm(request.POST or None)

    if form.is_valid():
        form.save()
        return redirect('inicio')

    return render(request, 'mi_app_salud/crear_paciente.html', {
        'form': form
    })


# =========================
# 📝 RECORDATORIOS
# =========================
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


# =========================
# ⚡ ACTUALIZAR ESTADO WEB
# =========================
@login_required
def actualizar_estado(request, paciente_id):
    paciente = get_object_or_404(Paciente, id=paciente_id)
    estado = request.GET.get('estado')

    if not estado:
        return redirect('inicio')

    estado = estado.upper().strip()

    RegistroSalud.objects.create(
        paciente=paciente,
        estado_fisico=estado,
        estado_emocional="NEUTRO"
    )

    historial = RegistroSalud.objects.filter(paciente=paciente)

    decision = evaluar_paciente(paciente, estado, historial)

    print("🧠 DECISIÓN:", decision)

    if decision["nivel"] >= 3:
        enviar_whatsapp(
            f"🚨 ALERTA UCI\nPaciente: {paciente.nombre}\nEstado: {estado}"
        )

    return redirect('inicio')

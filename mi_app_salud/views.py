<<<<<<< HEAD
# views.py

from django.shortcuts import render, get_object_or_404, redirect
from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
from datetime import datetime
=======
from django.shortcuts import render, get_object_or_404, redirect
from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
>>>>>>> ec7ba975c91bc3df226f791dbc70ec198871315b

from .models import Paciente, RegistroSalud, Recordatorio
from .forms import PacienteForm
from .clinical_engine import evaluar_paciente
from .alerts import enviar_whatsapp
from .clinical_engine import evaluar_paciente, evaluar_riesgo


<<<<<<< HEAD
# ======================================
# 🏠 INICIO
# ======================================
@login_required
def lista_pacientes(request):
    pacientes = Paciente.objects.all()
    return render(request, "mi_app_salud/inicio.html", {
        "pacientes": pacientes
=======
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
>>>>>>> ec7ba975c91bc3df226f791dbc70ec198871315b
    })


# ======================================
# 📡 API PACIENTES
# ======================================
def api_pacientes(request):
    pacientes = Paciente.objects.all()

    data = []
    for p in pacientes:
        data.append({
            "id": p.id,
            "nombre": p.nombre
        })

    return JsonResponse({"pacientes": data})

# ======================================
# ⚡ CAMBIAR ESTADO
# ======================================
from datetime import datetime

def api_cambiar_estado(request, paciente_id):
    paciente = get_object_or_404(Paciente, id=paciente_id)

    estado = request.GET.get("estado", "BIEN").upper().strip()
    ubicacion = request.GET.get("ubicacion", "No disponible")

    # SIGNOS VITALES DESDE HTML
    pulso = int(request.GET.get("pulso", 80))
    temp = float(request.GET.get("temp", 36.5))
    oxi = int(request.GET.get("oxi", 98))

    # GUARDAR REGISTRO
    RegistroSalud.objects.create(
        paciente=paciente,
        estado_fisico=estado,
        estado_emocional="NEUTRO"
    )

    historial = RegistroSalud.objects.filter(paciente=paciente)

    # IA EXISTENTE
    decision = evaluar_paciente(
        paciente,
        estado,
        historial
    )

    print("🧠 DECISIÓN:", decision)

    # IA CLÍNICA NUEVA
    riesgo = evaluar_riesgo(pulso, temp, oxi)

    print("🏥 RIESGO:", riesgo)

    # ALERTA
    if decision["nivel"] >= 3 or riesgo == "CRITICO":

        hora = datetime.now().strftime("%H:%M")

        mensaje = f"""
🚨 ALERTA MÉDICA URGENTE

👤 Paciente: {paciente.nombre}
📌 Estado: {estado}

❤️ Pulso: {pulso} BPM
🌡️ Temp: {temp} °C
🩸 Oxígeno: {oxi}%

📍 Ubicación:
{ubicacion}

🕒 Hora: {hora}

⚠️ Atención inmediata requerida.

Jarvice Health AI
"""

        enviar_whatsapp(mensaje)
        print("📲 WhatsApp principal enviado")

    return JsonResponse({
        "ok": True,
        "paciente": paciente.nombre,
        "estado": estado,
        "ubicacion": ubicacion,
        "decision": decision,
        "pulso": pulso,
        "temp": temp,
        "oxi": oxi,
        "riesgo": riesgo
    })
# ======================================
# 📲 SEGUNDO CONTACTO
# ======================================
def segundo_contacto(request):

    mensaje = """
🚨 ESCALAMIENTO NIVEL 2

El contacto principal no respondió.

Se requiere revisar al paciente.
"""

    enviar_whatsapp(mensaje)

    print("📲 Segundo contacto notificado")

    return JsonResponse({
        "ok": True,
        "mensaje": "Segundo contacto notificado"
    })


# ======================================
# 🚑 TERCER CONTACTO
# ======================================
def tercer_contacto(request):

    mensaje = """
🚨 ESCALAMIENTO NIVEL 3

Ningún contacto respondió.

Se recomienda llamar emergencias médicas ahora.
"""

    enviar_whatsapp(mensaje)

    print("🚑 Tercer contacto notificado")

    return JsonResponse({
        "ok": True,
        "mensaje": "Tercer contacto notificado"
    })
mensaje = """
🚨 ESCALAMIENTO NIVEL 3

Ningún contacto respondió.

🚑 Se recomienda llamar emergencias médicas ahora.
📍 Última ubicación disponible.
🧠 Riesgo crítico detectado.
"""


# ======================================
# ➕ CREAR PACIENTE
# ======================================
@login_required
def crear_paciente(request):
    form = PacienteForm(request.POST or None)

    if form.is_valid():
        form.save()
        return redirect("inicio")

    return render(request, "mi_app_salud/crear_paciente.html", {
        "form": form
    })


<<<<<<< HEAD
# ======================================
# 📝 RECORDATORIO
# ======================================
=======
# 📝 RECORDATORIOS
>>>>>>> ec7ba975c91bc3df226f791dbc70ec198871315b
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

<<<<<<< HEAD
    return redirect("inicio")
@login_required
def historial_paciente(request, paciente_id):
    paciente = get_object_or_404(Paciente, id=paciente_id)

    registros = RegistroSalud.objects.filter(
        paciente=paciente
    ).order_by('-fecha')

    recordatorios = Recordatorio.objects.filter(
        paciente=paciente
    ).order_by('-fecha')

    return render(request, "mi_app_salud/historial.html", {
        "paciente": paciente,
        "registros": registros,
        "recordatorios": recordatorios,
    })
=======
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
>>>>>>> ec7ba975c91bc3df226f791dbc70ec198871315b

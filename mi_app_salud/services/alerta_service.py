# ==========================================================
# JARVICE - SERVICIO DE ESCALAMIENTO DE ALERTAS
# ==========================================================

from ..alerts import enviar_whatsapp_a
from ..models import AuditoriaJarvice


# ==========================================================
# AUDITORÍA
# ==========================================================

def _registrar_auditoria(
    usuario,
    ip,
    accion,
    modulo,
    descripcion,
    datos_extra=None
):
    """
    Registra una acción de escalamiento sin depender
    directamente de un objeto request.
    """

    AuditoriaJarvice.objects.create(
        usuario=usuario,
        accion=accion,
        modulo=modulo,
        descripcion=descripcion,
        ip=ip,
        datos_extra=datos_extra
    )


# ==========================================================
# ESCALAMIENTO DE EMERGENCIA
# ==========================================================

def escalar_emergencia(
    paciente,
    signo,
    analisis,
    usuario=None,
    ip=None
):
    """
    Ejecuta el escalamiento de una alerta crítica.

    Orden:

    1. Contacto de emergencia principal
    2. Segundo contacto
    3. Tercer contacto
    4. SIN_CONTACTO si ninguno puede ser notificado

    No depende de request y puede ser utilizado desde:
    - vistas web
    - API de dispositivos
    - procesos automáticos
    - WebSockets
    """

    # ======================================================
    # DATOS COMUNES
    # ======================================================

    mensaje_base = f"""
🚨 ALERTA CRÍTICA JARVICE

Paciente:
{paciente.nombre} {paciente.apellido}

🩺 Patologías:
{paciente.enfermedades or "Sin datos"}

🧠 Antecedentes de salud mental:
{paciente.antecedentes_salud_mental or "Sin datos"}

⚠️ Alergias:
{paciente.alergias or "Sin datos"}

RIESGO:
CRÍTICO

❤️ Frecuencia cardíaca:
{
    signo.frecuencia_cardiaca
    if signo.frecuencia_cardiaca is not None
    else "Sin dato"
} lpm

🫁 Saturación:
{
    signo.saturacion_oxigeno
    if signo.saturacion_oxigeno is not None
    else "Sin dato"
} %

🌡️ Temperatura:
{
    signo.temperatura
    if signo.temperatura is not None
    else "Sin dato"
} °C

🩺 Presión arterial:
{signo.presion_arterial or "Sin dato"}

🧠 Estado emocional:
{signo.estado_emocional or "Sin dato"}

📡 Origen:
{signo.origen}

📍 Ubicación:
{
    f"{signo.latitud}, {signo.longitud}"
    if signo.latitud is not None and signo.longitud is not None
    else "Sin ubicación disponible"
}

🕒 Fecha de ubicación:
{
    signo.fecha_ubicacion.isoformat()
    if signo.fecha_ubicacion is not None
    else "Sin dato"
}

⚠️ Jarvice detectó parámetros clínicos críticos.

Se requiere atención inmediata.
"""

    # ======================================================
    # CONTACTO 1
    # ======================================================

    contacto_1 = paciente.contacto_emergencia
    telefono_1 = paciente.telefono_emergencia

    if telefono_1:

        mensaje_1 = (
            "🚨 CONTACTO DE EMERGENCIA JARVICE\n\n"
            + mensaje_base
        )

        enviado_1 = enviar_whatsapp_a(
            telefono_1,
            mensaje_1
        )

        _registrar_auditoria(
            usuario=usuario,
            ip=ip,
            accion="EMERGENCIA",
            modulo="ESCALAMIENTO",
            descripcion=(
                f"Primer contacto de emergencia "
                f"{'notificado' if enviado_1 else 'no pudo ser notificado'}."
            ),
            datos_extra={
                "nivel": 1,
                "paciente_id": paciente.id,
                "signo_id": signo.id,
                "contacto": contacto_1,
                "telefono": telefono_1,
                "enviado": enviado_1,
            }
        )

        if enviado_1:
            return {
                "nivel": 1,
                "estado": "CONTACTO_1_NOTIFICADO",
                "contacto": contacto_1,
                "telefono": telefono_1,
            }

    else:

        _registrar_auditoria(
            usuario=usuario,
            ip=ip,
            accion="EMERGENCIA",
            modulo="ESCALAMIENTO",
            descripcion=(
                "No existe teléfono configurado "
                "para el primer contacto de emergencia."
            ),
            datos_extra={
                "nivel": 1,
                "paciente_id": paciente.id,
                "signo_id": signo.id,
            }
        )

    # ======================================================
    # CONTACTO 2
    # ======================================================

    contacto_2 = paciente.contacto_emergencia_2
    telefono_2 = paciente.telefono_emergencia_2

    if telefono_2:

        mensaje_2 = (
            "🚨 SEGUNDO CONTACTO JARVICE\n\n"
            + mensaje_base
            + "\n\nEl primer contacto no pudo ser notificado."
        )

        enviado_2 = enviar_whatsapp_a(
            telefono_2,
            mensaje_2
        )

        _registrar_auditoria(
            usuario=usuario,
            ip=ip,
            accion="EMERGENCIA",
            modulo="ESCALAMIENTO",
            descripcion=(
                f"Segundo contacto "
                f"{'notificado' if enviado_2 else 'no pudo ser notificado'}."
            ),
            datos_extra={
                "nivel": 2,
                "paciente_id": paciente.id,
                "signo_id": signo.id,
                "contacto": contacto_2,
                "telefono": telefono_2,
                "enviado": enviado_2,
            }
        )

        if enviado_2:
            return {
                "nivel": 2,
                "estado": "CONTACTO_2_NOTIFICADO",
                "contacto": contacto_2,
                "telefono": telefono_2,
            }

    # ======================================================
    # CONTACTO 3
    # ======================================================

    contacto_3 = paciente.contacto_emergencia_3
    telefono_3 = paciente.telefono_emergencia_3

    if telefono_3:

        mensaje_3 = (
            "🚨 EMERGENCIA JARVICE\n\n"
            + mensaje_base
            + "\n\nNo fue posible notificar los contactos anteriores."
        )

        enviado_3 = enviar_whatsapp_a(
            telefono_3,
            mensaje_3
        )

        _registrar_auditoria(
            usuario=usuario,
            ip=ip,
            accion="EMERGENCIA",
            modulo="ESCALAMIENTO",
            descripcion=(
                f"Tercer contacto "
                f"{'notificado' if enviado_3 else 'no pudo ser notificado'}."
            ),
            datos_extra={
                "nivel": 3,
                "paciente_id": paciente.id,
                "signo_id": signo.id,
                "contacto": contacto_3,
                "telefono": telefono_3,
                "enviado": enviado_3,
            }
        )

        if enviado_3:
            return {
                "nivel": 3,
                "estado": "CONTACTO_3_NOTIFICADO",
                "contacto": contacto_3,
                "telefono": telefono_3,
            }

    # ======================================================
    # NINGÚN CONTACTO DISPONIBLE
    # ======================================================

    _registrar_auditoria(
        usuario=usuario,
        ip=ip,
        accion="EMERGENCIA",
        modulo="ESCALAMIENTO",
        descripcion=(
            "Jarvice no pudo notificar ningún contacto "
            "de emergencia configurado."
        ),
        datos_extra={
            "paciente_id": paciente.id,
            "signo_id": signo.id,
            "nivel": 0,
            "estado": "SIN_CONTACTO",
        }
    )

    return {
        "nivel": 0,
        "estado": "SIN_CONTACTO",
        "contacto": None,
        "telefono": None,
    }
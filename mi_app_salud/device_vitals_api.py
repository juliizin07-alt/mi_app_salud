import json
from decimal import Decimal, InvalidOperation
from asgiref.sync import async_to_sync
from channels.layers import get_channel_layer
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt

from .clinical_engine import analizar_signos_vitales
from .models import SignoVital
from .services.alerta_service import escalar_emergencia
from .services.dispositivo_service import (
    obtener_dispositivo,
    verificar_credencial_dispositivo,
)


@csrf_exempt
def dispositivo_signos_vitales(request):

    if request.method != "POST":
        return JsonResponse(
            {
                "ok": False,
                "error": "Metodo no permitido. Utilice POST.",
            },
            status=405,
        )

    try:
        datos = json.loads(
            request.body.decode("utf-8")
        )
    except (json.JSONDecodeError, UnicodeDecodeError):
        return JsonResponse(
            {
                "ok": False,
                "error": "JSON invalido.",
            },
            status=400,
        )

    identificador = datos.get("identificador")
    credencial = datos.get("credencial")

    if not identificador:
        return JsonResponse(
            {
                "ok": False,
                "error": "identificador es obligatorio.",
            },
            status=400,
        )

    if not credencial:
        return JsonResponse(
            {
                "ok": False,
                "error": "Credencial del dispositivo es obligatoria.",
            },
            status=401,
        )

    dispositivo = obtener_dispositivo(
        identificador
    )

    if dispositivo is None:
        return JsonResponse(
            {
                "ok": False,
                "error": "Dispositivo no encontrado o inactivo.",
            },
            status=404,
        )

    if not verificar_credencial_dispositivo(
        dispositivo,
        credencial
    ):
        return JsonResponse(
            {
                "ok": False,
                "error": "Credencial del dispositivo invalida.",
            },
            status=401,
        )

    frecuencia_cardiaca = datos.get(
        "frecuencia_cardiaca"
    )

    saturacion_oxigeno = datos.get(
        "saturacion_oxigeno"
    )

    temperatura = datos.get(
        "temperatura"
    )

    presion_arterial = datos.get(
        "presion_arterial",
        ""
    )

    estado_emocional = datos.get(
        "estado_emocional",
        ""
    )

    observaciones = datos.get(
        "observaciones",
        ""
    )

    if (
        frecuencia_cardiaca in [None, ""]
        and saturacion_oxigeno in [None, ""]
        and temperatura in [None, ""]
        and not presion_arterial
        and not estado_emocional
    ):
        return JsonResponse(
            {
                "ok": False,
                "error": "Debe enviar al menos un dato clinico.",
            },
            status=400,
        )

    if frecuencia_cardiaca not in [None, ""]:
        try:
            frecuencia_cardiaca = int(
                frecuencia_cardiaca
            )
        except (TypeError, ValueError):
            return JsonResponse(
                {
                    "ok": False,
                    "error": "frecuencia_cardiaca debe ser un entero.",
                },
                status=400,
            )

    if saturacion_oxigeno not in [None, ""]:
        try:
            saturacion_oxigeno = Decimal(
                str(saturacion_oxigeno)
            )
        except (InvalidOperation, ValueError):
            return JsonResponse(
                {
                    "ok": False,
                    "error": "saturacion_oxigeno debe ser numerica.",
                },
                status=400,
            )

    if temperatura not in [None, ""]:
        try:
            temperatura = Decimal(
                str(temperatura)
            )
            temperatura = temperatura.quantize(
                Decimal("0.1")
            )
        except (InvalidOperation, ValueError):
            return JsonResponse(
                {
                    "ok": False,
                    "error": "temperatura debe ser numerica.",
                },
                status=400,
            )

    if presion_arterial:
        partes_presion = presion_arterial.split("/")

        if (
            len(partes_presion) != 2
            or not all(
                parte.strip().isdigit()
                for parte in partes_presion
            )
        ):
            return JsonResponse(
                {
                    "ok": False,
                    "error": (
                        "presion_arterial debe utilizar "
                        "el formato sistolica/diastolica."
                    ),
                },
                status=400,
            )

    signo = SignoVital.objects.create(
        paciente=dispositivo.paciente,
        frecuencia_cardiaca=frecuencia_cardiaca,
        saturacion_oxigeno=saturacion_oxigeno,
        temperatura=temperatura,
        presion_arterial=presion_arterial,
        estado_emocional=estado_emocional,
        origen="SMARTWATCH",
        observaciones=observaciones,
    )

    analisis = analizar_signos_vitales(
        signo
    )
    channel_layer = get_channel_layer()

    if channel_layer is not None:

        async_to_sync(
            channel_layer.group_send
        )(
            "monitoreo",
            {
                "type": "enviar_monitoreo",
                "data": {
                    "tipo": (
                        "alerta_critica"
                        if analisis["riesgo_vital"] == "CRITICO"
                        else "signos_vitales"
                    ),
                    "paciente_id": dispositivo.paciente.id,
                    "paciente": (
                        f"{dispositivo.paciente.nombre} "
                        f"{dispositivo.paciente.apellido}"
                    ),
                    "dispositivo_id": dispositivo.id,
                    "frecuencia_cardiaca": (
                        signo.frecuencia_cardiaca
                    ),
                    "saturacion_oxigeno": (
                        float(signo.saturacion_oxigeno)
                        if signo.saturacion_oxigeno is not None
                        else None
                    ),
                    "temperatura": (
                        float(signo.temperatura)
                        if signo.temperatura is not None
                        else None
                    ),
                    "presion_arterial": (
                        signo.presion_arterial
                    ),
                    "estado_emocional": (
                        signo.estado_emocional
                    ),
                    "riesgo_vital": (
                        analisis["riesgo_vital"]
                    ),
                    "color_riesgo_vital": (
                        analisis["color_riesgo_vital"]
                    ),
                    "nivel_riesgo_ia": (
                        analisis["nivel_riesgo_ia"]
                    ),
                    "fecha": signo.fecha.isoformat(),
                },
            },
        )

    escalamiento = None

    if analisis["riesgo_vital"] == "CRITICO":

        escalamiento = escalar_emergencia(
            paciente=dispositivo.paciente,
            signo=signo,
            analisis=analisis,
            usuario=None,
            ip=request.META.get("REMOTE_ADDR")
        )

    return JsonResponse(

        {
            "ok": True,
            "mensaje": "Signos vitales recibidos correctamente.",
            "dispositivo": {
                "id": dispositivo.id,
                "nombre": dispositivo.nombre,
                "identificador": dispositivo.identificador,
            },
            "paciente": {
                "id": dispositivo.paciente.id,
                "nombre": dispositivo.paciente.nombre,
                "apellido": dispositivo.paciente.apellido,
            },
            "signo_id": signo.id,
            "signos_vitales": {
                "frecuencia_cardiaca":
                    signo.frecuencia_cardiaca,

                "saturacion_oxigeno": (
                    float(signo.saturacion_oxigeno)
                    if signo.saturacion_oxigeno is not None
                    else None
                ),

                "temperatura": (
                    float(signo.temperatura)
                    if signo.temperatura is not None
                    else None
                ),

                "presion_arterial":
                    signo.presion_arterial,

                "estado_emocional":
                    signo.estado_emocional,

                "origen":
                    signo.origen,

                "fecha":
                    signo.fecha.isoformat(),
            },
            "analisis": analisis,

            "escalamiento": escalamiento,
        }
    )

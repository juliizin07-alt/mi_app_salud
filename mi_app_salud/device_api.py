import json

from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.utils import timezone

from .services.dispositivo_service import (
    obtener_dispositivo,
    marcar_conectado,
)


@csrf_exempt
def dispositivo_heartbeat(request):

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
    bateria = datos.get("bateria")

    if not identificador:
        return JsonResponse(
            {
                "ok": False,
                "error": "identificador es obligatorio.",
            },
            status=400,
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

    if bateria is not None:
        try:
            bateria = int(bateria)
        except (TypeError, ValueError):
            return JsonResponse(
                {
                    "ok": False,
                    "error": "bateria debe ser un numero entero.",
                },
                status=400,
            )

        if not 0 <= bateria <= 100:
            return JsonResponse(
                {
                    "ok": False,
                    "error": "bateria debe estar entre 0 y 100.",
                },
                status=400,
            )

    dispositivo = marcar_conectado(
        dispositivo,
        bateria,
    )

    return JsonResponse(
        {
            "ok": True,
            "mensaje": "Heartbeat recibido correctamente.",
            "dispositivo": {
                "id": dispositivo.id,
                "nombre": dispositivo.nombre,
                "tipo": dispositivo.get_tipo_display(),
                "identificador": dispositivo.identificador,
                "conectado": dispositivo.conectado,
                "bateria": dispositivo.bateria,
                "ultima_conexion": (
                    dispositivo.ultima_conexion.isoformat()
                    if dispositivo.ultima_conexion
                    else None
                ),
            },
            "paciente": {
                "id": dispositivo.paciente.id,
                "nombre": dispositivo.paciente.nombre,
                "apellido": dispositivo.paciente.apellido,
            },
            "servidor": timezone.now().isoformat(),
        }
    )

from django.utils import timezone

from ..models import Dispositivo


def obtener_dispositivo(identificador):
    """
    Busca un dispositivo activo por su identificador único.
    """
    if not identificador:
        return None

    return (
        Dispositivo.objects
        .select_related("paciente")
        .filter(
            identificador=identificador,
            activo=True
        )
        .first()
    )


def marcar_conectado(dispositivo, bateria=None):
    """
    Marca un dispositivo como conectado
    y actualiza su última conexión.
    """
    dispositivo.conectado = True
    dispositivo.ultima_conexion = timezone.now()

    if bateria is not None:
        bateria = int(bateria)

        if 0 <= bateria <= 100:
            dispositivo.bateria = bateria

    dispositivo.save(
        update_fields=[
            "conectado",
            "ultima_conexion",
            "bateria",
        ]
    )

    return dispositivo


def marcar_desconectado(dispositivo):
    """
    Marca un dispositivo como desconectado.
    """
    dispositivo.conectado = False

    dispositivo.save(
        update_fields=[
            "conectado",
        ]
    )

    return dispositivo

from django.contrib.auth.hashers import check_password, make_password
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


def establecer_credencial_dispositivo(dispositivo, credencial):
    """
    Guarda únicamente el hash de la credencial del dispositivo.
    """
    if not credencial:
        raise ValueError(
            "La credencial del dispositivo es obligatoria."
        )

    dispositivo.credencial_hash = make_password(
        credencial
    )

    dispositivo.save(
        update_fields=[
            "credencial_hash",
        ]
    )

    return dispositivo


def verificar_credencial_dispositivo(dispositivo, credencial):
    """
    Verifica una credencial contra el hash almacenado.
    """
    if not dispositivo or not credencial:
        return False

    if not dispositivo.credencial_hash:
        return False

    return check_password(
        credencial,
        dispositivo.credencial_hash
    )

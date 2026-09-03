# ==========================================================
# JARVICE - SISTEMA DE ALERTAS
# ==========================================================

import time

from django.conf import settings
from twilio.rest import Client


# ==========================================================
# CONTROL ANTISPAM
# ==========================================================

ULTIMOS_ENVIADOS = {}

COOLDOWN_SEGUNDOS = 30


def puede_enviar(numero):
    """
    Evita enviar múltiples mensajes consecutivos
    al mismo número durante el período de cooldown.
    """

    ahora = time.time()

    if numero not in ULTIMOS_ENVIADOS:
        ULTIMOS_ENVIADOS[numero] = ahora
        return True

    if ahora - ULTIMOS_ENVIADOS[numero] > COOLDOWN_SEGUNDOS:
        ULTIMOS_ENVIADOS[numero] = ahora
        return True

    return False


# ==========================================================
# CONFIGURACIÓN TWILIO
# ==========================================================

ACCOUNT_SID = getattr(
    settings,
    "TWILIO_ACCOUNT_SID",
    ""
).strip()

AUTH_TOKEN = getattr(
    settings,
    "TWILIO_AUTH_TOKEN",
    ""
).strip()

FROM_NUMBER = getattr(
    settings,
    "TWILIO_FROM_NUMBER",
    ""
).strip()

TO_NUMBER = getattr(
    settings,
    "TWILIO_TO_NUMBER",
    ""
).strip()


# ==========================================================
# ENVIAR WHATSAPP
# ==========================================================

def enviar_whatsapp(mensaje):
    """
    Envía una alerta de Jarvice mediante WhatsApp utilizando
    Twilio.
    """

    if not mensaje or not mensaje.strip():
        print(" Mensaje vacío")
        return False

    if not ACCOUNT_SID:
        print(" TWILIO_ACCOUNT_SID no está configurado")
        return False

    if not AUTH_TOKEN:
        print(" TWILIO_AUTH_TOKEN no está configurado")
        return False

    if not FROM_NUMBER:
        print(" TWILIO_FROM_NUMBER no está configurado")
        return False

    if not TO_NUMBER:
        print(" TWILIO_TO_NUMBER no está configurado")
        return False

    if not puede_enviar(TO_NUMBER):
        print(
            " Esperando cooldown antes de enviar otro WhatsApp..."
        )
        return False

    try:

        print(" Enviando WhatsApp mediante Twilio...")

        client = Client(
            ACCOUNT_SID,
            AUTH_TOKEN
        )

        message = client.messages.create(
            body=mensaje,
            from_=FROM_NUMBER,
            to=TO_NUMBER
        )

        print(" WhatsApp enviado correctamente")

        print(
            "SID del mensaje:",
            message.sid
        )

        return True

    except Exception as e:

        print(" Error enviando WhatsApp:")
        print(str(e))

        return False


# ==========================================================
# ENVIAR WHATSAPP A UN NUMERO ESPECIFICO
# ==========================================================

def enviar_whatsapp_a(numero, mensaje):
    """
    Envía un WhatsApp a un número específico mediante Twilio.

    Utilizado por el sistema de escalamiento de emergencias
    de Jarvice.
    """

    if not numero:
        print(" Número de destino vacío")
        return False

    if not mensaje or not mensaje.strip():
        print(" Mensaje vacío")
        return False

    if not ACCOUNT_SID:
        print(" TWILIO_ACCOUNT_SID no está configurado")
        return False

    if not AUTH_TOKEN:
        print(" TWILIO_AUTH_TOKEN no está configurado")
        return False

    if not FROM_NUMBER:
        print(" TWILIO_FROM_NUMBER no está configurado")
        return False

    if not puede_enviar(numero):
        print(
            f" Cooldown activo para {numero}"
        )
        return False

    try:

        print(
            f" Enviando WhatsApp a {numero}..."
        )

        client = Client(
            ACCOUNT_SID,
            AUTH_TOKEN
        )

        message = client.messages.create(
            body=mensaje,
            from_=FROM_NUMBER,
            to=numero
        )

        print(
            f" WhatsApp enviado correctamente a {numero}"
        )

        print(
            "SID del mensaje:",
            message.sid
        )

        return True

    except Exception as e:

        print(" Error enviando WhatsApp:")
        print(str(e))

        return False

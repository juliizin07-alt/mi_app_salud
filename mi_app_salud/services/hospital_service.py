from ..brain import procesar_estado
from ..alerts import enviar_whatsapp


def procesar_evento(paciente, estado):
    decision = procesar_estado(paciente, estado)

    nivel = decision["nivel"]

    if nivel >= 3:
        mensaje = f"🚨 ALERTA CRÍTICA\nPaciente: {paciente.nombre}\nEstado: {estado}\nDetalle: {decision['mensaje']}"
        enviar_whatsapp(mensaje)

    return decision
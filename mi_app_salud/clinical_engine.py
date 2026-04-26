from .alerts import enviar_whatsapp

from .engine import calcular_riesgo


def evaluar_paciente(paciente, estado, historial=None):
    riesgo = calcular_riesgo(estado)

    return {
        "paciente": paciente.nombre,
        "nivel": riesgo["nivel"],
        "color": riesgo["color"],
        "mensaje": riesgo["mensaje"]
    }

def evaluar_paciente(paciente, estado, historial):
    """
    Motor clínico central (tipo hospital real)
    """

    criticos = historial.filter(estado_fisico="CRITICO").count()
    dolor = historial.filter(estado_fisico="DOLOR").count()

    # 🔴 EMERGENCIA
    if estado == "CRITICO" and criticos >= 2:
        mensaje = f"🚨 EMERGENCIA: {paciente.nombre}"
        enviar_whatsapp(mensaje)

        return {
            "nivel": 4,
            "estado": estado,
            "mensaje": "Emergencia crítica detectada"
        }

    # 🔴 CRÍTICO
    if estado == "CRITICO":
        mensaje = f"🔴 CRÍTICO: {paciente.nombre}"
        enviar_whatsapp(mensaje)

        return {
            "nivel": 3,
            "estado": estado,
            "mensaje": "Paciente crítico"
        }

    # 🟡 OBSERVACIÓN
    if estado == "DOLOR" or dolor >= 3:
        return {
            "nivel": 2,
            "estado": estado,
            "mensaje": "Paciente en observación"
        }

    # 🟢 ESTABLE
    return {
        "nivel": 1,
        "estado": estado,
        "mensaje": "Paciente estable"
    }
from .alerts import enviar_whatsapp
from .engine import calcular_riesgo


def evaluar_paciente(paciente, estado, historial):
    """
    Motor clínico principal
    """

    criticos = historial.filter(estado_fisico="CRITICO").count()
    dolor = historial.filter(estado_fisico="DOLOR").count()

    # 🚨 Emergencia grave repetida
    if estado == "CRITICO" and criticos >= 2:
        mensaje = f"🚨 EMERGENCIA: {paciente.nombre}"
        enviar_whatsapp(mensaje)

        return {
            "nivel": 4,
            "estado": estado,
            "mensaje": "Emergencia crítica detectada"
        }

    # 🔴 Crítico
    if estado == "CRITICO":
        mensaje = f"🔴 CRÍTICO: {paciente.nombre}"
        enviar_whatsapp(mensaje)

        return {
            "nivel": 3,
            "estado": estado,
            "mensaje": "Paciente crítico"
        }

    # 🟡 Observación
    if estado == "DOLOR" or dolor >= 3:
        return {
            "nivel": 2,
            "estado": estado,
            "mensaje": "Paciente en observación"
        }

    # 🟢 Estable
    return {
        "nivel": 1,
        "estado": estado,
        "mensaje": "Paciente estable"
    }


def evaluar_riesgo(pulso, temp, oxi):
    """
    IA de signos vitales
    """

    score = 0

    if pulso > 110:
        score += 2

    if temp > 38:
        score += 2

    if oxi < 94:
        score += 4

    if score >= 6:
        return "CRITICO"
    elif score >= 3:
        return "ALERTA"
    else:
        return "ESTABLE"
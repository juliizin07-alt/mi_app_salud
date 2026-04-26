def calcular_riesgo(paciente, estado_actual, historial):
    """
    Motor de triage tipo hospital.
    Devuelve nivel de riesgo clínico.
    """

    criticos = historial.filter(estado_fisico="CRITICO").count()
    dolor = historial.filter(estado_fisico="DOLOR").count()

    # 🔴 Emergencia
    if estado_actual == "CRITICO" and criticos >= 2:
        return {
            "nivel": 4,
            "etiqueta": "EMERGENCIA",
            "accion": "ALERTA_INMEDIATA"
        }

    # 🔴 Crítico
    if estado_actual == "CRITICO":
        return {
            "nivel": 3,
            "etiqueta": "CRITICO",
            "accion": "ENVIAR_ALERTA"
        }

    # 🟡 Observación
    if estado_actual == "DOLOR" or dolor >= 3:
        return {
            "nivel": 2,
            "etiqueta": "OBSERVACION",
            "accion": "MONITOREO"
        }

    # 🟢 Estable
    return {
        "nivel": 1,
        "etiqueta": "ESTABLE",
        "accion": "NORMAL"
    }
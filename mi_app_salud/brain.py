def procesar_estado(paciente, estado_fisico):
    """
    Motor de decisiones tipo Jarvis médico.
    Devuelve nivel de alerta + acción recomendada.
    """

    estado = estado_fisico.upper().strip()

    # 🟢 VERDE
    if estado == "OK":
        return {
            "nivel": 1,
            "color": "verde",
            "mensaje": f"{paciente.nombre} estable. Sin acción requerida."
        }

    # 🟡 AMARILLO
    if estado == "DOLOR":
        return {
            "nivel": 2,
            "color": "amarillo",
            "mensaje": f"{paciente.nombre} requiere atención leve."
        }

    # 🔴 ROJO (CRÍTICO)
    if estado == "CRITICO":
        return {
            "nivel": 3,
            "color": "rojo",
            "mensaje": f"{paciente.nombre} en estado crítico. ALERTA."
        }

    # fallback
    return {
        "nivel": 0,
        "color": "gris",
        "mensaje": "Estado desconocido"
    }
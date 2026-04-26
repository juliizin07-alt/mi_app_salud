def calcular_riesgo(estado):
    estado = estado.upper().strip()

    if estado == "CRITICO":
        return {"nivel": 4, "color": "rojo", "mensaje": "Riesgo vital inmediato"}

    elif estado == "DOLOR":
        return {"nivel": 3, "color": "naranja", "mensaje": "Atención urgente requerida"}

    elif estado == "ESTABLE":
        return {"nivel": 2, "color": "amarillo", "mensaje": "Observación"}

    return {"nivel": 1, "color": "verde", "mensaje": "Paciente estable"}

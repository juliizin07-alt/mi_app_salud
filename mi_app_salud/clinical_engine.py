# ==================================================
# JARVICE CLINICAL ENGINE
# ==================================================

def analizar_signos_vitales(signo):
    """
    Motor clinico central de Jarvice.

    Recibe un objeto SignoVital y analiza:
    - frecuencia cardiaca
    - saturacion de oxigeno
    - temperatura
    - presion arterial
    - estado emocional

    Devuelve un resultado estructurado para los paneles
    de Jarvice.
    """

    # ==================================================
    # ESTADOS INICIALES
    # ==================================================

    estado_frecuencia = "SIN DATOS"
    estado_saturacion = "SIN DATOS"
    estado_temperatura = "SIN DATOS"
    estado_presion = "SIN DATOS"
    estado_emocional = "SIN DATOS"

    # ==================================================
    # FRECUENCIA CARDIACA
    # ==================================================

    fc = signo.frecuencia_cardiaca

    if fc is not None:

        if 60 <= fc <= 100:
            estado_frecuencia = "NORMAL"

        elif 50 <= fc < 60 or 100 < fc <= 120:
            estado_frecuencia = "ATENCION"

        else:
            estado_frecuencia = "CRITICO"

    # ==================================================
    # SATURACION DE OXIGENO
    # ==================================================

    sat = signo.saturacion_oxigeno

    if sat is not None:

        if sat >= 95:
            estado_saturacion = "NORMAL"

        elif sat >= 90:
            estado_saturacion = "ATENCION"

        else:
            estado_saturacion = "CRITICO"

    # ==================================================
    # TEMPERATURA
    # ==================================================

    temp = signo.temperatura

    if temp is not None:

        temp = float(temp)

        if 36.0 <= temp <= 37.5:
            estado_temperatura = "NORMAL"

        elif 35.0 <= temp < 36.0 or 37.5 < temp <= 38.0:
            estado_temperatura = "ATENCION"

        else:
            estado_temperatura = "CRITICO"

        # ==================================================
    # PRESION ARTERIAL
    # ==================================================

    presion = signo.presion_arterial

    if presion:

        try:

            sistolica, diastolica = presion.split("/")

            sistolica = int(sistolica)
            diastolica = int(diastolica)

            if (
                90 <= sistolica <= 129
                and 60 <= diastolica <= 79
            ):
                estado_presion = "NORMAL"

            elif (
                sistolica < 90
                or diastolica < 60
                or 130 <= sistolica <= 139
                or 80 <= diastolica <= 89
            ):
                estado_presion = "ATENCION"

            else:
                estado_presion = "CRITICO"

        except (ValueError, AttributeError):
            estado_presion = "SIN DATOS"

    # ==================================================
    # ESTADO EMOCIONAL
    # ==================================================

    emocional = (
        signo.estado_emocional or ""
    ).upper().strip()

    if emocional in [
        "ESTABLE",
        "OK",
        "NORMAL",
        "NEUTRO"
    ]:

        estado_emocional = "ESTABLE"

    elif emocional:

        estado_emocional = "ATENCION"

    # ==================================================
    # RIESGO GENERAL
    # ==================================================

    estados = [
        estado_frecuencia,
        estado_saturacion,
        estado_temperatura,
        estado_presion,
        estado_emocional,
    ]

    if "CRITICO" in estados:

        riesgo_vital = "CRITICO"
        color_riesgo_vital = "rojo"

        estado_clinico_ia = "CRITICO"
        nivel_riesgo_ia = "CRITICO"
        color_riesgo_ia = "rojo"

        analisis_ia = (
            "Se detectan parametros clinicos "
            "que requieren atencion inmediata."
        )

    elif "ATENCION" in estados:

        riesgo_vital = "ATENCION"
        color_riesgo_vital = "amarillo"

        estado_clinico_ia = "ATENCION"
        nivel_riesgo_ia = "MODERADO"
        color_riesgo_ia = "amarillo"

        analisis_ia = (
            "Se detectan parametros que requieren "
            "seguimiento clinico."
        )

    elif any(
        estado in estados
        for estado in [
            "NORMAL",
            "ESTABLE"
        ]
    ):

        riesgo_vital = "BAJO"
        color_riesgo_vital = "verde"

        estado_clinico_ia = "ESTABLE"
        nivel_riesgo_ia = "BAJO"
        color_riesgo_ia = "verde"

        analisis_ia = (
            "No se detectan anomalias criticas "
            "en los parametros registrados."
        )

    else:

        riesgo_vital = "SIN DATOS"
        color_riesgo_vital = "gris"

        estado_clinico_ia = "SIN DATOS"
        nivel_riesgo_ia = "SIN DATOS"
        color_riesgo_ia = "gris"

        analisis_ia = (
            "No hay suficientes datos clinicos."
        )

    # ==================================================
    # RESULTADO
    # ==================================================

    return {
        "estado_frecuencia": estado_frecuencia,
        "estado_saturacion": estado_saturacion,
        "estado_temperatura": estado_temperatura,
        "estado_presion": estado_presion,
        "estado_emocional": estado_emocional,
        "riesgo_vital": riesgo_vital,
        "color_riesgo_vital": color_riesgo_vital,
        "estado_clinico_ia": estado_clinico_ia,
        "nivel_riesgo_ia": nivel_riesgo_ia,
        "color_riesgo_ia": color_riesgo_ia,
        "analisis_ia": analisis_ia,
    }


# ==================================================
# COMPATIBILIDAD CON EL MOTOR ANTERIOR
# ==================================================

def evaluar_riesgo(pulso, temp, oxi):
    """
    Funcion de compatibilidad con el motor anterior.
    """

    score = 0

    if pulso is not None and pulso > 110:
        score += 2

    if temp is not None and temp > 38:
        score += 2

    if oxi is not None and oxi < 94:
        score += 4

    if score >= 6:
        return "CRITICO"

    elif score >= 3:
        return "ALERTA"

    return "ESTABLE"
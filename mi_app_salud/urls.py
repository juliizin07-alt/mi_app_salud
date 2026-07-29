from django.urls import path
from . import views

urlpatterns = [

path(
    "",
    views.lista_pacientes,
    name="inicio"
),
    # ==================================================
    # REGISTRO Y AUTENTICACIÓN
    # ==================================================

    path(
        "registro/",
        views.registro,
        name="registro"
    ),

    path(
        "",
        views.lista_pacientes,
        name="inicio"
    ),

    path(
        "dashboard/",
        views.dashboard_redirect,
        name="dashboard"
    ),

    path(
        "logout/",
        views.salir,
        name="logout"
    ),

    # ==================================================
    # PACIENTES
    # ==================================================

    path(
        "crear-paciente/",
        views.crear_paciente,
        name="crear_paciente"
    ),

    path(
        "pacientes/",
        views.pacientes,
        name="pacientes"
    ),

    path(
        "historial/<int:paciente_id>/",
        views.historial_paciente,
        name="historial_paciente"
    ),

    # ==================================================
    # RECORDATORIOS
    # ==================================================

    path(
        "crear-recordatorio/<int:paciente_id>/",
        views.crear_recordatorio,
        name="crear_recordatorio"
    ),

    # ==================================================
    # MEDICACIÓN
    # ==================================================

    path(
        "medicacion/",
        views.medicacion,
        name="medicacion"
    ),

    path(
        "medicacion/crear/",
        views.crear_medicacion,
        name="crear_medicacion"
    ),

    path(
        "medicacion/<int:medicamento_id>/editar/",
        views.editar_medicacion,
        name="editar_medicacion"
    ),

    path(
        "medicacion/<int:medicamento_id>/tomar/",
        views.tomar_medicacion,
        name="tomar_medicacion"
    ),

    path(
        "medicacion/<int:medicamento_id>/estado/",
        views.cambiar_estado_medicacion,
        name="cambiar_estado_medicacion"
    ),

    path(
        "medicacion/<int:medicamento_id>/eliminar/",
        views.eliminar_medicacion,
        name="eliminar_medicacion"
    ),

    # ==================================================
    # PANEL JARVICE
    # ==================================================

    path(
        "seguridad/",
        views.seguridad,
        name="seguridad"
    ),

    path(
        "sueno/",
        views.sueno,
        name="sueno"
    ),

    path(
        "reportes/",
        views.reportes,
        name="reportes"
    ),

    path(
        "configuracion/",
        views.configuracion,
        name="configuracion"
    ),
    path(
    "emergencia/",
    views.emergencia,
    name="emergencia"
),
# ==================================================
# PANELES POR ROL JARVICE
# ==================================================

path(
    "panel/medico/",
    views.panel_medico,
    name="panel_medico"
),

path(
    "panel/enfermeria/",
    views.panel_enfermeria,
    name="panel_enfermeria"
),

path(
    "panel/paciente/",
    views.panel_paciente,
    name="panel_paciente"
),

path(
    "panel/emergencia/",
    views.panel_emergencia,
    name="panel_emergencia"
),
    # ==================================================
    # API
    # ==================================================

    path(
        "api/pacientes/",
        views.api_pacientes,
        name="api_pacientes"
    ),

    path(
        "api/cambiar-estado/<int:paciente_id>/",
        views.api_cambiar_estado,
        name="api_cambiar_estado"
    ),

    path(
        "api/segundo-contacto/",
        views.segundo_contacto,
        name="segundo_contacto"
    ),

    path(
        "api/tercer-contacto/",
        views.tercer_contacto,
        name="tercer_contacto"
    ),

]
path(
    "emergencia/",
    views.emergencia,
    name="emergencia"
),
# ==================================================
# PANELES PROFESIONALES
# ==================================================

path(
    "panel/medico/",
    views.panel_medico,
    name="panel_medico"
),

path(
    "panel/enfermeria/",
    views.panel_enfermeria,
    name="panel_enfermeria"
),

path(
    "panel/paciente/",
    views.panel_paciente,
    name="panel_paciente"
),

path(
    "panel/emergencia/",
    views.panel_emergencia,
    name="panel_emergencia"
),
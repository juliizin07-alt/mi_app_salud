from django.urls import path
from . import views
from .device_api import dispositivo_heartbeat
from django.contrib.auth import views as auth_views


urlpatterns = [

# ==========================================================
# 🆘 ACCESO QR — FICHA CLÍNICA DE EMERGENCIA
# ==========================================================

path(
    "emergencia/qr/<str:token>/",
    views.acceso_qr_emergencia,
    name="acceso_qr_emergencia"
),

path(
    "emergencia/qr/confirmar/<int:acceso_id>/",
    views.confirmar_acceso_qr,
    name="confirmar_acceso_qr"
),

path(
    "emergencia/qr/ficha/<int:acceso_id>/",
    views.ficha_emergencia_qr,
    name="ficha_emergencia_qr"
),

    # ==================================================
    # AUTENTICACIÓN
    # ==================================================

    path(
        "login/",
        views.login_view,
        name="login"
    ),
    # ==================================================
# ACCESO SECRETO ADMINISTRADOR
# ==================================================


    path(
    "bienvenida/",
    views.bienvenida_rol,
    name="bienvenida_rol"
    ),

    path(
        "registro/",
        views.registro,
        name="registro"
    ),

    path(
    "password-reset/",
    auth_views.PasswordResetView.as_view(
        template_name="mi_app_salud/password_reset.html",
        email_template_name="mi_app_salud/password_reset_email.txt",
        html_email_template_name="mi_app_salud/password_reset_email.html",
        subject_template_name="mi_app_salud/password_reset_subject.txt",
        success_url="/password-reset/done/"
    ),
    name="password_reset"
),

path(
    "password-reset/done/",
    auth_views.PasswordResetDoneView.as_view(
        template_name="mi_app_salud/password_reset_done.html"
    ),
    name="password_reset_done"
),

path(
    "password-reset/<uidb64>/<token>/",
    auth_views.PasswordResetConfirmView.as_view(
        template_name="mi_app_salud/password_reset_confirm.html",
        success_url="/password-reset/complete/"
    ),
    name="password_reset_confirm"
),

path(
    "password-reset/complete/",
    auth_views.PasswordResetCompleteView.as_view(
        template_name="mi_app_salud/password_reset_complete.html"
    ),
    name="password_reset_complete"
),

    path(
    "logout/",
    views.salir,
    name="logout"
),


    # ==================================================
    # DASHBOARD PRINCIPAL
    # ==================================================

    path(
        "",
        views.inicio,
        name="inicio"
    ),

    path(
        "dashboard/",
        views.dashboard_redirect,
        name="dashboard_redirect"
    ),


    # ==================================================
    # PACIENTES
    # ==================================================

    path(
        "pacientes/",
        views.pacientes,
        name="pacientes"
    ),

    path(
        "crear-paciente/",
        views.crear_paciente,
        name="crear_paciente"
    ),

    path(
        "historial/<int:paciente_id>/",
        views.historial_paciente,
        name="historial_paciente"
    ),

    path(
    "crear-evolucion/<int:paciente_id>/",
    views.crear_evolucion,
    name="crear_evolucion"
    ),

    path(
    "crear-evolucion-enfermeria/<int:paciente_id>/",
    views.crear_evolucion_enfermeria,
    name="crear_evolucion_enfermeria"
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
    # MÓDULOS JARVICE
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
        "configuracion/solicitud/",
        views.crear_solicitud_usuario,
        name="crear_solicitud_usuario"
    ),

    path(
        "emergencia/",
        views.emergencia,
        name="emergencia"
    ),


    # ==================================================
    # PANELES SEGÚN ROL
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
        "panel/familiar/",
        views.panel_familiar,
        name="panel_familiar"
    ),

    path(
        "panel/emergencia/",
        views.panel_emergencia,
        name="panel_emergencia"
    ),

    path(
    "panel/institucion/",
    views.panel_institucion,
    name="panel_institucion",
),


path(
    "cargar-resultado/<int:solicitud_id>/",
    views.cargar_resultado_estudio,
    name="cargar_resultado_estudio"
),

    # ==================================================
    # API JARVICE
    # ==================================================

    path(
        "api/dispositivo/heartbeat/",
        dispositivo_heartbeat,
        name="dispositivo_heartbeat"
    ),

    path(
        "api/pacientes/",
        views.api_pacientes,
        name="api_pacientes"
    ),

    path(
    "api/signos-vitales/",
    views.api_signos_vitales,
    name="api_signos_vitales"
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
    path(
    "crear-estudio/<int:paciente_id>/",
    views.crear_estudio,
    name="crear_estudio"
),

    # ==========================================================
# 🔐 ADMINISTRACIÓN SECRETA JARVICE
# ==========================================================

path(
    "jarvice-core-access/",
    views.acceso_admin_jarvice,
    name="acceso_admin_jarvice"
),

path(
    "jarvice-core-admin/",
    views.admin_jarvice,
    name="admin_jarvice"
),

path(
    "jarvice-core/",
    views.jarvice_core,
    name="jarvice_core"
),

path(
    "jarvice-core-usuarios/",
    views.admin_usuarios,
    name="admin_usuarios"
),

path(
    "jarvice-core-usuarios/<int:usuario_id>/",
    views.ver_usuario,
    name="ver_usuario"
),

path(
    "jarvice-core-usuarios/<int:usuario_id>/rol/",
    views.cambiar_rol_usuario,
    name="cambiar_rol_usuario"
),
path(
    "jarvice-core-usuarios/<int:usuario_id>/estado/",
    views.cambiar_estado_usuario,
    name="cambiar_estado_usuario"
),
path(
    "jarvice-core-seguridad/",
    views.admin_seguridad,
    name="admin_seguridad"
),
path(
    "jarvice-core-atencion/",
    views.centro_atencion_admin,
    name="centro_atencion_admin"
),

]

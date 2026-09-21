from .models import RegistroSalud, SolicitudEstudio


def notificaciones_jarvice(request):
    """
    Datos globales para la barra superior de Jarvice.
    """

    if not request.user.is_authenticated:
        return {
            "total_notificaciones_jarvice": 0,
            "total_alertas_criticas": 0,
            "total_estudios_pendientes": 0,
            "alerta_principal_jarvice": None,
        }

    try:
        perfil = request.user.perfilusuario
        rol = perfil.rol
    except Exception:
        rol = None

    total_alertas_criticas = 0
    total_estudios_pendientes = 0
    alerta_principal_jarvice = None

    if rol in ["ADMIN", "MEDICO", "ENFERMERIA"]:

        alertas_criticas = (
            RegistroSalud.objects
            .filter(estado="CRITICO")
            .select_related("paciente")
            .order_by("-fecha")
        )

        total_alertas_criticas = alertas_criticas.count()

        alerta_principal_jarvice = alertas_criticas.first()

    if rol in ["ADMIN", "ENFERMERIA"]:

        total_estudios_pendientes = (
            SolicitudEstudio.objects
            .filter(estado="PENDIENTE")
            .count()
        )

    total = (
        total_alertas_criticas
        + total_estudios_pendientes
    )

    return {
        "total_notificaciones_jarvice": total,
        "total_alertas_criticas": total_alertas_criticas,
        "total_estudios_pendientes": total_estudios_pendientes,
        "alerta_principal_jarvice": alerta_principal_jarvice,
    }
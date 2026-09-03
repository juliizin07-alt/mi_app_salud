from functools import wraps

from django.contrib import messages
from django.shortcuts import redirect


# =========================================================
# ROLES JARVICE
# =========================================================

ADMIN = "ADMIN"
MEDICO = "MEDICO"
ENFERMERIA = "ENFERMERIA"
PACIENTE = "PACIENTE"
FAMILIAR = "FAMILIAR"
EMERGENCIA = "EMERGENCIA"
INSTITUCION = "INSTITUCION"


# =========================================================
# OBTENER ROL DEL USUARIO
# =========================================================

def obtener_rol(usuario):

    if not usuario.is_authenticated:
        return None

    # Un superusuario siempre tiene acceso de administrador
    if usuario.is_superuser:
        return ADMIN

    try:
        return usuario.perfilusuario.rol
    except Exception:
        return None


# =========================================================
# COMPROBAR ROL
# =========================================================

def tiene_rol(usuario, roles_permitidos):

    rol = obtener_rol(usuario)

    return rol in roles_permitidos


# =========================================================
# DECORADOR DE ROLES
# =========================================================

def requiere_rol(*roles_permitidos):

    def decorador(view_func):

        @wraps(view_func)
        def wrapper(request, *args, **kwargs):

            # Usuario no autenticado
            if not request.user.is_authenticated:
                return redirect("login")

            # Usuario autenticado pero sin permiso
            if not tiene_rol(
                request.user,
                roles_permitidos
            ):

                messages.error(
                    request,
                    "No tenés permisos para acceder a este módulo."
                )

                return redirect("inicio")

            return view_func(
                request,
                *args,
                **kwargs
            )

        return wrapper

    return decorador
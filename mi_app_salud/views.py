# ==================================================
# IMPORTACIONES
# ==================================================

from django.shortcuts import render, redirect, get_object_or_404
from django.http import JsonResponse
from django.contrib import messages
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from django.contrib.auth import logout, authenticate, login
from django.utils import timezone
from django.utils.http import url_has_allowed_host_and_scheme
from django.db.models import Q, OuterRef, Subquery
from django.conf import settings
import secrets
from .permissions import requiere_rol
from .clinical_engine import analizar_signos_vitales
from .forms import PacienteForm, SolicitudUsuarioForm
from .alerts import (
    enviar_whatsapp,
    enviar_whatsapp_a
)


from .models import (
    PerfilUsuario,
    Paciente,
    RegistroSalud,
    Recordatorio,
    Medicacion,
    EvolucionMedica,
    EvolucionEnfermeria,
    EstudioMedico,
    SolicitudEstudio,
    AuditoriaJarvice,
    SignoVital,
    QRToken,
    AccesoClinico,
    Dispositivo,
    SolicitudUsuario,
)



# ==================================================
# SEGURIDAD DE ROLES JARVICE CORE
# ==================================================

from functools import wraps

# ==================================================
# AUDITORÍA CENTRAL JARVICE CORE
# ==================================================

def registrar_auditoria(
    request,
    accion,
    modulo,
    descripcion,
    datos_extra=None
):

    # --------------------------------------------------
    # OBTENER IP
    # --------------------------------------------------

    ip = request.META.get(
        "HTTP_X_FORWARDED_FOR"
    )

    if ip:
        ip = ip.split(",")[0].strip()
    else:
        ip = request.META.get(
            "REMOTE_ADDR"
        )

    # --------------------------------------------------
    # REGISTRAR EVENTO
    # --------------------------------------------------

    AuditoriaJarvice.objects.create(
        usuario=(
            request.user
            if request.user.is_authenticated
            else None
        ),
        accion=accion,
        modulo=modulo,
        descripcion=descripcion,
        ip=ip,
        datos_extra=datos_extra
    )



# ==================================================
# REGISTRO USUARIOS
# ==================================================
def registro(request):

    if request.method == "POST":

        username = request.POST.get("username")
        email = request.POST.get("email")
        password = request.POST.get("password")
        rol = request.POST.get("rol")

        # ==================================================
        # ROLES PERMITIDOS EN EL REGISTRO PÚBLICO
        # ==================================================

        roles_registro_permitidos = [
            "PACIENTE",
            "FAMILIAR",
            "MEDICO",
            "ENFERMERIA",
        ]

        if rol not in roles_registro_permitidos:

            messages.error(
                request,
                "El rol seleccionado no está permitido para el registro."
            )

            return redirect("registro")

        # ==================================================
        # COMPROBAR USUARIO EXISTENTE
        # ==================================================

        if User.objects.filter(username=username).exists():

            messages.error(
                request,
                "El usuario ya existe"
            )

            return redirect("registro")

        # ==================================================
        # CREAR USUARIO
        # ==================================================

        usuario = User.objects.create_user(
            username=username,
            email=email,
            password=password
        )

        # ==================================================
        # CREAR PERFIL JARVICE
        # ==================================================

        PerfilUsuario.objects.create(
            usuario=usuario,
            rol=rol
        )

        messages.success(
            request,
            "Usuario creado correctamente"
        )

        return redirect("login")

    return render(
        request,
        "mi_app_salud/registro.html"
    )


# ==================================================
# LOGIN USUARIO JARVICE
# ==================================================

def login_view(request):

    if request.method == "POST":

        username = request.POST.get("username", "").strip()
        password = request.POST.get("password", "")
        rol_seleccionado = request.POST.get("rol", "").strip().upper()

        # --------------------------------------------------
        # RECUPERAR DESTINO ORIGINAL
        # --------------------------------------------------

        next_url = (
            request.POST.get("next")
            or request.GET.get("next")
        )

        # --------------------------------------------------
        # VALIDAR ROL
        # --------------------------------------------------

        if not rol_seleccionado:

            messages.error(
                request,
                "Seleccione un tipo de acceso."
            )

            return redirect("login")

        # --------------------------------------------------
        # AUTENTICAR
        # --------------------------------------------------

        usuario = authenticate(
            request,
            username=username,
            password=password
        )

        if usuario is None:

            messages.error(
                request,
                "Usuario o contraseña incorrectos."
            )

            return redirect("login")

        # --------------------------------------------------
        # PERFIL JARVICE
        # --------------------------------------------------

        perfil = PerfilUsuario.objects.filter(
            usuario=usuario
        ).first()

        if perfil is None:

            messages.error(
                request,
                "El usuario no posee un perfil Jarvice configurado."
            )

            return redirect("login")

        # --------------------------------------------------
        # VALIDAR ROL
        # --------------------------------------------------

        if perfil.rol != rol_seleccionado:

            messages.error(
                request,
                "El tipo de acceso seleccionado no corresponde "
                "al rol de este usuario."
            )

            return redirect("login")

        # --------------------------------------------------
        # PROTEGER ADMIN
        # --------------------------------------------------

        if perfil.rol == "ADMIN":

            messages.error(
                request,
                "El acceso administrativo debe realizarse "
                "desde Jarvice Core."
            )

            return redirect("login")

        # --------------------------------------------------
        # USUARIO ACTIVO
        # --------------------------------------------------

        if not usuario.is_active:

            messages.error(
                request,
                "Este usuario se encuentra desactivado."
            )

            return redirect("login")

        # --------------------------------------------------
        # INICIAR SESIÓN
        # --------------------------------------------------

        login(
            request,
            usuario
        )

        # --------------------------------------------------
        # AUDITORÍA
        # --------------------------------------------------

        registrar_auditoria(
            request=request,
            accion="LOGIN",
            modulo="AUTENTICACION",
            descripcion=(
                f"Inicio de sesión del usuario "
                f"{usuario.username} "
                f"con rol {perfil.rol}"
            ),
            datos_extra={
                "rol": perfil.rol,
            }
        )

        # --------------------------------------------------
        # VOLVER AL DESTINO ORIGINAL
        # --------------------------------------------------

        if next_url:

            from django.utils.http import url_has_allowed_host_and_scheme

            if url_has_allowed_host_and_scheme(
                next_url,
                allowed_hosts={request.get_host()},
                require_https=request.is_secure(),
            ):

                return redirect(next_url)

        # --------------------------------------------------
        # DESTINO NORMAL
        # --------------------------------------------------

        return redirect(
            "bienvenida_rol"
        )

    # ==================================================
    # MOSTRAR LOGIN
    # ==================================================

    return render(
        request,
        "mi_app_salud/login.html"
    )

# ==================================================
# BIENVENIDA SEGÚN ROL JARVICE
# ==================================================

@login_required
def bienvenida_rol(request):

    perfil = request.user.perfilusuario

    return render(
        request,
        "mi_app_salud/bienvenida_rol.html",
        {
            "perfil": perfil
        }
    )

# ==================================================
# DASHBOARD PRINCIPAL JARVICE
# ==================================================

def inicio(request):

    perfil = get_object_or_404(
        PerfilUsuario,
        usuario=request.user
    )

    pacientes = Paciente.objects.all()

    paciente = None
    ultimo_signo_vital = None

    # ==========================================
    # PACIENTE ACTIVO
    # ==========================================

    try:

        paciente = request.user.paciente

        ultimo_signo_vital = (
            SignoVital.objects
            .filter(paciente=paciente)
            .order_by("-fecha")
            .first()
        )

    except Paciente.DoesNotExist:

        # El usuario no es un paciente.
        # No mostramos signos de otro paciente.

        paciente = None
        ultimo_signo_vital = None

    return render(
        request,
        "mi_app_salud/inicio.html",
        {
            "pacientes": pacientes,
            "paciente": paciente,
            "rol": perfil.rol,
            "ultimo_signo_vital": ultimo_signo_vital,
        }
    )


    # ==========================================
    # PACIENTE ACTIVO
    # ==========================================

    try:

        paciente = request.user.paciente

        ultimo_signo_vital = (
            SignoVital.objects
            .filter(paciente=paciente)
            .order_by("-fecha")
            .first()
        )

    except Paciente.DoesNotExist:

        # El usuario no es un paciente.
        # No mostramos signos de otro paciente.

        ultimo_signo_vital = None

    return render(
        request,
        "mi_app_salud/inicio.html",
        {
            "pacientes": pacientes,
            "rol": perfil.rol,
            "ultimo_signo_vital": ultimo_signo_vital,
        }
    )


@login_required
def dashboard_redirect(request):

    print("USUARIO:", request.user)

    perfil = get_object_or_404(
        PerfilUsuario,
        usuario=request.user
    )

    print("ROL:", perfil.rol)

    if perfil.rol == "ADMIN":
        return redirect("admin_jarvice")

    if perfil.rol == "MEDICO":
        return redirect("panel_medico")

    if perfil.rol == "ENFERMERIA":
        return redirect("panel_enfermeria")

    if perfil.rol == "PACIENTE":
        return redirect("panel_paciente")

    if perfil.rol == "FAMILIAR":
        return redirect("panel_familiar")

    if perfil.rol == "EMERGENCIA":
        return redirect("panel_emergencia")

    if perfil.rol == "INSTITUCION":
        return redirect("panel_institucion")

    return redirect("inicio")

def acceso_admin_jarvice(request):

    mensaje_error = None

    if request.method == "POST":

        codigo = request.POST.get("codigo", "").strip()
        username = request.POST.get("username", "").strip()
        password = request.POST.get("password", "")

        # --------------------------------------------------
        # 1. VALIDAR CODIGO SECRETO
        # --------------------------------------------------

        codigo_correcto = secrets.compare_digest(
            codigo,
            settings.JARVICE_ADMIN_CODE
        )

        if not codigo_correcto:

            mensaje_error = "Código administrativo incorrecto."

        else:

            # --------------------------------------------------
            # 2. AUTENTICAR USUARIO
            # --------------------------------------------------

            usuario = authenticate(
                request,
                username=username,
                password=password
            )

            if usuario is None:

                mensaje_error = (
                    "Credenciales administrativas incorrectas."
                )

            elif not usuario.is_superuser:

                mensaje_error = (
                    "Este usuario no posee privilegios "
                    "de administrador Jarvice."
                )

            else:

                perfil = PerfilUsuario.objects.filter(
                    usuario=usuario
                ).first()

                if perfil is None:

                    mensaje_error = (
                        "El usuario no posee un perfil "
                        "Jarvice configurado."
                    )

                elif perfil.rol != "ADMIN":

                    mensaje_error = (
                        "Este usuario no posee el rol "
                        "de administrador Jarvice."
                    )

                else:

                    # ==================================================
                    # AUTORIZAR SESIÓN JARVICE CORE
                    # ==================================================

                    login(request, usuario)

                    request.session["jarvice_core_autorizado"] = True
                    request.session["jarvice_core_usuario"] = usuario.username
                    request.session.modified = True

                    # ==================================================
                    # AUDITORÍA
                    # ==================================================

                    registrar_auditoria(
                        request=request,
                        accion="LOGIN",
                        modulo="JARVICE_CORE",
                        descripcion=(
                            f"Acceso al panel maestro JARVICE CORE "
                            f"del administrador {usuario.username}"
                        ),
                        datos_extra={
                            "rol": perfil.rol,
                        }
                    )

                    return redirect("admin_jarvice")

    # ==================================================
    # MOSTRAR PANTALLA DE ACCESO
    # ==================================================

    return render(
        request,
        "mi_app_salud/acceso_admin_jarvice.html",
        {
            "mensaje_error": mensaje_error
        }
    )

# ==================================================
# PANEL MAESTRO ADMINISTRADOR JARVICE CORE
# ==================================================

@requiere_rol("ADMIN")
def admin_jarvice(request):

    # ==================================================
    # SEGURIDAD JARVICE CORE
    # ==================================================

    if not request.user.is_superuser:

        messages.error(
            request,
            "Acceso restringido al administrador Jarvice."
        )

        return redirect("inicio")

    # ==================================================
    # SESIÓN CORE
    # ==================================================

    if not request.session.get(
        "jarvice_core_autorizado",
        False
    ):

        messages.error(
            request,
            "Debés realizar el acceso seguro al JARVICE CORE."
        )

        return redirect(
            "acceso_admin_jarvice"
        )

    # ==================================================
    # USUARIOS
    # ==================================================

    usuarios = User.objects.select_related(
        "perfilusuario"
    ).all()

    total_usuarios = usuarios.count()

    total_activos = usuarios.filter(
        is_active=True
    ).count()

    total_inactivos = usuarios.filter(
        is_active=False
    ).count()

    total_superusuarios = usuarios.filter(
        is_superuser=True
    ).count()

    # ==================================================
    # PACIENTES
    # ==================================================

    total_pacientes = Paciente.objects.count()

    # ==================================================
    # Alertas críticas
    # ==================================================

    total_alertas_criticas = RegistroSalud.objects.filter(
        estado="CRITICO"
    ).count()

    alertas_criticas = (
        RegistroSalud.objects
        .filter(estado="CRITICO")
        .select_related("paciente")
        .order_by("-fecha")[:10]
    )

    # ==================================================
    # MEDICACIONES
    # ==================================================

    total_medicaciones = Medicacion.objects.filter(
        activo=True
    ).count()

    total_medicaciones_pendientes = Medicacion.objects.filter(
        activo=True,
        tomado=False
    ).count()

    # ==================================================
    # RECORDATORIOS
    # ==================================================

    total_recordatorios_pendientes = Recordatorio.objects.filter(
        hecho=False
    ).count()

    # ==================================================
    # ESTUDIOS
    # ==================================================

    total_estudios_pendientes = SolicitudEstudio.objects.filter(
        estado="PENDIENTE"
    ).count()

    # ==================================================
    # CENTRO DE ATENCIÓN JARVICE
    # ==================================================

    total_solicitudes_pendientes = SolicitudUsuario.objects.filter(
        estado="PENDIENTE"
    ).count()

    solicitudes_pendientes = (
        SolicitudUsuario.objects
        .filter(estado="PENDIENTE")
        .select_related("usuario")
        .order_by("-fecha_creacion")[:10]
    )

    ultimas_solicitudes = (
        SolicitudUsuario.objects
        .select_related("usuario")
        .order_by("-fecha_creacion")[:10]
    )


    # ==================================================
    # AUDITORÍA
    # ==================================================

    total_auditorias = AuditoriaJarvice.objects.count()

    ultimas_auditorias = (
        AuditoriaJarvice.objects
        .select_related("usuario")
        .order_by("-fecha")[:10]
    )

    # ==================================================
    # DISTRIBUCIÓN DE ROLES
    # ==================================================

    total_admin = PerfilUsuario.objects.filter(
        rol="ADMIN"
    ).count()

    total_medicos = PerfilUsuario.objects.filter(
        rol="MEDICO"
    ).count()

    total_enfermeria = PerfilUsuario.objects.filter(
        rol="ENFERMERIA"
    ).count()

    total_pacientes_usuarios = PerfilUsuario.objects.filter(
        rol="PACIENTE"
    ).count()

    total_familiares = PerfilUsuario.objects.filter(
        rol="FAMILIAR"
    ).count()

    total_emergencias = PerfilUsuario.objects.filter(
        rol="EMERGENCIA"
    ).count()

    total_instituciones = PerfilUsuario.objects.filter(
        rol="INSTITUCION"
    ).count()

       # ==================================================
    # ESTADO DEL SISTEMA
    # ==================================================

    sistema_online = True
    base_datos = True

    # ==================================================
    # INTELIGENCIA ARTIFICIAL
    # ==================================================

    ia_activa = False

    # ==================================================
    # DISPOSITIVOS JARVICE
    # ==================================================

    dispositivos = Dispositivo.objects.filter(
        activo=True
    ).count()

        # ==================================================
    # SIGNOS VITALES JARVICE
    # ==================================================

    ultimo_signo_vital = (
        SignoVital.objects
        .filter(
            paciente__enfermera_asignada__usuario=request.user
        )
        .select_related("paciente")
        .order_by("-fecha")
        .first()
    )

    # ==================================================
    # ANÁLISIS CLÍNICO JARVICE
    # ==================================================

    if ultimo_signo_vital:

        analisis_clinico = analizar_signos_vitales(
            ultimo_signo_vital
        )

    else:

        analisis_clinico = {
            "estado_frecuencia": "SIN DATOS",
            "estado_saturacion": "SIN DATOS",
            "estado_temperatura": "SIN DATOS",
            "estado_presion": "SIN DATOS",
            "estado_emocional": "SIN DATOS",
            "riesgo_vital": "SIN DATOS",
            "color_riesgo_vital": "gris",
            "estado_clinico_ia": "SIN DATOS",
            "nivel_riesgo_ia": "SIN DATOS",
            "color_riesgo_ia": "gris",
        }

    lista_dispositivos = (
        Dispositivo.objects
        .filter(activo=True)
        .select_related("paciente")
        .order_by("-fecha_alta")
    )

    # ==================================================
    # CONTEXTO JARVICE CORE
    # ==================================================

    contexto = {

        "usuario": request.user,

        "sistema_online": sistema_online,
        "base_datos": base_datos,
        "ia_activa": ia_activa,
        "dispositivos": dispositivos,
        "lista_dispositivos": lista_dispositivos,
         "ultimo_signo_vital": ultimo_signo_vital,
        "analisis_clinico": analisis_clinico,

        "total_usuarios": total_usuarios,
        "total_activos": total_activos,
        "total_inactivos": total_inactivos,
        "total_superusuarios": total_superusuarios,

        "total_pacientes": total_pacientes,

        "total_alertas_criticas": total_alertas_criticas,
        "alertas_criticas": alertas_criticas,

        "total_medicaciones": total_medicaciones,
        "total_medicaciones_pendientes": total_medicaciones_pendientes,

        "total_recordatorios_pendientes": total_recordatorios_pendientes,

        "total_estudios_pendientes": total_estudios_pendientes,
        "total_solicitudes_pendientes": total_solicitudes_pendientes,
        "solicitudes_pendientes": solicitudes_pendientes,
        "ultimas_solicitudes": ultimas_solicitudes,

        "total_auditorias": total_auditorias,
        "ultimas_auditorias": ultimas_auditorias,

        "total_admin": total_admin,
        "total_medicos": total_medicos,
        "total_enfermeria": total_enfermeria,
        "total_pacientes_usuarios": total_pacientes_usuarios,
        "total_familiares": total_familiares,
        "total_emergencias": total_emergencias,
        "total_instituciones": total_instituciones,
    }

    # ==================================================
    # RENDER
    # ==================================================

    return render(
        request,
        "mi_app_salud/jarvice_core.html",
        contexto
    )

@requiere_rol("ADMIN")
def jarvice_core(request):

    # ==========================================
    # SEGURIDAD JARVICE CORE
    # ==========================================

    if not request.user.is_authenticated:
        return redirect("login")

    if not request.user.is_superuser:
        return redirect("inicio")

    # ==========================================
    # DATOS DEL SISTEMA
    # ==========================================

    total_usuarios = User.objects.count()

    total_pacientes = Paciente.objects.count()

    total_superusuarios = User.objects.filter(
        is_superuser=True
    ).count()

    total_activos = User.objects.filter(
        is_active=True
    ).count()

    contexto = {
        "total_usuarios": total_usuarios,
        "total_pacientes": total_pacientes,
        "total_superusuarios": total_superusuarios,
        "total_activos": total_activos,
    }

    return render(
        request,
        "mi_app_salud/jarvice_core.html",
        contexto
    )


@requiere_rol("MEDICO")
def panel_medico(request):

    buscar = request.GET.get("buscar", "").strip()

    # ==================================================
    # PACIENTES
    # ==================================================

    pacientes = Paciente.objects.all().order_by(
        "apellido",
        "nombre"
    )

    # ==================================================
    # BUSCADOR
    # ==================================================

    if buscar:

        palabras = buscar.split()

        for palabra in palabras:

            pacientes = pacientes.filter(
                Q(nombre__icontains=palabra)
                | Q(apellido__icontains=palabra)
                | Q(historia_clinica__icontains=palabra)
                | Q(dni__icontains=palabra)
            )

    # ==================================================
    # DATOS CLÍNICOS DE CADA PACIENTE
    # ==================================================

    for paciente in pacientes:

        # ----------------------------------------------
        # ÚLTIMO ESTADO CLÍNICO
        # ----------------------------------------------

        paciente.ultimo_estado = (
            RegistroSalud.objects
            .filter(
                paciente=paciente
            )
            .order_by("-fecha")
            .first()
        )

        # ----------------------------------------------
        # ÚLTIMOS SIGNOS VITALES
        # ----------------------------------------------

        paciente.ultimo_signo_vital = (
            SignoVital.objects
            .filter(
                paciente=paciente
            )
            .order_by("-fecha")
            .first()
        )

    # ==================================================
    # ALERTAS JARVICE IA
    # ==================================================

    alertas_ia = []

    for paciente in pacientes:

        registro = paciente.ultimo_estado

        if registro and registro.estado in [
            "DOLOR",
            "CRITICO"
        ]:

            alertas_ia.append({
                "paciente": paciente,
                "registro": registro,
            })

    total_alertas_ia = len(alertas_ia)

    # ==================================================
    # MEDICACIONES ACTIVAS
    # ==================================================

    medicamentos = Medicacion.objects.filter(
        activo=True
    )

    # ==================================================
    # ALERTAS CRÍTICAS
    # ==================================================

    alertas_criticas = (
        RegistroSalud.objects
        .filter(
            estado="CRITICO"
        )
        .select_related(
            "paciente"
        )
        .order_by(
            "-fecha"
        )
    )

    # ==================================================
    # CONTADORES
    # ==================================================

    evoluciones_recientes = (
        EvolucionEnfermeria.objects
        .select_related("paciente", "usuario")
        .order_by("-fecha")[:10]
    )
    total_pacientes = pacientes.count()

    total_medicamentos = medicamentos.count()

    total_alertas = alertas_criticas.count()

    # ==================================================
    # ÚLTIMO SIGNO VITAL GENERAL
    # ==================================================

    ultimo_signo_vital = (
        SignoVital.objects
        .select_related("paciente")
        .order_by("-fecha")
        .first()
    )

    # ==================================================
    # JARVICE CLINICAL ENGINE
    # ==================================================

    if ultimo_signo_vital:

        analisis_clinico = analizar_signos_vitales(
            ultimo_signo_vital
        )

    else:

        analisis_clinico = {
            "estado_frecuencia": "SIN DATOS",
            "estado_saturacion": "SIN DATOS",
            "estado_temperatura": "SIN DATOS",
            "estado_presion": "SIN DATOS",
            "estado_emocional": "SIN DATOS",

            "riesgo_vital": "SIN DATOS",
            "color_riesgo_vital": "gris",

            "estado_clinico_ia": "SIN DATOS",
            "nivel_riesgo_ia": "SIN DATOS",
            "color_riesgo_ia": "gris",

            "analisis_ia": (
                "Esperando registros de signos vitales."
            ),
        }


    # ==================================================
    # ALERTAS CRÍTICAS
    # ==================================================

    alertas = (
        RegistroSalud.objects
        .filter(
            estado="CRITICO"
        )
        .select_related(
            "paciente"
        )
        .order_by(
            "-fecha"
        )[:10]
    )

    # ==================================================
    # MEDICACIONES PENDIENTES
    # ==================================================

    medicaciones_pendientes = (
        Medicacion.objects
        .filter(
            activo=True,
            tomado=False
        )
        .select_related(
            "paciente"
        )
        .order_by(
            "horario"
        )[:10]
    )

    # ==================================================
    # RECORDATORIOS PENDIENTES
    # ==================================================

    recordatorios_pendientes = (
        Recordatorio.objects
        .filter(
            hecho=False
        )
        .select_related(
            "paciente"
        )
        .order_by(
            "-fecha"
        )[:10]
    )

    # ==================================================
    # ESTUDIOS PENDIENTES
    # ==================================================

    estudios_pendientes = (
        SolicitudEstudio.objects
        .filter(
            estado="PENDIENTE"
        )
        .select_related(
            "paciente",
            "medico"
        )
        .order_by(
            "-fecha_solicitud"
        )[:10]
    )

    # ==================================================
    # CONTEXTO DEL PANEL
    # ==================================================

    contexto = {

        # --------------------------------------------------
        # PACIENTES
        # --------------------------------------------------

        "pacientes": pacientes,

        "total_pacientes":
            pacientes.count(),

        # --------------------------------------------------
        # ALERTAS
        # --------------------------------------------------

        "alertas": alertas,

        "total_alertas":
            alertas.count(),

        # --------------------------------------------------
        # ACTIVIDAD RECIENTE DE ENFERMERÍA
        # --------------------------------------------------

        "evoluciones_recientes":
            evoluciones_recientes,

        # --------------------------------------------------
        # MEDICACIÓN
        # --------------------------------------------------

        "medicaciones_pendientes":
            medicaciones_pendientes,

        "total_medicaciones":
            medicaciones_pendientes.count(),

        # --------------------------------------------------
        # RECORDATORIOS
        # --------------------------------------------------

        "recordatorios_pendientes":
            recordatorios_pendientes,

        "total_recordatorios":
            recordatorios_pendientes.count(),

        # --------------------------------------------------
        # ESTUDIOS
        # --------------------------------------------------

        "estudios_pendientes":
            estudios_pendientes,

        "total_estudios":
            estudios_pendientes.count(),

        # ==================================================
        # JARVICE CLINICAL AI
        # ==================================================

        "ultimo_signo_vital":
            ultimo_signo_vital,

        "analisis_clinico":
            analisis_clinico,

        "estado_frecuencia":
            analisis_clinico["estado_frecuencia"],

        "estado_saturacion":
            analisis_clinico["estado_saturacion"],

        "estado_temperatura":
            analisis_clinico["estado_temperatura"],

        "estado_presion":
            analisis_clinico["estado_presion"],

        "estado_emocional":
            analisis_clinico["estado_emocional"],

        "riesgo_vital":
            analisis_clinico["riesgo_vital"],

        "color_riesgo_vital":
            analisis_clinico["color_riesgo_vital"],

        "estado_clinico_ia":
            analisis_clinico["estado_clinico_ia"],

        "nivel_riesgo_ia":
            analisis_clinico["nivel_riesgo_ia"],

        "color_riesgo_ia":
            analisis_clinico["color_riesgo_ia"],

        "analisis_ia":
            analisis_clinico["analisis_ia"],
    }

    # ==================================================
    # RENDER
    # ==================================================

    return render(
    request,
    "mi_app_salud/panel_medico.html",
    contexto
)
    # ============================================================
# PANEL DE ENFERMERÍA
# ============================================================

@requiere_rol("ENFERMERIA")
def panel_enfermeria(request):

    # ========================================================
    # PACIENTES
    # ========================================================

    pacientes = (
        Paciente.objects
        .all()
        .order_by("apellido", "nombre")
    )

    mis_pacientes = (
        Paciente.objects
        .filter(enfermera_asignada__usuario=request.user)
        .order_by("apellido", "nombre")
    )
    # ========================================================
    # ÚLTIMO SIGNO VITAL
    # ========================================================

    ultimo_signo_vital = (
        SignoVital.objects
        .select_related("paciente")
        .order_by("-fecha")
        .first()
    )

    # ========================================================
    # ANÁLISIS CLÍNICO JARVICE
    # ========================================================

    if ultimo_signo_vital:

        analisis_clinico = analizar_signos_vitales(
            ultimo_signo_vital
        )

    else:

        analisis_clinico = {
            "estado_frecuencia": "SIN DATOS",
            "estado_saturacion": "SIN DATOS",
            "estado_temperatura": "SIN DATOS",
            "estado_presion": "SIN DATOS",
            "estado_emocional": "SIN DATOS",

            "riesgo_vital": "SIN DATOS",
            "color_riesgo_vital": "gris",

            "estado_clinico_ia": "SIN DATOS",
            "nivel_riesgo_ia": "SIN DATOS",
            "color_riesgo_ia": "gris",

            "analisis_ia": (
                "Esperando registros de signos vitales."
            ),
        }

    # ========================================================
    # ALERTAS CRÍTICAS
    # ========================================================

    alertas = (
        RegistroSalud.objects
        .filter(
            estado="CRITICO",
            paciente__enfermera_asignada__usuario=request.user
        )
        .select_related(
            "paciente"
        )
        .order_by(
            "-fecha"
        )[:10]
    )

    # ========================================================
    # MEDICACIONES PENDIENTES
    # ========================================================

    medicaciones_pendientes = (
        Medicacion.objects
        .filter(
            activo=True,
            tomado=False
        )
        .select_related(
            "paciente"
        )
        .order_by(
            "horario"
        )[:10]
    )

    # ========================================================
    # RECORDATORIOS PENDIENTES
    # ========================================================

    recordatorios_pendientes = (
        Recordatorio.objects
        .filter(
            hecho=False
        )
        .select_related(
            "paciente"
        )
        .order_by(
            "fecha"
        )[:10]
    )

    # ========================================================
    # ESTUDIOS PENDIENTES
    # ========================================================

    estudios_pendientes = (
        SolicitudEstudio.objects
        .filter(
            estado="PENDIENTE"
        )
        .select_related(
            "paciente",
            "medico"
        )
        .order_by(
            "-fecha_solicitud"
        )[:10]
    )

    # ========================================================
    # CONTADORES
    # ========================================================

    evoluciones_recientes = (
        EvolucionEnfermeria.objects
        .select_related("paciente", "usuario")
        .order_by("-fecha")[:10]
    )
    total_pacientes = pacientes.count()
    total_alertas = alertas.count()
    total_medicaciones = medicaciones_pendientes.count()
    total_recordatorios = recordatorios_pendientes.count()
    total_estudios = estudios_pendientes.count()

    # ========================================================
    # CONTEXTO DEL PANEL
    # ========================================================

    contexto = {

        "pacientes": pacientes,

        "mis_pacientes": mis_pacientes,

        "evoluciones_recientes": evoluciones_recientes,

        "total_pacientes":
            total_pacientes,

        "alertas": alertas,

        "total_alertas":
            total_alertas,

        "medicaciones_pendientes":
            medicaciones_pendientes,

        "total_medicaciones":
            total_medicaciones,

        "recordatorios_pendientes":
            recordatorios_pendientes,

        "total_recordatorios":
            total_recordatorios,

        "estudios_pendientes":
            estudios_pendientes,

        "total_estudios":
            total_estudios,

        # ====================================================
        # JARVICE CLINICAL AI
        # ====================================================

        "ultimo_signo_vital":
            ultimo_signo_vital,

        "analisis_clinico":
            analisis_clinico,

        "estado_frecuencia":
            analisis_clinico["estado_frecuencia"],

        "estado_saturacion":
            analisis_clinico["estado_saturacion"],

        "estado_temperatura":
            analisis_clinico["estado_temperatura"],

        "estado_presion":
            analisis_clinico["estado_presion"],

        "estado_emocional":
            analisis_clinico["estado_emocional"],

        "riesgo_vital":
            analisis_clinico["riesgo_vital"],

        "color_riesgo_vital":
            analisis_clinico["color_riesgo_vital"],

        "estado_clinico_ia":
            analisis_clinico["estado_clinico_ia"],

        "nivel_riesgo_ia":
            analisis_clinico["nivel_riesgo_ia"],

        "color_riesgo_ia":
            analisis_clinico["color_riesgo_ia"],

        "analisis_ia":
            analisis_clinico["analisis_ia"],
    }

    # ========================================================
    # RENDER
    # ========================================================

    return render(
        request,
        "mi_app_salud/dashboard_enfermeria.html",
        contexto
    )

@requiere_rol("PACIENTE")
def panel_paciente(request):

    # ==================================================
    # PACIENTE AUTENTICADO
    # ==================================================

    paciente = getattr(
        request.user,
        "paciente",
        None
    )

    if paciente is None:

        messages.error(
            request,
            "Tu usuario todavía no está asociado a un paciente Jarvice."
        )

        return redirect("inicio")


    # ==================================================
    # SIGNOS VITALES
    # ==================================================

    signos_vitales = (
        SignoVital.objects
        .filter(paciente=paciente)
        .order_by("-fecha")
    )

    ultimo_signo_vital = signos_vitales.first()


    # ==================================================
    # ESTADO CLÍNICO
    # ==================================================

    registros_salud = (
        RegistroSalud.objects
        .filter(paciente=paciente)
        .order_by("-fecha")
    )

    ultimo_estado = registros_salud.first()


    # ==================================================
    # MEDICACIÓN
    # ==================================================

    medicaciones = (
        Medicacion.objects
        .filter(
            paciente=paciente,
            activo=True
        )
        .order_by("horario")
    )


    # ==================================================
    # RECORDATORIOS
    # ==================================================

    recordatorios = (
        Recordatorio.objects
        .filter(
            paciente=paciente,
            hecho=False
        )
        .order_by("fecha")
    )


    # ==================================================
    # ÚLTIMA EVOLUCIÓN MÉDICA
    # ==================================================

    ultima_evolucion = (
        EvolucionMedica.objects
        .filter(paciente=paciente)
        .order_by("-fecha")
        .first()
    )


    # ==================================================
    # CONTEXTO JARVICE
    # ==================================================

    contexto = {

        "paciente": paciente,

        "signos_vitales": signos_vitales[:10],

        "ultimo_signo_vital": ultimo_signo_vital,

        "ultimo_estado": ultimo_estado,

        "registros_salud": registros_salud[:10],

        "medicaciones": medicaciones,

        "recordatorios": recordatorios[:10],

        "ultima_evolucion": ultima_evolucion,

    }


    return render(
        request,
        "paciente/panel.html",
        contexto
    )


@requiere_rol("EMERGENCIA")
def panel_emergencia(request):

    # ==================================================
    # ALERTAS CRÍTICAS
    # ==================================================

    alertas_criticas = (
        RegistroSalud.objects
        .filter(
            estado="CRITICO"
        )
        .select_related(
            "paciente"
        )
        .order_by(
            "-fecha"
        )
    )

    # ==================================================
    # SITUACIONES DE DOLOR
    # ==================================================

    situaciones_dolor = (
        RegistroSalud.objects
        .filter(
            estado="DOLOR"
        )
        .select_related(
            "paciente"
        )
        .order_by(
            "-fecha"
        )
    )

    # ==================================================
    # ÚLTIMAS ALERTAS
    # ==================================================

    emergencias = (
        RegistroSalud.objects
        .filter(
            estado__in=[
                "CRITICO",
                "DOLOR",
            ]
        )
        .select_related(
            "paciente"
        )
        .order_by(
            "-fecha"
        )[:20]
    )

    # ==================================================
    # CONTADORES
    # ==================================================

    total_alertas = emergencias.count()

    total_criticas = alertas_criticas.count()

    total_dolor = situaciones_dolor.count()

    # ==================================================
    # CONTEXTO
    # ==================================================

    contexto = {

        "emergencias": emergencias,

        "alertas_criticas":
            alertas_criticas[:10],

        "situaciones_dolor":
            situaciones_dolor[:10],

        "total_alertas":
            total_alertas,

        "total_criticas":
            total_criticas,

        "total_dolor":
            total_dolor,
    }

    # ==================================================
    # RENDER
    # ==================================================

    return render(
        request,
        "mi_app_salud/emergencia.html",
        contexto
    )

    # ==================================================
# PANEL INSTITUCIÓN
# ==================================================

@requiere_rol("INSTITUCION")
def panel_institucion(request):

    solicitudes = SolicitudEstudio.objects.filter(
        estado="PENDIENTE"
    ).order_by("-fecha_solicitud")

    print("SOLICITUDES:", solicitudes)
    print("CANTIDAD:", solicitudes.count())

    return render(
        request,
        "mi_app_salud/panel_institucion.html",
        {
            "solicitudes": solicitudes
        }
    )
 # ==================================================
# CARGAR RESULTADO ESTUDIO (INSTITUCIÓN)
# ==================================================

@login_required
def cargar_resultado_estudio(request, solicitud_id):

    solicitud = get_object_or_404(
        SolicitudEstudio,
        id=solicitud_id
    )


    if request.method == "POST":

        print("==============================")
        print("POST RECIBIDO")
        print("DATOS:", request.POST)
        print("ARCHIVOS:", request.FILES)
        print("==============================")


        solicitud.informe = request.POST.get(
            "informe"
        )


        solicitud.archivo_informe = request.FILES.get(
            "archivo_informe"
        )


        solicitud.fecha_realizacion = timezone.now()


        solicitud.estado = "REALIZADO"


        solicitud.save()


        messages.success(
            request,
            "Resultado del estudio cargado correctamente."
        )


        return redirect(
            "panel_institucion"
        )


    return render(
        request,
        "mi_app_salud/cargar_resultado_estudio.html",
        {
            "solicitud": solicitud
        }
    )
# ==================================================
# CREAR PACIENTE
# ==================================================

@requiere_rol("ADMIN", "MEDICO", "ENFERMERIA")
def crear_paciente(request):

    if request.method == "POST":

        form = PacienteForm(request.POST)

        if form.is_valid():

            paciente = form.save(commit=False)

            # Generar historia clínica después de obtener el ID
            paciente.save()

            paciente.historia_clinica = f"HC{paciente.id:06d}"
            paciente.save(update_fields=["historia_clinica"])

            messages.success(
                request,
                f"Paciente {paciente.nombre} {paciente.apellido} creado correctamente."
            )

            return redirect("pacientes")

    else:

        form = PacienteForm()

    return render(
        request,
        "mi_app_salud/crear_paciente.html",
        {
            "form": form,
        }
    )

# ==================================================
# LISTADO PACIENTES
# ==================================================

@requiere_rol("ADMIN", "MEDICO", "ENFERMERIA")
def pacientes(request):

    pacientes = Paciente.objects.all()

    datos = []


    for paciente in pacientes:


        ultimo = RegistroSalud.objects.filter(
            paciente=paciente
        ).order_by("-fecha").first()


        datos.append(
            {
                "paciente": paciente,
                "ultimo": ultimo
            }
        )


    return render(
        request,
        "mi_app_salud/pacientes.html",
        {
            "datos": datos
        }
    )




# ==================================================
# HISTORIAL CLÍNICO DEL PACIENTE
# ==================================================

@requiere_rol("ADMIN", "MEDICO", "ENFERMERIA")
def historial_paciente(request, paciente_id):

    paciente = get_object_or_404(
        Paciente,
        id=paciente_id
    )

    # ==========================================
    # REGISTROS DE SALUD
    # ==========================================

    registros = RegistroSalud.objects.filter(
        paciente=paciente
    ).order_by("-fecha")

    ultimo_estado = registros.first()

    # ==========================================
    # RECORDATORIOS
    # ==========================================

    recordatorios = Recordatorio.objects.filter(
        paciente=paciente
    ).order_by("-fecha")

    # ==========================================
    # MEDICACIÓN
    # ==========================================

    medicaciones = Medicacion.objects.filter(
        paciente=paciente
    )

    # ==========================================
    # SIGNOS VITALES JARVICE
    # ==========================================

    signos_vitales = SignoVital.objects.filter(
        paciente=paciente
    ).order_by("-fecha")

    ultimo_signo_vital = signos_vitales.first()

    # ==========================================
    # EVOLUCIONES MÉDICAS
    # ==========================================

    evoluciones = EvolucionMedica.objects.filter(
        paciente=paciente
    ).order_by("-fecha")

    evoluciones_enfermeria = EvolucionEnfermeria.objects.filter(
    paciente=paciente
).select_related("usuario").order_by("-fecha")

    # ==========================================
    # ESTUDIOS SOLICITADOS
    # ==========================================

    solicitudes_estudios = SolicitudEstudio.objects.filter(
        paciente=paciente
    ).order_by("-fecha_solicitud")

    # ==========================================
    # ANÁLISIS DE RIESGO JARVICE
    # ==========================================

    riesgo = "BAJO"
    color_riesgo = "verde"

    # ==========================================
    # ANALIZAR ÚLTIMO ESTADO
    # ==========================================

    if ultimo_estado:

        if ultimo_estado.estado == "CRITICO":

            riesgo = "CRITICO"
            color_riesgo = "rojo"

        elif ultimo_estado.estado in [
            "DOLOR",
            "CANSADO"
        ]:

            riesgo = "ATENCION"
            color_riesgo = "amarillo"

    # ==========================================
    # ANALIZAR MEDICACIÓN
    # ==========================================

    for medicamento in medicaciones:

        if not medicamento.activo:

            if riesgo != "CRITICO":

                riesgo = "ATENCION"
                color_riesgo = "amarillo"

    # ==========================================
    # PROTEGER ESTADO CRÍTICO
    # ==========================================

    if (
        ultimo_estado
        and ultimo_estado.estado == "CRITICO"
    ):

        riesgo = "CRITICO"
        color_riesgo = "rojo"

    # ==========================================
    # CONTEXTO DE LA HISTORIA CLÍNICA
    # ==========================================

    contexto = {
        "paciente": paciente,

        "registros": registros,

        "recordatorios": recordatorios,

        "medicaciones": medicaciones,

        "signos_vitales": signos_vitales,

        "ultimo_signo_vital": ultimo_signo_vital,

        "ultimo_estado": ultimo_estado,

        "evoluciones": evoluciones,

        "solicitudes_estudios": solicitudes_estudios,

        "riesgo": riesgo,

        "color_riesgo": color_riesgo,

        "evoluciones_enfermeria": evoluciones_enfermeria,
    }

    return render(
        request,
        "mi_app_salud/historial_paciente.html",
        contexto
    )
# ==================================================
# CREAR EVOLUCIÓN MÉDICA
# ==================================================

@requiere_rol("ADMIN", "MEDICO")
def crear_evolucion(request, paciente_id):

    paciente = get_object_or_404(
        Paciente,
        id=paciente_id
    )

    if request.method == "POST":

        descripcion = request.POST.get("descripcion")
        diagnostico = request.POST.get("diagnostico")
        indicaciones = request.POST.get("indicaciones")

        EvolucionMedica.objects.create(
    paciente=paciente,
    usuario=request.user,
    descripcion=descripcion,
    diagnostico=diagnostico,
    indicaciones=indicaciones
)


        messages.success(
            request,
            "Evolución médica registrada correctamente"
        )

        return redirect(
            "historial_paciente",
            paciente_id=paciente.id
        )

    return render(
        request,
        "mi_app_salud/crear_evolucion.html",
        {
            "paciente": paciente
        }
    )


@requiere_rol("ADMIN", "MEDICO")
def crear_estudio(request, paciente_id):

    paciente = get_object_or_404(
        Paciente,
        id=paciente_id
    )

    if request.method == "POST":

        EstudioMedico.objects.create(
            paciente=paciente,
            tipo=request.POST.get("tipo"),
            nombre=request.POST.get("nombre"),
            fecha=request.POST.get("fecha"),
            observaciones=request.POST.get("observaciones"),
            archivo=request.FILES.get("archivo")
        )

        messages.success(
            request,
            "Estudio médico registrado correctamente."
        )

        return redirect(
            "historial_paciente",
            paciente_id=paciente.id
        )

    return render(
        request,
        "mi_app_salud/crear_estudio.html",
        {
            "paciente": paciente
        }
    )
   # ==================================================
# EVOLUCIÓN DE ENFERMERÍA
# ==================================================

@requiere_rol("ADMIN", "ENFERMERIA")
def crear_evolucion_enfermeria(request, paciente_id):

    paciente = get_object_or_404(
        Paciente,
        id=paciente_id
    )

    if request.method == "POST":

        estado = request.POST.get("estado")
        observaciones = request.POST.get("observaciones", "").strip()
        intervenciones = request.POST.get("intervenciones", "").strip()
        incidentes = request.POST.get("incidentes", "").strip()

        if not observaciones:
            messages.error(
                request,
                "Las observaciones son obligatorias."
            )

            return render(
                request,
                "mi_app_salud/crear_evolucion_enfermeria.html",
                {
                    "paciente": paciente,
                    "estados": EvolucionEnfermeria.ESTADOS,
                    "estado_seleccionado": estado,
                    "observaciones": observaciones,
                    "intervenciones": intervenciones,
                    "incidentes": incidentes,
                }
            )

        EvolucionEnfermeria.objects.create(
            paciente=paciente,
            usuario=request.user,
            estado=estado or "ESTABLE",
            observaciones=observaciones,
            intervenciones=intervenciones,
            incidentes=incidentes,
        )

        messages.success(
            request,
            "Evolución de enfermería registrada correctamente."
        )

        return redirect(
            "historial_paciente",
            paciente_id=paciente.id
        )

    return render(
        request,
        "mi_app_salud/crear_evolucion_enfermeria.html",
        {
            "paciente": paciente,
            "estados": EvolucionEnfermeria.ESTADOS,
        }
    )

# ==================================================
# RECORDATORIOS
# ==================================================

@requiere_rol("ADMIN", "MEDICO", "ENFERMERIA")
def crear_recordatorio(request, paciente_id):

    paciente = get_object_or_404(
        Paciente,
        id=paciente_id
    )


    if request.method == "POST":

        texto = request.POST.get("texto")


        if texto:

            Recordatorio.objects.create(
                paciente=paciente,
                texto=texto
            )


            messages.success(
                request,
                "Recordatorio creado correctamente"
            )


        else:

            messages.error(
                request,
                "Ingrese un texto"
            )


        return redirect(
            "historial_paciente",
            paciente_id=paciente.id
        )


    return render(
        request,
        "mi_app_salud/crear_recordatorio.html",
        {
            "paciente": paciente
        }
    )



@login_required
def seguridad(request):

    # ==================================================
    # USUARIO Y PERFIL
    # ==================================================

    perfil = getattr(
        request.user,
        "perfilusuario",
        None
    )

    # ==================================================
    # PACIENTE ASOCIADO AL USUARIO
    # ==================================================

    paciente = getattr(
        request.user,
        "paciente",
        None
    )

    # ==================================================
    # CONTACTOS DE EMERGENCIA
    # ==================================================

    contactos_emergencia = []

    if paciente:

        if paciente.contacto_emergencia:
            contactos_emergencia.append({
                "nombre": paciente.contacto_emergencia,
                "telefono": paciente.telefono_emergencia,
                "tipo": "Familiar principal",
                "icono": "👨‍👩‍👧",
            })

        if paciente.contacto_emergencia_2:
            contactos_emergencia.append({
                "nombre": paciente.contacto_emergencia_2,
                "telefono": paciente.telefono_emergencia_2,
                "tipo": "Contacto secundario",
                "icono": "👨‍👩‍👧",
            })

        if paciente.contacto_emergencia_3:
            contactos_emergencia.append({
                "nombre": paciente.contacto_emergencia_3,
                "telefono": paciente.telefono_emergencia_3,
                "tipo": "Contacto adicional",
                "icono": "👨‍👩‍👧",
            })

    # ==================================================
    # DISPOSITIVOS
    # ==================================================

    dispositivos = []

    if paciente:
        dispositivos = paciente.dispositivos.filter(
            activo=True
        ).order_by("-ultima_conexion")

    # ==================================================
    # AUDITORÍA
    # ==================================================

    # ==================================================
    # AUDITORÍA Y ACCESOS CLÍNICOS
    # ==================================================

    auditorias = AuditoriaJarvice.objects.none()
    accesos_clinicos = AccesoClinico.objects.none()

    # El administrador puede consultar la actividad global.
    if perfil and perfil.rol == "ADMIN":

        auditorias = AuditoriaJarvice.objects.select_related(
            "usuario"
        ).order_by(
            "-fecha"
        )[:10]

        accesos_clinicos = AccesoClinico.objects.select_related(
            "usuario",
            "paciente"
        ).order_by(
            "-fecha_solicitud"
        )[:10]

    # Los demás usuarios no reciben registros globales
    # de auditoría ni accesos clínicos de otros usuarios.

    # ==================================================
    # CONTEXTO
    # ==================================================

    contexto = {
        "perfil": perfil,
        "paciente": paciente,
        "contactos_emergencia": contactos_emergencia,
        "dispositivos": dispositivos,
        "auditorias": auditorias,
        "accesos_clinicos": accesos_clinicos,
    }

    return render(
        request,
        "mi_app_salud/seguridad.html",
        contexto
    )

# ==================================================
# API PACIENTES
# ==================================================

@requiere_rol("ADMIN", "MEDICO", "ENFERMERIA")
def api_pacientes(request):

    pacientes = Paciente.objects.all()

    data = []


    for paciente in pacientes:

        data.append(
            {
                "id": paciente.id,
                "nombre": paciente.nombre,
                "apellido": paciente.apellido,
                "edad": paciente.edad
            }
        )


    return JsonResponse(
        {
            "pacientes": data
        }
    )
# ==========================================================
# ESCALAMIENTO DE EMERGENCIA JARVICE
# ==========================================================

def escalar_emergencia(
    request,
    paciente,
    signo,
    analisis
):

    # ======================================================
    # DATOS COMUNES
    # ======================================================

    mensaje_base = f"""
🚨 ALERTA CRÍTICA JARVICE

Paciente:
{paciente.nombre} {paciente.apellido}

RIESGO:
CRÍTICO

❤️ Frecuencia cardíaca:
{signo.frecuencia_cardiaca if signo.frecuencia_cardiaca is not None else "Sin dato"} lpm

🫁 Saturación:
{signo.saturacion_oxigeno if signo.saturacion_oxigeno is not None else "Sin dato"} %

🌡️ Temperatura:
{signo.temperatura if signo.temperatura is not None else "Sin dato"} °C

🩺 Presión arterial:
{signo.presion_arterial or "Sin dato"}

🧠 Estado emocional:
{signo.estado_emocional or "Sin dato"}

📡 Origen:
{signo.origen}

⚠️ Jarvice detectó parámetros clínicos críticos.

Se requiere atención inmediata.
"""

    # ======================================================
    # CONTACTO 1
    # ======================================================

    contacto_1 = paciente.contacto_emergencia
    telefono_1 = paciente.telefono_emergencia

    if telefono_1:

        mensaje_1 = (
            "🚨 CONTACTO DE EMERGENCIA JARVICE\n\n"
            + mensaje_base
        )

        enviado_1 = enviar_whatsapp_a(
            telefono_1,
            mensaje_1
        )

        registrar_auditoria(
            request=request,
            accion="EMERGENCIA",
            modulo="ESCALAMIENTO",
            descripcion=(
                f"Primer contacto de emergencia "
                f"{'notificado' if enviado_1 else 'no pudo ser notificado'}."
            ),
            datos_extra={
                "nivel": 1,
                "paciente_id": paciente.id,
                "signo_id": signo.id,
                "contacto": contacto_1,
                "telefono": telefono_1,
                "enviado": enviado_1,
            }
        )

        if enviado_1:
            return {
                "nivel": 1,
                "estado": "CONTACTO_1_NOTIFICADO",
                "contacto": contacto_1,
                "telefono": telefono_1,
            }

    else:

        registrar_auditoria(
            request=request,
            accion="EMERGENCIA",
            modulo="ESCALAMIENTO",
            descripcion=(
                "No existe teléfono configurado "
                "para el primer contacto de emergencia."
            ),
            datos_extra={
                "nivel": 1,
                "paciente_id": paciente.id,
                "signo_id": signo.id,
            }
        )

    # ======================================================
    # CONTACTO 2
    # ======================================================

    contacto_2 = paciente.contacto_emergencia_2
    telefono_2 = paciente.telefono_emergencia_2

    if telefono_2:

        mensaje_2 = (
            "🚨 SEGUNDO CONTACTO JARVICE\n\n"
            + mensaje_base
            + "\n\nEl primer contacto no pudo ser notificado."
        )

        enviado_2 = enviar_whatsapp_a(
            telefono_2,
            mensaje_2
        )

        registrar_auditoria(
            request=request,
            accion="EMERGENCIA",
            modulo="ESCALAMIENTO",
            descripcion=(
                f"Segundo contacto "
                f"{'notificado' if enviado_2 else 'no pudo ser notificado'}."
            ),
            datos_extra={
                "nivel": 2,
                "paciente_id": paciente.id,
                "signo_id": signo.id,
                "contacto": contacto_2,
                "telefono": telefono_2,
                "enviado": enviado_2,
            }
        )

        if enviado_2:
            return {
                "nivel": 2,
                "estado": "CONTACTO_2_NOTIFICADO",
                "contacto": contacto_2,
                "telefono": telefono_2,
            }

    # ======================================================
    # CONTACTO 3
    # ======================================================

    contacto_3 = paciente.contacto_emergencia_3
    telefono_3 = paciente.telefono_emergencia_3

    if telefono_3:

        mensaje_3 = (
            "🚨 EMERGENCIA JARVICE\n\n"
            + mensaje_base
            + "\n\nNo fue posible notificar los contactos anteriores."
        )

        enviado_3 = enviar_whatsapp_a(
            telefono_3,
            mensaje_3
        )

        registrar_auditoria(
            request=request,
            accion="EMERGENCIA",
            modulo="ESCALAMIENTO",
            descripcion=(
                f"Tercer contacto "
                f"{'notificado' if enviado_3 else 'no pudo ser notificado'}."
            ),
            datos_extra={
                "nivel": 3,
                "paciente_id": paciente.id,
                "signo_id": signo.id,
                "contacto": contacto_3,
                "telefono": telefono_3,
                "enviado": enviado_3,
            }
        )

        if enviado_3:
            return {
                "nivel": 3,
                "estado": "CONTACTO_3_NOTIFICADO",
                "contacto": contacto_3,
                "telefono": telefono_3,
            }

    # ======================================================
    # NINGÚN CONTACTO DISPONIBLE
    # ======================================================

    registrar_auditoria(
        request=request,
        accion="EMERGENCIA",
        modulo="ESCALAMIENTO",
        descripcion=(
            "Jarvice no pudo notificar ningún contacto "
            "de emergencia configurado."
        ),
        datos_extra={
            "paciente_id": paciente.id,
            "signo_id": signo.id,
            "nivel": 0,
            "estado": "SIN_CONTACTO",
        }
    )

    return {
        "nivel": 0,
        "estado": "SIN_CONTACTO",
        "contacto": None,
        "telefono": None,
    }
# ==================================================
# API SIGNOS VITALES JARVICE
# ==================================================

@requiere_rol("ADMIN", "MEDICO", "ENFERMERIA")
def api_signos_vitales(request):

    if request.method != "POST":
        return JsonResponse(
            {
                "ok": False,
                "error": "Metodo no permitido. Utilice POST."
            },
            status=405
        )

    # ==================================================
    # LEER JSON
    # ==================================================

    try:

        import json

        datos = json.loads(
            request.body.decode("utf-8")
        )

    except (json.JSONDecodeError, UnicodeDecodeError):

        return JsonResponse(
            {
                "ok": False,
                "error": "JSON invalido."
            },
            status=400
        )

    # ==================================================
    # PACIENTE
    # ==================================================

    paciente_id = datos.get("paciente_id")

    if not paciente_id:

        return JsonResponse(
            {
                "ok": False,
                "error": "paciente_id es obligatorio."
            },
            status=400
        )

    paciente = get_object_or_404(
        Paciente,
        id=paciente_id
    )

    # ==================================================
    # DATOS VITALES
    # ==================================================

    frecuencia_cardiaca = datos.get(
        "frecuencia_cardiaca"
    )

    saturacion_oxigeno = datos.get(
        "saturacion_oxigeno"
    )

    temperatura = datos.get(
        "temperatura"
    )

    presion_arterial = datos.get(
        "presion_arterial",
        ""
    )

    estado_emocional = datos.get(
        "estado_emocional",
        ""
    )

    origen = datos.get(
        "origen",
        "MANUAL"
    )

    observaciones = datos.get(
        "observaciones",
        ""
    )

    # ==================================================
    # ORIGEN VALIDO
    # ==================================================

    origenes_validos = [
        "MANUAL",
        "SMARTWATCH",
        "SENSOR",
        "SISTEMA",
    ]

    if origen not in origenes_validos:

        return JsonResponse(
            {
                "ok": False,
                "error": "Origen de datos no valido."
            },
            status=400
        )

    # ==================================================
    # CREAR SIGNO VITAL
    # ==================================================

    signo = SignoVital.objects.create(

        paciente=paciente,

        frecuencia_cardiaca=(
            frecuencia_cardiaca
            if frecuencia_cardiaca not in ["", None]
            else None
        ),

        saturacion_oxigeno=(
            saturacion_oxigeno
            if saturacion_oxigeno not in ["", None]
            else None
        ),

        temperatura=(
            temperatura
            if temperatura not in ["", None]
            else None
        ),

        presion_arterial=presion_arterial,

        estado_emocional=estado_emocional,

        origen=origen,

        observaciones=observaciones,
    )

    # ==================================================
    # ANALISIS CLINICO JARVICE
    # ==================================================

    from .clinical_engine import analizar_signos_vitales

    analisis = analizar_signos_vitales(
        signo
    )

    # ==================================================
    # AUDITORIA DE ALERTA CLINICA
    # ==================================================

    if analisis["riesgo_vital"] == "CRITICO":

        registrar_auditoria(
            request=request,
            accion="EMERGENCIA",
            modulo="SIGNOS_VITALES",
            descripcion=(
                f"Jarvice detecto riesgo critico "
                f"en el paciente "
                f"{paciente.nombre} {paciente.apellido}."
            ),
            datos_extra={
                "paciente_id": paciente.id,
                "signo_id": signo.id,
                "riesgo_vital": analisis["riesgo_vital"],
                "estado_clinico_ia": analisis["estado_clinico_ia"],
                "nivel_riesgo_ia": analisis["nivel_riesgo_ia"],
                "frecuencia_cardiaca": signo.frecuencia_cardiaca,
                "saturacion_oxigeno": (
                    float(signo.saturacion_oxigeno)
                    if signo.saturacion_oxigeno is not None
                    else None
                ),
                "temperatura": (
                    float(signo.temperatura)
                    if signo.temperatura is not None
                    else None
                ),
                "presion_arterial": signo.presion_arterial,
                "estado_emocional": signo.estado_emocional,
                "origen": signo.origen,
            }
        )

    # ==================================================
    # ESCALAMIENTO AUTOMATICO JARVICE
    # ==================================================

    escalamiento = None

    if analisis["riesgo_vital"] == "CRITICO":

        escalamiento = escalar_emergencia(
            request=request,
            paciente=paciente,
            signo=signo,
            analisis=analisis
        )

    # ==================================================
    # RESPUESTA
    # ==================================================

    return JsonResponse(
        {
            "ok": True,

            "signo_id": signo.id,

            "paciente": {
                "id": paciente.id,
                "nombre": paciente.nombre,
                "apellido": paciente.apellido,
            },

            "signos_vitales": {

                "frecuencia_cardiaca":
                    signo.frecuencia_cardiaca,

                "saturacion_oxigeno": (
                    float(signo.saturacion_oxigeno)
                    if signo.saturacion_oxigeno is not None
                    else None
                ),

                "temperatura": (
                    float(signo.temperatura)
                    if signo.temperatura is not None
                    else None
                ),

                "presion_arterial":
                    signo.presion_arterial,

                "estado_emocional":
                    signo.estado_emocional,

                "origen":
                    signo.origen,

                "fecha":
                    signo.fecha.isoformat(),
            },

            "analisis": analisis,

            "escalamiento": escalamiento,
        }
    )


# ==================================================
# API CAMBIAR ESTADO SALUD
# ==================================================

@login_required
def api_cambiar_estado(request, paciente_id):

    if request.method != "GET":
        return JsonResponse(
            {
                "ok": False,
                "error": "Método no permitido. Utilice GET."
            },
            status=405
        )

    paciente = get_object_or_404(
        Paciente,
        id=paciente_id
    )

    estado = request.GET.get(
        "estado",
        "OK"
    )

    estados_validos = [
        "OK",
        "CANSADO",
        "DOLOR",
        "CRITICO"
    ]

    if estado not in estados_validos:
        return JsonResponse(
            {
                "ok": False,
                "error": "Estado de salud no válido."
            },
            status=400
        )

    RegistroSalud.objects.create(
    paciente=paciente,
    estado_fisico=estado,
    estado_emocional="NEUTRO",
    estado=estado
)

    return JsonResponse(
        {
            "ok": True,

            "paciente": {
                "id": paciente.id,
                "nombre": paciente.nombre,
                "apellido": paciente.apellido,
            },

            "estado": estado,

            "mensaje":
                "Estado de salud actualizado correctamente."
        }
    )
# ==================================================
# CONTACTOS EMERGENCIA
# ==================================================

@requiere_rol("ADMIN", "EMERGENCIA")
def segundo_contacto(request):

    return JsonResponse(
        {
            "ok": True,
            "mensaje": "Segundo contacto notificado"
        }
    )



@requiere_rol("ADMIN", "EMERGENCIA")
def tercer_contacto(request):

    return JsonResponse(
        {
            "ok": True,
            "mensaje": "Emergencias notificadas"
        }
    )



# ==================================================
# CAMBIO ESTADO MANUAL
# ==================================================

@login_required
def cambiar_estado(request, paciente_id, estado):

    paciente = get_object_or_404(
        Paciente,
        id=paciente_id
    )


    estados_validos = [
        "OK",
        "CANSADO",
        "DOLOR",
        "CRITICO"
    ]


    if estado not in estados_validos:

        estado = "OK"



    RegistroSalud.objects.create(

        paciente=paciente,

        estado_fisico=estado,

        estado_emocional="NEUTRO",

        estado=estado

    )


    return JsonResponse(
        {
            "ok": True,
            "estado": estado
        }
    )



# ==================================================
# MEDICACION
# ==================================================

@requiere_rol("ADMIN", "MEDICO", "ENFERMERIA")
def medicacion(request):

    medicamentos = (
        Medicacion.objects
        .select_related("paciente", "confirmado_por")
        .order_by("horario")
    )

    return render(
        request,
        "mi_app_salud/medicacion.html",
        {
            "medicamentos": medicamentos
        }
    )


# ==================================================
# CREAR MEDICACION
# ==================================================

@requiere_rol("ADMIN", "MEDICO")
def crear_medicacion(request):

    pacientes = Paciente.objects.all()


    if request.method == "POST":

        paciente_id = request.POST.get("paciente")

        nombre = request.POST.get("nombre")

        dosis = request.POST.get("dosis")

        horario = request.POST.get("horario")



        if not nombre or not dosis or not horario:

            messages.error(
                request,
                "Complete todos los campos"
            )

            return redirect(
                "crear_medicacion"
            )



        paciente = get_object_or_404(
            Paciente,
            id=paciente_id
        )



        Medicacion.objects.create(

            paciente=paciente,

            nombre=nombre,

            dosis=dosis,

            horario=horario,

            activo=True

        )



        messages.success(
            request,
            "Medicamento agregado correctamente"
        )


        return redirect(
            "medicacion"
        )



    return render(
        request,
        "mi_app_salud/crear_medicacion.html",
        {
            "pacientes": pacientes
        }
    )





# ==========================================
# TOMAR MEDICACION
# ==========================================


@requiere_rol("ADMIN", "MEDICO", "ENFERMERIA")
def tomar_medicacion(request, medicamento_id):

    medicamento = get_object_or_404(
        Medicacion,
        id=medicamento_id
    )

    medicamento.tomado = True
    medicamento.fecha_ultima_toma = timezone.now()

    # Guarda el usuario que confirmó
    medicamento.confirmado_por = request.user

    medicamento.save()

    messages.success(
        request,
        f"{medicamento.nombre} marcado como tomado."
    )

    return redirect("medicacion")

# ==================================================
# EDITAR MEDICACION
# ==================================================

@requiere_rol("ADMIN", "MEDICO")
def editar_medicacion(request, medicamento_id):

    medicamento = get_object_or_404(
        Medicacion,
        id=medicamento_id
    )


    pacientes = Paciente.objects.all()



    if request.method == "POST":


        medicamento.paciente = get_object_or_404(
            Paciente,
            id=request.POST.get("paciente")
        )


        medicamento.nombre = request.POST.get(
            "nombre"
        )


        medicamento.dosis = request.POST.get(
            "dosis"
        )


        medicamento.horario = request.POST.get(
            "horario"
        )


        medicamento.save()



        messages.success(
            request,
            "Medicación actualizada correctamente."
        )


        return redirect(
            "medicacion"
        )



    return render(
        request,
        "mi_app_salud/editar_medicacion.html",
        {
            "medicamento": medicamento,
            "pacientes": pacientes
        }
    )



# ==================================================
# SUSPENDER / REACTIVAR MEDICACION
# ==================================================

@requiere_rol("ADMIN", "MEDICO")
def cambiar_estado_medicacion(request, medicamento_id):

    medicamento = get_object_or_404(
        Medicacion,
        id=medicamento_id
    )


    medicamento.activo = not medicamento.activo

    medicamento.save()



    if medicamento.activo:

        messages.success(
            request,
            "Medicación reactivada."
        )

    else:

        messages.warning(
            request,
            "Medicación suspendida."
        )


    return redirect(
        "medicacion"
    )



# ==================================================
# ELIMINAR MEDICACION
# ==================================================

@requiere_rol("ADMIN", "MEDICO")
def eliminar_medicacion(request, medicamento_id):

    medicamento = get_object_or_404(
        Medicacion,
        id=medicamento_id
    )


    medicamento.delete()


    messages.success(
        request,
        "Medicación eliminada correctamente."
    )


    return redirect(
        "medicacion"
    )



# ==================================================
# MÓDULOS JARVICE
# ==================================================

@requiere_rol("PACIENTE")
def sueno(request):

    return render(
        request,
        "mi_app_salud/sueno.html"
    )


@login_required
def reportes(request):

    from django.db.models import Count
    from mi_app_salud.models import (
        Paciente,
        RegistroSalud,
        SignoVital,
        Medicacion,
        EvolucionMedica,
        EstudioMedico,
    )

    # ==================================================
    # DETERMINAR ROL Y PACIENTES VISIBLES
    # ==================================================

    rol = getattr(
        getattr(request.user, "perfilusuario", None),
        "rol",
        None
    )

    paciente_actual = getattr(
        request.user,
        "paciente",
        None
    )

    if rol == "PACIENTE":

        if paciente_actual is None:
            messages.error(
                request,
                "Tu usuario no está asociado a un paciente Jarvice."
            )
            return redirect("inicio")

        pacientes_visibles = Paciente.objects.filter(
            id=paciente_actual.id
        )

    elif rol == "ENFERMERIA":

        pacientes_visibles = Paciente.objects.filter(
            enfermera_asignada__usuario=request.user
        )

    else:

        # ADMIN y MEDICO mantienen el alcance global
        pacientes_visibles = Paciente.objects.all()

    # ==================================================
    # DATOS GENERALES
    # ==================================================

    total_pacientes = pacientes_visibles.count()

    total_signos = SignoVital.objects.filter(
        paciente__in=pacientes_visibles
    ).count()

    total_medicaciones = Medicacion.objects.filter(
        paciente__in=pacientes_visibles
    ).count()

    total_evoluciones = EvolucionMedica.objects.filter(
        paciente__in=pacientes_visibles
    ).count()

    total_estudios = EstudioMedico.objects.filter(
        paciente__in=pacientes_visibles
    ).count()

    # ==================================================
    # SIGNOS VITALES
    # ==================================================

    signos = (
        SignoVital.objects
        .filter(paciente__in=pacientes_visibles)
        .select_related("paciente")
        .order_by("fecha")
    )

    signos_data = []

    for signo in signos:

        signos_data.append({
            "fecha": signo.fecha.strftime("%d/%m %H:%M"),
            "paciente": (
                f"{signo.paciente.nombre} "
                f"{signo.paciente.apellido}"
            ),
            "frecuencia_cardiaca": (
                signo.frecuencia_cardiaca
                if signo.frecuencia_cardiaca is not None
                else None
            ),
            "saturacion": (
                float(signo.saturacion_oxigeno)
                if signo.saturacion_oxigeno is not None
                else None
            ),
            "temperatura": (
                float(signo.temperatura)
                if signo.temperatura is not None
                else None
            ),
        })

    # ==================================================
    # ESTADO FÍSICO
    # ==================================================

    estados_fisicos = (
        RegistroSalud.objects
        .filter(paciente__in=pacientes_visibles)
        .values("estado_fisico")
        .annotate(total=Count("id"))
        .order_by("estado_fisico")
    )

    estado_fisico_data = [
        {
            "estado": item["estado_fisico"],
            "total": item["total"],
        }
        for item in estados_fisicos
    ]

    # ==================================================
    # ESTADO EMOCIONAL
    # ==================================================

    estados_emocionales = (
        RegistroSalud.objects
        .filter(paciente__in=pacientes_visibles)
        .values("estado_emocional")
        .annotate(total=Count("id"))
        .order_by("estado_emocional")
    )

    estado_emocional_data = [
        {
            "estado": item["estado_emocional"],
            "total": item["total"],
        }
        for item in estados_emocionales
    ]

    # ==================================================
    # MEDICACIÓN
    # ==================================================

    medicamentos_tomados = Medicacion.objects.filter(
        paciente__in=pacientes_visibles,
        tomado=True
    ).count()

    medicamentos_pendientes = Medicacion.objects.filter(
        paciente__in=pacientes_visibles,
        tomado=False
    ).count()

    medicacion_data = [
        {
            "estado": "Tomados",
            "total": medicamentos_tomados,
        },
        {
            "estado": "Pendientes",
            "total": medicamentos_pendientes,
        },
    ]

    # ==================================================
    # ESTADOS CRÍTICOS
    # ==================================================

    alertas_criticas = RegistroSalud.objects.filter(
        paciente__in=pacientes_visibles,
        estado_fisico="CRITICO"
    ).count()

    # ==================================================
    # ÚLTIMO REGISTRO VITAL
    # ==================================================

    ultimo_signo = signos.last()

    ultimo_pulso = (
        ultimo_signo.frecuencia_cardiaca
        if ultimo_signo
        and ultimo_signo.frecuencia_cardiaca is not None
        else None
    )

    ultima_saturacion = (
        float(ultimo_signo.saturacion_oxigeno)
        if ultimo_signo
        and ultimo_signo.saturacion_oxigeno is not None
        else None
    )

    ultima_temperatura = (
        float(ultimo_signo.temperatura)
        if ultimo_signo
        and ultimo_signo.temperatura is not None
        else None
    )

    # ==================================================
    # CONTEXTO
    # ==================================================

    contexto = {
        "total_pacientes": total_pacientes,
        "total_signos": total_signos,
        "total_medicaciones": total_medicaciones,
        "total_evoluciones": total_evoluciones,
        "total_estudios": total_estudios,
        "alertas_criticas": alertas_criticas,
        "ultimo_pulso": ultimo_pulso,
        "ultima_saturacion": ultima_saturacion,
        "ultima_temperatura": ultima_temperatura,
        "signos_data": signos_data,
        "estado_fisico_data": estado_fisico_data,
        "estado_emocional_data": estado_emocional_data,
        "medicacion_data": medicacion_data,
    }

    return render(
        request,
        "mi_app_salud/reportes.html",
        contexto
    )



@login_required
def configuracion(request):

    return render(
        request,
        "mi_app_salud/configuracion.html"
    )

# ==================================================
# CENTRO DE ATENCION JARVICE
# ==================================================

@login_required
def crear_solicitud_usuario(request):

    if request.method == "POST":

        formulario = SolicitudUsuarioForm(
            request.POST
        )

        if formulario.is_valid():

            solicitud = formulario.save(
                commit=False
            )

            solicitud.usuario = request.user

            solicitud.save()

            messages.success(
                request,
                "Tu solicitud fue enviada correctamente a Jarvice."
            )

            return redirect("configuracion")

    else:

        formulario = SolicitudUsuarioForm()

    return render(
        request,
        "mi_app_salud/solicitud_usuario.html",
        {
            "formulario": formulario
        }
    )

# ==================================================
# LOGOUT
# ==================================================

@login_required
def salir(request):

    # ==========================================
    # AUDITORÍA JARVICE CORE
    # ==========================================

    if request.user.is_authenticated:

        registrar_auditoria(
            request=request,
            accion="LOGOUT",
            modulo="AUTENTICACION",
            descripcion=f"Cierre de sesión del usuario {request.user.username}",
        )

    # ==========================================
    # CERRAR SESIÓN
    # ==========================================

    logout(request)

    return redirect("login")

# ==================================================
# EMERGENCIA
# ==================================================

@requiere_rol("ADMIN", "EMERGENCIA")
def emergencia(request):

    return render(
        request,
        "mi_app_salud/emergencia.html"
    )
# ==================================================
# PANEL FAMILIAR
# ==================================================

@requiere_rol("FAMILIAR")
def panel_familiar(request):

    return render(
        request,
        "mi_app_salud/panel_familiar.html"
    )

@login_required
@requiere_rol("ADMIN")
def admin_usuarios(request):

    # ==========================================
    # BUSCADOR
    # ==========================================

    buscar = request.GET.get("buscar", "").strip()

    # ==========================================
    # USUARIOS + PERFIL
    # ==========================================

    usuarios = (
        User.objects
        .select_related("perfilusuario")
        .all()
        .order_by("username")
    )

    # ==========================================
    # FILTRAR USUARIOS
    # ==========================================

    if buscar:
        usuarios = usuarios.filter(
            Q(username__icontains=buscar)
            | Q(email__icontains=buscar)
            | Q(first_name__icontains=buscar)
            | Q(last_name__icontains=buscar)
            | Q(perfilusuario__nombre__icontains=buscar)
            | Q(perfilusuario__apellido__icontains=buscar)
            | Q(perfilusuario__rol__icontains=buscar)
        ).distinct()

    # ==========================================
    # ESTADÍSTICAS
    # ==========================================

    total_usuarios = usuarios.count()

    total_activos = usuarios.filter(
        is_active=True
    ).count()

    total_inactivos = usuarios.filter(
        is_active=False
    ).count()

    total_superusuarios = usuarios.filter(
        is_superuser=True
    ).count()

    # ==========================================
    # CONTEXTO
    # ==========================================

    contexto = {
        "usuarios": usuarios,
        "buscar": buscar,
        "total_usuarios": total_usuarios,
        "total_activos": total_activos,
        "total_inactivos": total_inactivos,
        "total_superusuarios": total_superusuarios,
    }

    # ==========================================
    # RENDER USUARIOS
    # ==========================================

    return render(
        request,
        "mi_app_salud/admin_usuarios.html",
        contexto
    )

@login_required
@requiere_rol("ADMIN")
def admin_seguridad(request):

    # ==========================================
    # AUDITORÍA
    # ==========================================

    auditorias = (
        AuditoriaJarvice.objects
        .select_related("usuario")
        .order_by("-fecha")
    )

    # ==========================================
    # ESTADÍSTICAS
    # ==========================================

    total_eventos = auditorias.count()

    total_logins = auditorias.filter(
        accion="LOGIN"
    ).count()

    total_logouts = auditorias.filter(
        accion="LOGOUT"
    ).count()

    total_emergencias = auditorias.filter(
        accion="EMERGENCIA"
    ).count()

    # ==========================================
    # CONTEXTO
    # ==========================================

    contexto = {
        "auditorias": auditorias,
        "total_eventos": total_eventos,
        "total_logins": total_logins,
        "total_logouts": total_logouts,
        "total_emergencias": total_emergencias,
    }

    # ==========================================
    # RENDER SEGURIDAD
    # ==========================================

    return render(
        request,
        "mi_app_salud/admin_seguridad.html",
        contexto
    )
    # ==================================================
# CENTRO DE ATENCIÓN JARVICE - ADMINISTRADOR
# ==================================================

@login_required
@requiere_rol("ADMIN")
def centro_atencion_admin(request):

    # ==============================================
    # SEGURIDAD JARVICE CORE
    # ==============================================

    if not request.user.is_superuser:

        messages.error(
            request,
            "Acceso restringido al administrador Jarvice."
        )

        return redirect("inicio")

    # ==============================================
    # SESIÓN CORE
    # ==============================================

    if not request.session.get(
        "jarvice_core_autorizado",
        False
    ):

        messages.error(
            request,
            "Debés realizar el acceso seguro al JARVICE CORE."
        )

        return redirect(
            "acceso_admin_jarvice"
        )

    # ==============================================
    # SOLICITUDES
    # ==============================================

    solicitudes = (
        SolicitudUsuario.objects
        .select_related("usuario")
        .order_by("-fecha_creacion")
    )

    total_solicitudes = solicitudes.count()

    total_pendientes = solicitudes.filter(
        estado="PENDIENTE"
    ).count()

    total_revision = solicitudes.filter(
        estado="REVISION"
    ).count()

    total_respondidas = solicitudes.filter(
        estado="RESPONDIDO"
    ).count()

    total_cerradas = solicitudes.filter(
        estado="CERRADO"
    ).count()

    # ==============================================
    # CONTEXTO
    # ==============================================

    contexto = {

        "solicitudes": solicitudes,

        "total_solicitudes": total_solicitudes,
        "total_pendientes": total_pendientes,
        "total_revision": total_revision,
        "total_respondidas": total_respondidas,
        "total_cerradas": total_cerradas,

    }

    # ==============================================
    # RENDER
    # ==============================================

    return render(
        request,
        "mi_app_salud/centro_atencion_admin.html",
        contexto
    )

    # ==================================================
# DETALLE DE USUARIO JARVICE CORE
# ==================================================

@login_required
@requiere_rol("ADMIN")
def ver_usuario(request, usuario_id):

    # ==========================================
    # SEGURIDAD
    # ==========================================

    if not request.user.is_superuser:
        return redirect("inicio")

    # ==========================================
    # BUSCAR USUARIO
    # ==========================================

    usuario = get_object_or_404(
        User.objects.select_related("perfilusuario"),
        id=usuario_id
    )

    # ==========================================
    # RENDER
    # ==========================================

    return render(
        request,
        "mi_app_salud/ver_usuario.html",
        {
            "usuario": usuario,
        }
    )


# ==================================================
# CAMBIAR ESTADO DE USUARIO
# ==================================================

@login_required
@requiere_rol("ADMIN")
def cambiar_estado_usuario(request, usuario_id):

    usuario = get_object_or_404(
        User,
        id=usuario_id
    )

    if usuario.is_superuser:

        messages.error(
            request,
            "No se puede modificar el estado de un superusuario desde este panel."
        )

        return redirect(
            "ver_usuario",
            usuario_id=usuario.id
        )

    if request.method != "POST":

        return redirect(
            "ver_usuario",
            usuario_id=usuario.id
        )

    # ==========================================
    # ESTADO ANTERIOR
    # ==========================================

    estado_anterior = usuario.is_active

    # ==========================================
    # CAMBIAR ESTADO
    # ==========================================

    usuario.is_active = not usuario.is_active

    usuario.save(
        update_fields=["is_active"]
    )

    # ==========================================
    # DATOS DE AUDITORÍA
    # ==========================================

    accion = (
        "ACTIVAR"
        if usuario.is_active
        else "DESACTIVAR"
    )

    estado_anterior_texto = (
        "ACTIVO"
        if estado_anterior
        else "INACTIVO"
    )

    estado_nuevo_texto = (
        "ACTIVO"
        if usuario.is_active
        else "INACTIVO"
    )

    registrar_auditoria(
        request=request,
        accion=accion,
        modulo="ADMIN_USUARIOS",
        descripcion=(
            f"El administrador {request.user.username} "
            f"cambió el estado del usuario "
            f"{usuario.username}: "
            f"{estado_anterior_texto} → {estado_nuevo_texto}."
        ),
        datos_extra={
            "usuario_afectado_id": usuario.id,
            "usuario_afectado": usuario.username,
            "estado_anterior": estado_anterior_texto,
            "estado_nuevo": estado_nuevo_texto,
        }
    )

    # ==========================================
    # MENSAJE
    # ==========================================

    if usuario.is_active:

        messages.success(
            request,
            f"El usuario {usuario.username} fue activado correctamente."
        )

    else:

        messages.warning(
            request,
            f"El usuario {usuario.username} fue desactivado correctamente."
        )

    return redirect(
        "ver_usuario",
        usuario_id=usuario.id
    )


# ==================================================
# CAMBIAR ROL DE USUARIO
# ==================================================

@login_required
@requiere_rol("ADMIN")
def cambiar_rol_usuario(request, usuario_id):

    usuario = get_object_or_404(
        User.objects.select_related("perfilusuario"),
        id=usuario_id
    )

    # ==========================================
    # PROTEGER SUPERUSUARIOS
    # ==========================================

    if usuario.is_superuser:

        messages.error(
            request,
            "No se puede modificar el rol de un superusuario desde este panel."
        )

        return redirect(
            "ver_usuario",
            usuario_id=usuario.id
        )

    # ==========================================
    # SOLO POST
    # ==========================================

    if request.method != "POST":

        return redirect(
            "ver_usuario",
            usuario_id=usuario.id
        )

    # ==========================================
    # NUEVO ROL
    # ==========================================

    nuevo_rol = request.POST.get(
        "rol",
        ""
    ).strip()

    # ==========================================
    # ROLES VÁLIDOS
    # ==========================================

    roles_validos = {
        "ADMIN",
        "MEDICO",
        "ENFERMERIA",
        "PACIENTE",
        "FAMILIAR",
        "EMERGENCIA",
        "INSTITUCION",
    }

    if nuevo_rol not in roles_validos:

        messages.error(
            request,
            "El rol seleccionado no es válido."
        )

        return redirect(
            "ver_usuario",
            usuario_id=usuario.id
        )

    # ==========================================
    # PERFIL ACTUAL
    # ==========================================

    perfil = getattr(
        usuario,
        "perfilusuario",
        None
    )

    rol_anterior = (
        perfil.rol
        if perfil
        else None
    )

    # ==========================================
    # EVITAR REGISTRAR CAMBIOS INNECESARIOS
    # ==========================================

    if rol_anterior == nuevo_rol:

        messages.info(
            request,
            f"El usuario {usuario.username} ya posee el rol seleccionado."
        )

        return redirect(
            "ver_usuario",
            usuario_id=usuario.id
        )

    # ==========================================
    # CREAR O ACTUALIZAR PERFIL
    # ==========================================

    if perfil is None:

        perfil = PerfilUsuario.objects.create(
            usuario=usuario,
            rol=nuevo_rol
        )

    else:

        perfil.rol = nuevo_rol

        perfil.save(
            update_fields=["rol"]
        )

    # ==========================================
    # AUDITORÍA
    # ==========================================

    registrar_auditoria(
        request=request,
        accion="MODIFICAR",
        modulo="ADMIN_USUARIOS",
        descripcion=(
            f"El administrador {request.user.username} "
            f"cambió el rol del usuario "
            f"{usuario.username}: "
            f"{rol_anterior or 'SIN_ROL'} → {nuevo_rol}."
        ),
        datos_extra={
            "usuario_afectado_id": usuario.id,
            "usuario_afectado": usuario.username,
            "rol_anterior": rol_anterior,
            "rol_nuevo": nuevo_rol,
        }
    )

    # ==========================================
    # MENSAJE
    # ==========================================

    messages.success(
        request,
        f"El rol de {usuario.username} fue actualizado correctamente."
    )

    return redirect(
        "ver_usuario",
        usuario_id=usuario.id
    )

# ===# ==================================================
# GENERADOR DE QR DINÁMICO JARVICE
# ==================================================

def generar_qr_token(paciente, minutos=5):

    # --------------------------------------------------
    # INVALIDAR TOKENS ANTERIORES
    # --------------------------------------------------

    QRToken.objects.filter(
        paciente=paciente,
        activo=True
    ).update(
        activo=False
    )

    # --------------------------------------------------
    # GENERAR TOKEN CRIPTOGRÁFICAMENTE SEGURO
    # --------------------------------------------------

    token = secrets.token_urlsafe(48)

    # --------------------------------------------------
    # FECHA DE EXPIRACIÓN
    # --------------------------------------------------

    expira = timezone.now() + timezone.timedelta(
        minutes=minutos
    )

    # --------------------------------------------------
    # CREAR NUEVO TOKEN
    # --------------------------------------------------

    qr = QRToken.objects.create(
        paciente=paciente,
        token=token,
        expira=expira,
        activo=True
    )

    return qr


# ==========================================================
# 🆘 FICHA CLÍNICA DE EMERGENCIA MEDIANTE QR
# ==========================================================

def acceso_qr_emergencia(request, token):

    # ------------------------------------------------------
    # BUSCAR TOKEN
    # ------------------------------------------------------

    qr = get_object_or_404(
        QRToken,
        token=token
    )

    # ------------------------------------------------------
    # VALIDAR VIGENCIA
    # ------------------------------------------------------

    if not qr.esta_vigente():

        return render(
            request,
            "mi_app_salud/qr_acceso_denegado.html",
            {
                "mensaje": (
                    "Este código QR ya no es válido. "
                    "Solicite un nuevo código al paciente."
                )
            }
        )

    paciente = qr.paciente

    # ------------------------------------------------------
    # CREAR SOLICITUD DE ACCESO
    # ------------------------------------------------------
    # El acceso mediante QR NO requiere usuario.
    # Si existe una sesión iniciada, igualmente podemos
    # conservar el usuario para auditoría.

    usuario = (
        request.user
        if request.user.is_authenticated
        else None
    )

    tipo_acceso = "EMERGENCIA"

    acceso = AccesoClinico.objects.create(
        paciente=paciente,
        usuario=usuario,
        tipo_acceso=tipo_acceso,
        autorizado=False,
        motivo="Acceso mediante QR de emergencia",
        ip=request.META.get("REMOTE_ADDR")
    )

    # ------------------------------------------------------
    # MOSTRAR CONFIRMACIÓN
    # ------------------------------------------------------

    return render(
        request,
        "mi_app_salud/qr_confirmar_acceso.html",
        {
            "paciente": paciente,
            "qr": qr,
            "acceso": acceso,
            "perfil": (
                getattr(
                    request.user,
                    "perfilusuario",
                    None
                )
                if request.user.is_authenticated
                else None
            ),
        }
    )

# ==========================================================
# CONFIRMAR ACCESO A FICHA DE EMERGENCIA
# ==========================================================

def confirmar_acceso_qr(request, acceso_id):

    acceso = get_object_or_404(
        AccesoClinico,
        id=acceso_id
    )

    # ------------------------------------------------------
    # SEGURIDAD
    # ------------------------------------------------------
    # El acceso debe haber sido creado mediante QR.

    if acceso.tipo_acceso != "EMERGENCIA":

        return render(
            request,
            "mi_app_salud/qr_acceso_denegado.html",
            {
                "mensaje": "Solicitud de acceso no válida."
            }
        )

    # ------------------------------------------------------
    # CONFIRMAR
    # ------------------------------------------------------

    if request.method == "POST":

        acceso.autorizado = True
        acceso.fecha_autorizacion = timezone.now()

        acceso.save(
            update_fields=[
                "autorizado",
                "fecha_autorizacion",
            ]
        )

        # --------------------------------------------------
        # AUDITORÍA
        # --------------------------------------------------

        registrar_auditoria(
            request=request,
            accion="ACCESO_QR_EMERGENCIA",
            modulo="SEGURIDAD_CLINICA",
            descripcion=(
                f"Acceso mediante QR a ficha de emergencia "
                f"del paciente {acceso.paciente}"
            ),
            datos_extra={
                "paciente_id": acceso.paciente.id,
                "usuario_id": (
                    acceso.usuario.id
                    if acceso.usuario
                    else None
                ),
                "rol": acceso.tipo_acceso,
                "acceso_id": acceso.id,
                "metodo": "QR",
            }
        )

        return redirect(
            "ficha_emergencia_qr",
            acceso_id=acceso.id
        )

    # ------------------------------------------------------
    # MOSTRAR CONFIRMACIÓN
    # ------------------------------------------------------

    return render(
        request,
        "mi_app_salud/qr_confirmar_acceso.html",
        {
            "paciente": acceso.paciente,
            "acceso": acceso,
            "perfil": (
                getattr(
                    request.user,
                    "perfilusuario",
                    None
                )
                if request.user.is_authenticated
                else None
            ),
        }
    )


# ==========================================================
# FICHA CLÍNICA DE EMERGENCIA
# ==========================================================

def ficha_emergencia_qr(request, acceso_id):

    acceso = get_object_or_404(
        AccesoClinico,
        id=acceso_id
    )

    # ------------------------------------------------------
    # SEGURIDAD
    # ------------------------------------------------------

    if acceso.tipo_acceso != "EMERGENCIA":

        return render(
            request,
            "mi_app_salud/qr_acceso_denegado.html",
            {
                "mensaje": "Acceso no autorizado."
            }
        )

    if not acceso.autorizado:

        return render(
            request,
            "mi_app_salud/qr_acceso_denegado.html",
            {
                "mensaje": (
                    "El acceso a la ficha clínica "
                    "todavía no fue autorizado."
                )
            }
        )

    paciente = acceso.paciente

    # ------------------------------------------------------
    # MEDICACIÓN ACTUAL
    # ------------------------------------------------------

    medicaciones = Medicacion.objects.filter(
        paciente=paciente,
        activo=True
    ).order_by(
        "horario"
    )

    # ------------------------------------------------------
    # ÚLTIMO SIGNO VITAL
    # ------------------------------------------------------

    ultimo_signo_vital = SignoVital.objects.filter(
        paciente=paciente
    ).order_by(
        "-fecha"
    ).first()

    # ------------------------------------------------------
    # ÚLTIMO ESTADO
    # ------------------------------------------------------

    ultimo_estado = RegistroSalud.objects.filter(
        paciente=paciente
    ).order_by(
        "-fecha"
    ).first()

    # ------------------------------------------------------
    # EVOLUCIÓN MÉDICA MÁS RECIENTE
    # ------------------------------------------------------

    ultima_evolucion = EvolucionMedica.objects.filter(
        paciente=paciente
    ).order_by(
        "-fecha"
    ).first()

    # ------------------------------------------------------
    # CONTEXTO
    # ------------------------------------------------------

    contexto = {
        "paciente": paciente,
        "medicaciones": medicaciones,
        "ultimo_signo_vital": ultimo_signo_vital,
        "ultimo_estado": ultimo_estado,
        "ultima_evolucion": ultima_evolucion,
        "acceso": acceso,
    }

    return render(
        request,
        "mi_app_salud/ficha_emergencia_qr.html",
        contexto
    )

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



from .models import (
    PerfilUsuario,
    Paciente,
    RegistroSalud,
    Recordatorio,
    Medicacion,
    EvolucionMedica,
    EstudioMedico,
    SolicitudEstudio
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


        if User.objects.filter(username=username).exists():

            messages.error(
                request,
                "El usuario ya existe"
            )

            return redirect("registro")


        usuario = User.objects.create_user(
            username=username,
            email=email,
            password=password
        )


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
# LOGIN USUARIO
# ==================================================

def login_view(request):

    if request.method == "POST":

        username = request.POST.get("username")
        password = request.POST.get("password")

        usuario = authenticate(
            request,
            username=username,
            password=password
        )

        if usuario is not None:

            login(
                request,
                usuario
            )

            return redirect(
                "bienvenida_rol"
            )

        messages.error(
            request,
            "Usuario o contraseña incorrectos"
        )


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

@login_required
def inicio(request):

    perfil = get_object_or_404(
    PerfilUsuario,
    usuario=request.user
)

    pacientes = Paciente.objects.all()

    return render(
        request,
        "mi_app_salud/inicio.html",
        {
            "pacientes": pacientes,
            "rol": perfil.rol,
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
        return redirect("inicio")


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

# ==================================================
# PANEL MÉDICO
# ==================================================

from django.db.models import Q


@login_required
def panel_medico(request):

    buscar = request.GET.get("buscar", "")

    pacientes = Paciente.objects.all()

    if buscar:

        palabras = buscar.split()

    for palabra in palabras:

        pacientes = pacientes.filter(
            Q(nombre__icontains=palabra) |
            Q(apellido__icontains=palabra) |
            Q(historia_clinica__icontains=palabra) |
            Q(dni__icontains=palabra)
        )

    return render(
        request,
        "mi_app_salud/panel_medico.html",
        {
            "pacientes": pacientes,
            "buscar": buscar,
        }
    )

@login_required
def panel_enfermeria(request):

    return render(
        request,
        "enfermeria/panel.html",
        {
            "prueba": "Panel enfermería conectado correctamente"
        }
    )



@login_required
def panel_paciente(request):

    return render(
        request,
        "paciente/panel.html"
    )



@login_required
def panel_emergencia(request):

    return render(
        request,
        "emergencia/panel.html"
    )
    
    # ==================================================
# PANEL INSTITUCIÓN
# ==================================================

@login_required
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

@login_required
def crear_paciente(request):

    if request.method == "POST":

        nombre = request.POST.get("nombre")
        apellido = request.POST.get("apellido")
        edad = request.POST.get("edad")


        if not nombre or not apellido or not edad:

            messages.error(
                request,
                "Complete todos los campos"
            )

            return redirect("crear_paciente")


        paciente = Paciente.objects.create(

            nombre=nombre,

            apellido=apellido,

            edad=edad

        )


        paciente.historia_clinica = f"HC{paciente.id:06d}"

        paciente.save()


        messages.success(
            request,
            "Paciente creado correctamente"
        )


        return redirect("inicio")


    return render(
        request,
        "mi_app_salud/crear_paciente.html"
    )
# ==================================================
# LISTADO PACIENTES
# ==================================================

@login_required
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
# HISTORIAL PACIENTE
# ==================================================

@login_required
def historial_paciente(request, paciente_id):

    paciente = get_object_or_404(
        Paciente,
        id=paciente_id
    )


    registros = RegistroSalud.objects.filter(
        paciente=paciente
    ).order_by("-fecha")


    recordatorios = Recordatorio.objects.filter(
        paciente=paciente
    ).order_by("-fecha")


    medicaciones = Medicacion.objects.filter(
        paciente=paciente
    )


    evoluciones = EvolucionMedica.objects.filter(
        paciente=paciente
    ).order_by("-fecha")


    estudios = EstudioMedico.objects.filter(
        paciente=paciente
    ).order_by("-fecha")


    # SOLICITUDES DE ESTUDIOS DEL MÉDICO

    solicitudes_estudios = SolicitudEstudio.objects.filter(
        paciente=paciente
    ).order_by("-fecha_solicitud")



    # ==========================================
    # ANALISIS RIESGO JARVICE
    # ==========================================

    riesgo = "BAJO"
    color_riesgo = "verde"


    ultimo_registro = registros.first()


    if ultimo_registro:

        if ultimo_registro.estado == "CRITICO":

            riesgo = "CRITICO"
            color_riesgo = "rojo"


        elif ultimo_registro.estado in [
            "DOLOR",
            "CANSADO"
        ]:

            riesgo = "ATENCION"
            color_riesgo = "amarillo"



        for medicamento in medicaciones:

            if not medicamento.activo:

                riesgo = "ATENCION"
                color_riesgo = "amarillo"

    # ==========================================
    # ÚLTIMO ESTADO PARA JARVICE AI
    # ==========================================

    ultimo_estado = RegistroSalud.objects.filter(
        paciente=paciente
    ).order_by("-fecha").first()


    return render(
        request,
        "mi_app_salud/historial_paciente.html",
        {
            "paciente": paciente,
            "registros": registros,
            "recordatorios": recordatorios,
            "medicaciones": medicaciones,
            "evoluciones": evoluciones,
            "solicitudes_estudios": solicitudes_estudios,
            "ultimo_estado": ultimo_estado,
        }
    )


# ==================================================
# CREAR EVOLUCIÓN MÉDICA
# ==================================================

@login_required
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


@login_required
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
# RECORDATORIOS
# ==================================================

@login_required
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



# ==================================================
# SEGURIDAD
# ==================================================

@login_required
def seguridad(request):
    return render(
        request,
        "mi_app_salud/seguridad.html"
    )

# ==================================================
# API PACIENTES
# ==================================================

@login_required
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



# ==================================================
# API CAMBIAR ESTADO SALUD
# ==================================================

@login_required
def api_cambiar_estado(request, paciente_id):

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
            "paciente": paciente.nombre,
            "estado": estado
        }
    )



# ==================================================
# CONTACTOS EMERGENCIA
# ==================================================

@login_required
def segundo_contacto(request):

    return JsonResponse(
        {
            "ok": True,
            "mensaje": "Segundo contacto notificado"
        }
    )



@login_required
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

@login_required
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

@login_required
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


@login_required
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

@login_required
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

@login_required
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

@login_required
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

@login_required
def sueno(request):

    return render(
        request,
        "mi_app_salud/sueno.html"
    )



@login_required
def reportes(request):

    return render(
        request,
        "mi_app_salud/reportes.html"
    )



@login_required
def configuracion(request):

    return render(
        request,
        "mi_app_salud/configuracion.html"
    )



# ==================================================
# LOGOUT
# ==================================================

def salir(request):
    logout(request)
    return redirect("login")

# ==================================================
# EMERGENCIA
# ==================================================

@login_required
def emergencia(request):

    return render(
        request,
        "mi_app_salud/emergencia.html"
    )
# ==================================================
# PANEL FAMILIAR
# ==================================================

@login_required
def panel_familiar(request):

    return render(
        request,
        "mi_app_salud/panel_familiar.html"
    )
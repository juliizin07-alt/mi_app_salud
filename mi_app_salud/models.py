from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone


# ============================
# USUARIOS JARVICE
# ============================

class PerfilUsuario(models.Model):

    ROLES = (

    ("ADMIN", "Administrador"),

    ("MEDICO", "Médico"),

    ("ENFERMERIA", "Enfermería"),

    ("PACIENTE", "Paciente"),

    ("FAMILIAR", "Familiar"),

    ("EMERGENCIA", "Emergencias"),

    ("INSTITUCION", "Institución"),


)


    usuario = models.OneToOneField(
        User,
        on_delete=models.CASCADE
    )


    rol = models.CharField(
        max_length=20,
        choices=ROLES,
        default="PACIENTE"
    )


    nombre = models.CharField(
        max_length=100,
        blank=True
    )


    apellido = models.CharField(
        max_length=100,
        blank=True
    )


    matricula = models.CharField(
        max_length=50,
        blank=True,
        null=True
    )


    especialidad = models.CharField(
        max_length=100,
        blank=True,
        null=True
    )


    telefono = models.CharField(
        max_length=30,
        blank=True,
        null=True
    )


    def __str__(self):

        return f"{self.usuario.username} - {self.rol}"



# ============================
# PACIENTES
# ============================
class Paciente(models.Model):

    SEXOS = [
        ("F", "Femenino"),
        ("M", "Masculino"),
        ("O", "Otro"),
    ]

    usuario = models.OneToOneField(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="paciente"
    )
    enfermera_asignada = models.ForeignKey(
        PerfilUsuario,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="pacientes_asignados",
        limit_choices_to={"rol": "ENFERMERIA"},
    )

    nombre = models.CharField(max_length=100)

    apellido = models.CharField(max_length=100)

    historia_clinica = models.CharField(
        max_length=20,
        unique=True,
        blank=True,
        null=True
    )

    dni = models.CharField(
        max_length=20,
        unique=True,
        blank=True,
        null=True
    )

    edad = models.PositiveIntegerField()

    fecha_nacimiento = models.DateField(
        blank=True,
        null=True
    )

    sexo = models.CharField(
        max_length=1,
        choices=SEXOS,
        blank=True
    )

    grupo_sanguineo = models.CharField(
        max_length=5,
        blank=True
    )

    peso = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        blank=True,
        null=True
    )

    altura = models.DecimalField(
        max_digits=4,
        decimal_places=2,
        blank=True,
        null=True
    )

    alergias = models.TextField(
        blank=True
    )

    enfermedades = models.TextField(
        blank=True
    )

    telefono = models.CharField(
        max_length=30,
        blank=True
    )

    direccion = models.TextField(
        blank=True
    )

    contacto_emergencia = models.CharField(
        max_length=150,
        blank=True
    )

    telefono_emergencia = models.CharField(
        max_length=30,
        blank=True
    )

    contacto_emergencia_2 = models.CharField(
        max_length=150,
        blank=True
    )

    telefono_emergencia_2 = models.CharField(
        max_length=30,
        blank=True
    )

    contacto_emergencia_3 = models.CharField(
        max_length=150,
        blank=True
    )

    telefono_emergencia_3 = models.CharField(
        max_length=30,
        blank=True
    )

    medico_cabecera = models.CharField(
        max_length=150,
        blank=True
    )

    observaciones = models.TextField(
        blank=True
    )

    fecha_creacion = models.DateTimeField(
        auto_now_add=True
    )

    def __str__(self):
        return f"{self.nombre} {self.apellido}"

# ============================
# DISPOSITIVOS JARVICE
# ============================

class Dispositivo(models.Model):

    TIPOS = [
        ("SMARTWATCH", "Smartwatch"),
        ("SENSOR", "Sensor"),
    ]

    paciente = models.ForeignKey(
        Paciente,
        on_delete=models.CASCADE,
        related_name="dispositivos"
    )

    nombre = models.CharField(
        max_length=100
    )

    tipo = models.CharField(
        max_length=20,
        choices=TIPOS,
        default="SMARTWATCH"
    )

    identificador = models.CharField(
        max_length=100,
        unique=True
    )

    activo = models.BooleanField(
        default=True
    )

    conectado = models.BooleanField(
        default=False
    )

    bateria = models.PositiveIntegerField(
        default=100
    )

    ultima_conexion = models.DateTimeField(
        null=True,
        blank=True
    )

    fecha_alta = models.DateTimeField(
        auto_now_add=True
    )

    def __str__(self):
        return f"{self.nombre} - {self.paciente.nombre} {self.paciente.apellido}"

# ============================
# REGISTROS DE SALUD
# ============================

class RegistroSalud(models.Model):


    ESTADOS = [
        ("OK", "OK"),
        ("CANSADO", "CANSADO"),
        ("DOLOR", "DOLOR"),
        ("CRITICO", "CRITICO"),
    ]


    paciente = models.ForeignKey(
        Paciente,
        on_delete=models.CASCADE,
        related_name="registros"
    )


    estado_fisico = models.CharField(
        max_length=20,
        choices=ESTADOS,
        default="OK"
    )


    estado_emocional = models.CharField(
        max_length=50,
        default="NEUTRO"
    )


    estado = models.CharField(
        max_length=20,
        default="OK"
    )


    fecha = models.DateTimeField(
        auto_now_add=True
    )


    def __str__(self):

        return f"{self.paciente.nombre} - {self.estado}"



# ============================
# RECORDATORIOS
# ============================

class Recordatorio(models.Model):


    paciente = models.ForeignKey(
        Paciente,
        on_delete=models.CASCADE,
        related_name="recordatorios"
    )


    texto = models.CharField(
        max_length=255
    )


    fecha = models.DateTimeField(
        auto_now_add=True
    )


    hecho = models.BooleanField(
        default=False
    )


    def __str__(self):

        return f"{self.paciente.nombre} - {self.texto}"

# ============================
# MEDICACIÓN JARVICE
# ============================

class Medicacion(models.Model):

    paciente = models.ForeignKey(
        Paciente,
        on_delete=models.CASCADE,
        related_name="medicaciones"
    )

    nombre = models.CharField(max_length=100)

    dosis = models.CharField(max_length=50)

    horario = models.TimeField()

    activo = models.BooleanField(default=True)

    tomado = models.BooleanField(default=False)

    fecha_ultima_toma = models.DateTimeField(
        null=True,
        blank=True
    )

    confirmado_por = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True
    )

    def __str__(self):
        return self.nombre


# ==================================================

# EVOLUCIÓN MÉDICA

# ==================================================

class EvolucionMedica(models.Model):

    paciente = models.ForeignKey(
        Paciente,
        on_delete=models.CASCADE,
        related_name="evoluciones"
    )

    usuario = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="evoluciones_creadas"
    )

    fecha = models.DateTimeField(
        auto_now_add=True
    )

    descripcion = models.TextField()

    diagnostico = models.TextField(
        blank=True,
        null=True
    )

    indicaciones = models.TextField(
        blank=True,
        null=True
    )

    def __str__(self):
        return f"Evolución de {self.paciente.nombre} - {self.fecha.date()}"
# ==================================================
# ESTUDIOS MÉDICOS REALIZADOS
# ==================================================

class EstudioMedico(models.Model):

    paciente = models.ForeignKey(
        Paciente,
        on_delete=models.CASCADE,
        related_name="estudios"
    )

    fecha = models.DateField()

    tipo = models.CharField(
        max_length=100
    )

    nombre = models.CharField(
        max_length=200
    )

    institucion = models.CharField(
        max_length=150,
        blank=True
    )

    profesional = models.CharField(
        max_length=150,
        blank=True
    )

    observaciones = models.TextField(
        blank=True,
        null=True
    )

    archivo = models.FileField(
        upload_to="estudios/",
        blank=True,
        null=True
    )

    def __str__(self):
        return f"{self.tipo} - {self.paciente.nombre}"


# ==================================================

# SOLICITUDES DE ESTUDIOS

# ==================================================

class SolicitudEstudio(models.Model):

    ESTADOS = [
        ("PENDIENTE", "Pendiente"),
        ("REALIZADO", "Realizado"),
        ("CANCELADO", "Cancelado"),
    ]

    paciente = models.ForeignKey(
        Paciente,
        on_delete=models.CASCADE,
        related_name="solicitudes_estudios"
    )

    medico = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True
    )

    estudio = models.CharField(
        max_length=150
    )

    motivo = models.TextField(
        blank=True
    )

    fecha_solicitud = models.DateTimeField(
        auto_now_add=True
    )

    archivo_informe = models.FileField(
        upload_to="estudios/",
        null=True,
        blank=True
    )

    informe = models.TextField(
        blank=True,
        null=True
    )

    fecha_realizacion = models.DateTimeField(
        null=True,
        blank=True
    )

    estado = models.CharField(
        max_length=20,
        choices=ESTADOS,
        default="PENDIENTE"
    )

    def __str__(self):
        return f"{self.estudio} - {self.paciente.nombre}"
    # ==================================================
# AUDITORÍA JARVICE CORE
# ==================================================

class AuditoriaJarvice(models.Model):

    TIPOS_ACCION = [
        ("LOGIN", "Inicio de sesión"),
        ("LOGOUT", "Cierre de sesión"),
        ("CREAR", "Creación"),
        ("MODIFICAR", "Modificación"),
        ("ELIMINAR", "Eliminación"),
        ("ACTIVAR", "Activación"),
        ("DESACTIVAR", "Desactivación"),
        ("EMERGENCIA", "Emergencia"),
        ("SEGURIDAD", "Seguridad"),
        ("SISTEMA", "Sistema"),
    ]

    usuario = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="auditorias_jarvice"
    )

    accion = models.CharField(
        max_length=20,
        choices=TIPOS_ACCION
    )

    modulo = models.CharField(
        max_length=100,
        blank=True
    )

    descripcion = models.TextField()

    fecha = models.DateTimeField(
        auto_now_add=True
    )

    ip = models.GenericIPAddressField(
        null=True,
        blank=True
    )

    datos_extra = models.JSONField(
        null=True,
        blank=True
    )

    def __str__(self):
        usuario = (
            self.usuario.username
            if self.usuario
            else "Sistema"
        )

        return f"{usuario} - {self.accion} - {self.fecha}"
    # ==================================================
# SIGNOS VITALES JARVICE
# ==================================================

class SignoVital(models.Model):

    ORIGENES = [
        ("MANUAL", "Carga manual"),
        ("SMARTWATCH", "Smartwatch"),
        ("SENSOR", "Sensor"),
        ("SISTEMA", "Sistema"),
    ]

    paciente = models.ForeignKey(
        Paciente,
        on_delete=models.CASCADE,
        related_name="signos_vitales"
    )

    frecuencia_cardiaca = models.PositiveIntegerField(
        null=True,
        blank=True
    )

    saturacion_oxigeno = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        null=True,
        blank=True
    )

    temperatura = models.DecimalField(
        max_digits=4,
        decimal_places=1,
        null=True,
        blank=True
    )

    presion_arterial = models.CharField(
        max_length=20,
        blank=True
    )

    estado_emocional = models.CharField(
        max_length=50,
        blank=True
    )

    origen = models.CharField(
        max_length=20,
        choices=ORIGENES,
        default="MANUAL"
    )

    observaciones = models.TextField(
        blank=True
    )

    fecha = models.DateTimeField(
        auto_now_add=True
    )

    def __str__(self):
        return f"Signos vitales - {self.paciente.nombre} {self.paciente.apellido} - {self.fecha}"
    # ==================================================
# QR DINÁMICO JARVICE
# ==================================================

class QRToken(models.Model):

    paciente = models.ForeignKey(
        Paciente,
        on_delete=models.CASCADE,
        related_name="qr_tokens"
    )

    token = models.CharField(
        max_length=128,
        unique=True
    )

    creado = models.DateTimeField(
        auto_now_add=True
    )

    expira = models.DateTimeField()

    activo = models.BooleanField(
        default=True
    )

    def __str__(self):
        return f"QR {self.paciente} - {self.token[:12]}"

    def esta_vigente(self):

        return (
            self.activo
            and timezone.now() < self.expira
        )


# ==================================================
# ACCESO A HISTORIA CLÍNICA MEDIANTE QR
# ==================================================

class AccesoClinico(models.Model):

    TIPOS_ACCESO = [
        ("ENFERMERIA", "Enfermería"),
        ("MEDICO", "Médico"),
        ("EMERGENCIA", "Emergencia"),
        ("ADMIN", "Administrador"),
    ]

    paciente = models.ForeignKey(
        Paciente,
        on_delete=models.CASCADE,
        related_name="accesos_clinicos"
    )

    usuario = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="accesos_clinicos"
    )

    tipo_acceso = models.CharField(
        max_length=20,
        choices=TIPOS_ACCESO
    )

    autorizado = models.BooleanField(
        default=False
    )

    fecha_solicitud = models.DateTimeField(
        auto_now_add=True
    )

    fecha_autorizacion = models.DateTimeField(
        null=True,
        blank=True
    )

    motivo = models.TextField(
        blank=True
    )

    ip = models.GenericIPAddressField(
        null=True,
        blank=True
    )

    def __str__(self):

        usuario = (
            self.usuario.username
            if self.usuario
            else "Sin usuario"
        )

        return (
            f"{usuario} †’ "
            f"{self.paciente} †’ "
            f"{self.tipo_acceso}"
        )


class EvolucionEnfermeria(models.Model):
    ESTADOS = [
        ("ESTABLE", "Estable"),
        ("OBSERVACION", "En observación"),
        ("DOLOR", "Dolor"),
        ("CRITICO", "Crítico"),
    ]

    paciente = models.ForeignKey(
        Paciente,
        on_delete=models.CASCADE,
        related_name="evoluciones_enfermeria"
    )

    usuario = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="evoluciones_enfermeria_creadas"
    )

    fecha = models.DateTimeField(auto_now_add=True)

    estado = models.CharField(
        max_length=20,
        choices=ESTADOS,
        default="ESTABLE"
    )

    observaciones = models.TextField()

    intervenciones = models.TextField(
        blank=True
    )

    incidentes = models.TextField(
        blank=True
    )

    def __str__(self):
        usuario = self.usuario.username if self.usuario else "Sin usuario"

        return (
            f"Evolución de enfermería - "
            f"{self.paciente.nombre} {self.paciente.apellido} - "
            f"{usuario} - {self.fecha}"
        )



# ==================================================
# CENTRO DE ATENCION JARVICE
# ==================================================

class SolicitudUsuario(models.Model):

    TIPOS = [
        ("SUGERENCIA", "Sugerencia"),
        ("OPINION", "Opinión"),
        ("PROBLEMA", "Problema técnico"),
        ("RECLAMO", "Queja / Reclamo"),
        ("ATENCION", "Atención al usuario"),
    ]

    ESTADOS = [
        ("PENDIENTE", "Pendiente"),
        ("REVISION", "En revisión"),
        ("RESPONDIDO", "Respondido"),
        ("CERRADO", "Cerrado"),
    ]

    usuario = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="solicitudes_jarvice"
    )

    tipo = models.CharField(
        max_length=20,
        choices=TIPOS
    )

    asunto = models.CharField(
        max_length=200
    )

    mensaje = models.TextField()

    estado = models.CharField(
        max_length=20,
        choices=ESTADOS,
        default="PENDIENTE"
    )

    respuesta_admin = models.TextField(
        blank=True
    )

    fecha_creacion = models.DateTimeField(
        auto_now_add=True
    )

    fecha_actualizacion = models.DateTimeField(
        auto_now=True
    )

    def __str__(self):
        return (
            f"{self.get_tipo_display()} - "
            f"{self.asunto} - "
            f"{self.usuario.username}"
        )
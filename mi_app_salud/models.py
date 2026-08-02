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

    nombre = models.CharField(max_length=100)

    apellido = models.CharField(max_length=100)

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
# MEDICACION JARVICE
# ============================

class Medicacion(models.Model):


    paciente = models.ForeignKey(
        Paciente,
        on_delete=models.CASCADE,
        related_name="medicaciones"
    )


    nombre = models.CharField(
        max_length=100
    )


    dosis = models.CharField(
        max_length=50
    )


    horario = models.TimeField()


    activo = models.BooleanField(
        default=True
    )


    tomado = models.BooleanField(
        default=False
    )


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
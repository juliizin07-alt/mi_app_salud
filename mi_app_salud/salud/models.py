from django.db import models
from datetime import date


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

class RegistroSalud(models.Model):
    paciente = models.ForeignKey(Paciente, on_delete=models.CASCADE, related_name="registros")
    fecha = models.DateTimeField(auto_now_add=True)

    # 🧠 EMOCIONAL
    ESTADO_EMOCIONAL = [
        ("CALMA", "Calma"),
        ("ANSIEDAD", "Ansiedad"),
        ("ESTRES", "Estrés"),
        ("TRISTEZA", "Tristeza"),
    ]

    estado_emocional = models.CharField(
        max_length=20,
        choices=ESTADO_EMOCIONAL,
        default="CALMA"
    )

    # ❤️ FÍSICO
    ESTADO_FISICO = [
        ("ENERGIA", "Energía"),
        ("CANSADO", "Cansado"),
        ("DOLOR", "Dolor"),
        ("CRITICO", "Crítico"),
    ]

    estado_fisico = models.CharField(
        max_length=20,
        choices=ESTADO_FISICO,
        default="ENERGIA"
    )

    # 🚦 SEMÁFORO AUTOMÁTICO
    def semaforo(self):
        if self.estado_emocional in ["ANSIEDAD", "ESTRES"] or self.estado_fisico == "CRITICO":
            return "ROJO"
        elif self.estado_fisico == "CANSADO":
            return "AMARILLO"
        return "VERDE"

    def __str__(self):
        return f"{self.paciente.nombre} - {self.estado_emocional} / {self.estado_fisico}"
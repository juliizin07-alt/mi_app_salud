from django.db import models
from django.utils import timezone


class Paciente(models.Model):
    nombre = models.CharField(max_length=100)
    apellido = models.CharField(max_length=100, blank=True, null=True)
    edad = models.IntegerField(blank=True, null=True)

    def __str__(self):
        return f"{self.nombre} {self.apellido or ''}".strip()


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

    estado_fisico = models.CharField(max_length=20, choices=ESTADOS)
    estado_emocional = models.CharField(max_length=50, default="NEUTRO")
    fecha = models.DateTimeField(auto_now_add=True)
    estado = models.CharField(max_length=20, default="OK")

    def __str__(self):
        return f"{self.paciente.nombre} - {self.estado_fisico}"


class Recordatorio(models.Model):
    paciente = models.ForeignKey(
        Paciente,
        on_delete=models.CASCADE,
        related_name="recordatorios"
    )
    texto = models.CharField(max_length=255)
    fecha = models.DateTimeField(auto_now_add=True)
    hecho = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.paciente.nombre} - {self.texto}"
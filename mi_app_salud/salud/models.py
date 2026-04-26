from django.db import models
from datetime import date


class Paciente(models.Model):
    nombre = models.CharField(max_length=100)
    fecha_nacimiento = models.DateField()
    dni = models.CharField(max_length=20)

    def edad(self):
        today = date.today()
        return today.year - self.fecha_nacimiento.year - (
            (today.month, today.day) < (self.fecha_nacimiento.month, self.fecha_nacimiento.day)
        )

    def __str__(self):
        return self.nombre


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
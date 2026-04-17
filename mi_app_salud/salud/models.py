from django.db import models

class Paciente(models.Model):
    nombre = models.CharField(max_length=100)
    fecha_nacimiento = models.DateField()
    dni = models.CharField(max_length=20)

    def __str__(self):
        return self.nombre


class RegistroSalud(models.Model):

    ESTADOS = [
        ("OK", "Normal"),
        ("CANSADO", "Cansado"),
        ("DOLOR", "Dolor"),
        ("CRITICO", "Crítico"),
    ]

    paciente = models.ForeignKey(Paciente, on_delete=models.CASCADE, related_name="registros")
    fecha = models.DateTimeField(auto_now_add=True)
    estado = models.CharField(max_length=20, choices=ESTADOS)

    def __str__(self):
        return f"{self.paciente.nombre} - {self.estado}"
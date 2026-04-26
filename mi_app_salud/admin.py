from django.contrib import admin
from .models import Paciente, RegistroSalud, Recordatorio


# 🧑‍⚕️ PACIENTE
@admin.register(Paciente)
class PacienteAdmin(admin.ModelAdmin):
    list_display = ("nombre", "apellido", "edad")
    search_fields = ("nombre", "apellido")
    list_filter = ("edad",)


# 📋 REGISTROS DE SALUD
@admin.register(RegistroSalud)
class RegistroSaludAdmin(admin.ModelAdmin):
    list_display = ("paciente", "estado_fisico", "estado_emocional", "fecha")
    list_filter = ("estado_fisico", "fecha")
    search_fields = ("paciente__nombre", "paciente__apellido")


# ⏰ RECORDATORIOS (si ya los estás usando)
@admin.register(Recordatorio)
class RecordatorioAdmin(admin.ModelAdmin):
    list_display = ("paciente", "texto", "hecho", "fecha")
    list_filter = ("hecho",)
    search_fields = ("texto",)
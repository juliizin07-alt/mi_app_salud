from django.contrib import admin
from .models import Paciente, RegistroSalud


@admin.register(Paciente)
class PacienteAdmin(admin.ModelAdmin):
    list_display = ('nombre', 'apellido', 'edad')


@admin.register(RegistroSalud)
class RegistroSaludAdmin(admin.ModelAdmin):
    list_display = ('paciente', 'estado_fisico', 'estado_emocional', 'fecha')
    
    from django.contrib import admin
from .models import Paciente, RegistroSalud, Recordatorio

admin.site.register(Paciente)
admin.site.register(RegistroSalud)
admin.site.register(Recordatorio)
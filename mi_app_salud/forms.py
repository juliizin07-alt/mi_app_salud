from django import forms
from .models import Paciente, SolicitudUsuario


class PacienteForm(forms.ModelForm):

    class Meta:

        model = Paciente

        fields = [
            "nombre",
            "apellido",
            "dni",
            "fecha_nacimiento",
            "sexo",
            "grupo_sanguineo",
            "peso",
            "altura",
            "alergias",
            "enfermedades",
            "antecedentes_salud_mental",
            "telefono",
            "direccion",
            "contacto_emergencia",
            "telefono_emergencia",
            "contacto_emergencia_2",
            "telefono_emergencia_2",
            "contacto_emergencia_3",
            "telefono_emergencia_3",
            "medico_cabecera",
            "observaciones",
        ]

        widgets = {

            "nombre": forms.TextInput(attrs={
                "class": "campo",
                "placeholder": "Nombre"
            }),

            "apellido": forms.TextInput(attrs={
                "class": "campo",
                "placeholder": "Apellido"
            }),

            "dni": forms.TextInput(attrs={
                "class": "campo",
                "placeholder": "DNI"
            }),

            "fecha_nacimiento": forms.DateInput(
                attrs={
                    "class": "campo",
                    "type": "date"
                }
            ),

            "sexo": forms.Select(attrs={
                "class": "campo"
            }),

            "grupo_sanguineo": forms.TextInput(attrs={
                "class": "campo",
                "placeholder": "Ej: O+, A+, B-"
            }),

            "peso": forms.NumberInput(attrs={
                "class": "campo",
                "placeholder": "Peso en kg",
                "step": "0.01"
            }),

            "altura": forms.NumberInput(attrs={
                "class": "campo",
                "placeholder": "Altura en metros",
                "step": "0.01"
            }),

            "alergias": forms.Textarea(attrs={
                "class": "campo",
                "placeholder": "Alergias conocidas",
                "rows": 3
            }),

            "enfermedades": forms.Textarea(attrs={
                "class": "campo",
                "placeholder": "Enfermedades o antecedentes relevantes",
                "rows": 3
            }),

            "antecedentes_salud_mental": forms.Textarea(attrs={
            "class": "campo",
            "placeholder": "Antecedentes de salud mental relevantes",
            "rows": 3
                }),

            "telefono": forms.TextInput(attrs={
                "class": "campo",
                "placeholder": "TelÃ©fono"
            }),

            "direccion": forms.Textarea(attrs={
                "class": "campo",
                "placeholder": "DirecciÃ³n",
                "rows": 2
            }),

            "contacto_emergencia": forms.TextInput(attrs={
                "class": "campo",
                "placeholder": "Nombre del contacto"
            }),

            "telefono_emergencia": forms.TextInput(attrs={
                "class": "campo",
                "placeholder": "TelÃ©fono de emergencia"
            }),

                        "contacto_emergencia_2": forms.TextInput(attrs={
                "class": "campo",
                "placeholder": "Nombre del segundo contacto"
            }),

            "telefono_emergencia_2": forms.TextInput(attrs={
                "class": "campo",
                "placeholder": "TelÃ©fono del segundo contacto"
            }),

            "contacto_emergencia_3": forms.TextInput(attrs={
                "class": "campo",
                "placeholder": "Nombre del tercer contacto"
            }),

            "telefono_emergencia_3": forms.TextInput(attrs={
                "class": "campo",
                "placeholder": "TelÃ©fono del tercer contacto"
            }),

            "medico_cabecera": forms.TextInput(attrs={
                "class": "campo",
                "placeholder": "MÃ©dico de cabecera"
            }),

            "observaciones": forms.Textarea(attrs={
                "class": "campo",
                "placeholder": "Observaciones clÃ­nicas",
                "rows": 4
            }),
        }

    def clean_dni(self):

        dni = self.cleaned_data.get("dni")

        if dni:
            dni = dni.strip()

            if Paciente.objects.filter(dni=dni).exists():
                raise forms.ValidationError(
                    "Ya existe un paciente registrado con este DNI."
                )

        return dni

# ==================================================
# FORMULARIO CENTRO DE ATENCION JARVICE
# ==================================================

class SolicitudUsuarioForm(forms.ModelForm):

    class Meta:
        model = SolicitudUsuario

        fields = [
            "tipo",
            "asunto",
            "mensaje",
        ]

        widgets = {
            "tipo": forms.Select(
                attrs={
                    "class": "campo"
                }
            ),

            "asunto": forms.TextInput(
                attrs={
                    "class": "campo",
                    "placeholder": "Â¿Sobre quÃ© querÃ©s comunicarte?",
                    "maxlength": "200",
                }
            ),

            "mensaje": forms.Textarea(
                attrs={
                    "class": "campo",
                    "placeholder": "Contanos tu sugerencia, opiniÃ³n, problema, reclamo o consulta...",
                    "rows": 6,
                }
            ),
        }

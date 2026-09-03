import os

from django.core.management.base import BaseCommand
from django.contrib.auth.models import User

from mi_app_salud.models import PerfilUsuario


class Command(BaseCommand):

    help = "Inicializa el administrador principal de Jarvice"

    def handle(self, *args, **options):

        username = os.getenv(
            "DJANGO_SUPERUSER_USERNAME",
            "admin"
        )

        email = os.getenv(
            "DJANGO_SUPERUSER_EMAIL",
            "admin@jarvice.local"
        )

        password = os.getenv(
            "DJANGO_SUPERUSER_PASSWORD",
            "cambiar-esta-contrasena"
        )

        usuario, creado = User.objects.get_or_create(
            username=username,
            defaults={
                "email": email,
                "is_staff": True,
                "is_superuser": True,
                "is_active": True,
            }
        )

        if creado:
            usuario.set_password(password)
            usuario.save()

            self.stdout.write(
                self.style.SUCCESS(
                    f"Administrador Jarvice '{username}' creado."
                )
            )

        else:

            cambios = False

            if usuario.email != email:
                usuario.email = email
                cambios = True

            if not usuario.is_staff:
                usuario.is_staff = True
                cambios = True

            if not usuario.is_superuser:
                usuario.is_superuser = True
                cambios = True

            if not usuario.is_active:
                usuario.is_active = True
                cambios = True

            if cambios:
                usuario.save()

            self.stdout.write(
                self.style.WARNING(
                    f"Administrador Jarvice '{username}' ya existe."
                )
            )

        perfil, perfil_creado = PerfilUsuario.objects.get_or_create(
            usuario=usuario,
            defaults={
                "rol": "ADMIN",
            }
        )

        if perfil.rol != "ADMIN":
            perfil.rol = "ADMIN"
            perfil.save(update_fields=["rol"])

        if perfil_creado:
            self.stdout.write(
                self.style.SUCCESS(
                    "Perfil Jarvice ADMIN creado correctamente."
                )
            )
        else:
            self.stdout.write(
                self.style.SUCCESS(
                    "Perfil Jarvice ADMIN verificado correctamente."
                )
            )

        self.stdout.write(
            self.style.SUCCESS(
                "Inicialización de Jarvice completada."
            )
        )

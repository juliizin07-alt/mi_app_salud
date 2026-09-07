import json

from django.test import TestCase, Client

from mi_app_salud.models import Paciente, Dispositivo
from mi_app_salud.services.dispositivo_service import (
    establecer_credencial_dispositivo,
    verificar_credencial_dispositivo,
)


class DispositivoAutenticacionTests(TestCase):

    def setUp(self):
        self.paciente = Paciente.objects.create(
            nombre="Paciente",
            apellido="Prueba",
            edad=40,
        )

        self.dispositivo = Dispositivo.objects.create(
            paciente=self.paciente,
            nombre="Smartwatch Test",
            tipo="SMARTWATCH",
            identificador="TEST-AUTH-001",
        )

        self.credencial = "Test-Jarvice-2026!"

        establecer_credencial_dispositivo(
            self.dispositivo,
            self.credencial
        )

        self.client = Client(
            HTTP_HOST="127.0.0.1"
        )

    def test_credencial_correcta(self):
        respuesta = self.client.post(
            "/api/dispositivo/heartbeat/",
            data=json.dumps({
                "identificador": "TEST-AUTH-001",
                "credencial": self.credencial,
                "bateria": 95,
            }),
            content_type="application/json",
        )

        self.assertEqual(
            respuesta.status_code,
            200
        )

        self.dispositivo.refresh_from_db()

        self.assertTrue(
            self.dispositivo.conectado
        )

        self.assertEqual(
            self.dispositivo.bateria,
            95
        )

    def test_credencial_incorrecta(self):
        respuesta = self.client.post(
            "/api/dispositivo/heartbeat/",
            data=json.dumps({
                "identificador": "TEST-AUTH-001",
                "credencial": "credencial-incorrecta",
                "bateria": 95,
            }),
            content_type="application/json",
        )

        self.assertEqual(
            respuesta.status_code,
            401
        )

    def test_credencial_ausente(self):
        respuesta = self.client.post(
            "/api/dispositivo/heartbeat/",
            data=json.dumps({
                "identificador": "TEST-AUTH-001",
                "bateria": 95,
            }),
            content_type="application/json",
        )

        self.assertEqual(
            respuesta.status_code,
            401
        )

    def test_verificacion_directa_de_credencial(self):
        self.assertTrue(
            verificar_credencial_dispositivo(
                self.dispositivo,
                self.credencial
            )
        )

        self.assertFalse(
            verificar_credencial_dispositivo(
                self.dispositivo,
                "credencial-incorrecta"
            )
        )

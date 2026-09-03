from types import SimpleNamespace
from unittest.mock import patch

from django.test import SimpleTestCase

from mi_app_salud.brain import procesar_estado
from mi_app_salud.services.hospital_service import procesar_evento


class JarviceBrainTests(SimpleTestCase):

    def setUp(self):
        self.paciente = SimpleNamespace(
            nombre="Paciente Test"
        )

    def test_estado_ok(self):
        decision = procesar_estado(
            self.paciente,
            "OK"
        )

        self.assertEqual(decision["nivel"], 1)
        self.assertEqual(decision["color"], "verde")

    def test_estado_dolor(self):
        decision = procesar_estado(
            self.paciente,
            "DOLOR"
        )

        self.assertEqual(decision["nivel"], 2)
        self.assertEqual(decision["color"], "amarillo")

    def test_estado_critico(self):
        decision = procesar_estado(
            self.paciente,
            "CRITICO"
        )

        self.assertEqual(decision["nivel"], 3)
        self.assertEqual(decision["color"], "rojo")

    def test_estado_desconocido(self):
        decision = procesar_estado(
            self.paciente,
            "OTRO"
        )

        self.assertEqual(decision["nivel"], 0)
        self.assertEqual(decision["color"], "gris")

    @patch("mi_app_salud.services.hospital_service.enviar_whatsapp")
    def test_estado_critico_genera_alerta(self, mock_whatsapp):

        decision = procesar_evento(
            self.paciente,
            "CRITICO"
        )

        self.assertEqual(decision["nivel"], 3)
        mock_whatsapp.assert_called_once()

    @patch("mi_app_salud.services.hospital_service.enviar_whatsapp")
    def test_estado_ok_no_genera_alerta(self, mock_whatsapp):

        decision = procesar_evento(
            self.paciente,
            "OK"
        )

        self.assertEqual(decision["nivel"], 1)
        mock_whatsapp.assert_not_called()
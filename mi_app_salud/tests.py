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

    # ==================================================
    # SIGNOS VITALES DEL SMARTWATCH
    # ==================================================

    def test_signos_vitales_normales(self):
        respuesta = self.client.post(
            "/api/dispositivo/signos-vitales/",
            data=json.dumps({
                "identificador": "TEST-AUTH-001",
                "credencial": self.credencial,
                "frecuencia_cardiaca": 82,
                "saturacion_oxigeno": 97,
                "temperatura": 36.7,
                "presion_arterial": "120/75",
                "estado_emocional": "ESTABLE",
            }),
            content_type="application/json",
        )

        self.assertEqual(
            respuesta.status_code,
            200
        )

        datos = respuesta.json()

        self.assertEqual(
            datos["signos_vitales"]["origen"],
            "SMARTWATCH"
        )

        self.assertEqual(
            datos["analisis"]["riesgo_vital"],
            "BAJO"
        )

        self.assertEqual(
            datos["analisis"]["color_riesgo_vital"],
            "verde"
        )

    def test_signos_vitales_atencion(self):
        respuesta = self.client.post(
            "/api/dispositivo/signos-vitales/",
            data=json.dumps({
                "identificador": "TEST-AUTH-001",
                "credencial": self.credencial,
                "frecuencia_cardiaca": 110,
                "saturacion_oxigeno": 93,
                "temperatura": 37.8,
                "presion_arterial": "135/85",
                "estado_emocional": "ANSIEDAD",
            }),
            content_type="application/json",
        )

        self.assertEqual(
            respuesta.status_code,
            200
        )

        datos = respuesta.json()

        self.assertEqual(
            datos["analisis"]["riesgo_vital"],
            "ATENCION"
        )

        self.assertEqual(
            datos["analisis"]["color_riesgo_vital"],
            "amarillo"
        )

        self.assertEqual(
            datos["analisis"]["nivel_riesgo_ia"],
            "MODERADO"
        )

    def test_signos_vitales_criticos(self):
        respuesta = self.client.post(
            "/api/dispositivo/signos-vitales/",
            data=json.dumps({
                "identificador": "TEST-AUTH-001",
                "credencial": self.credencial,
                "frecuencia_cardiaca": 145,
                "saturacion_oxigeno": 88,
                "temperatura": 39.2,
                "presion_arterial": "160/100",
                "estado_emocional": "ANGUSTIADO",
            }),
            content_type="application/json",
        )

        self.assertEqual(
            respuesta.status_code,
            200
        )

        datos = respuesta.json()

        self.assertEqual(
            datos["analisis"]["riesgo_vital"],
            "CRITICO"
        )

        self.assertEqual(
            datos["analisis"]["color_riesgo_vital"],
            "rojo"
        )

        self.assertEqual(
            datos["analisis"]["nivel_riesgo_ia"],
            "CRITICO"
        )

    def test_signos_vitales_con_credencial_incorrecta(self):
        respuesta = self.client.post(
            "/api/dispositivo/signos-vitales/",
            data=json.dumps({
                "identificador": "TEST-AUTH-001",
                "credencial": "credencial-incorrecta",
                "frecuencia_cardiaca": 82,
            }),
            content_type="application/json",
        )

        self.assertEqual(
            respuesta.status_code,
            401
        )
    # ==================================================
    # VALIDACIONES DE LA API DEL SMARTWATCH
    # ==================================================

    def test_signos_vitales_json_invalido(self):
        respuesta = self.client.post(
            "/api/dispositivo/signos-vitales/",
            data="{json-invalido",
            content_type="application/json",
        )

        self.assertEqual(
            respuesta.status_code,
            400
        )

    def test_signos_vitales_sin_datos_clinicos(self):
        respuesta = self.client.post(
            "/api/dispositivo/signos-vitales/",
            data=json.dumps({
                "identificador": "TEST-AUTH-001",
                "credencial": self.credencial,
            }),
            content_type="application/json",
        )

        self.assertEqual(
            respuesta.status_code,
            400
        )

    def test_signos_vitales_frecuencia_invalida(self):
        respuesta = self.client.post(
            "/api/dispositivo/signos-vitales/",
            data=json.dumps({
                "identificador": "TEST-AUTH-001",
                "credencial": self.credencial,
                "frecuencia_cardiaca": "abc",
            }),
            content_type="application/json",
        )

        self.assertEqual(
            respuesta.status_code,
            400
        )

    def test_signos_vitales_saturacion_invalida(self):
        respuesta = self.client.post(
            "/api/dispositivo/signos-vitales/",
            data=json.dumps({
                "identificador": "TEST-AUTH-001",
                "credencial": self.credencial,
                "saturacion_oxigeno": "abc",
            }),
            content_type="application/json",
        )

        self.assertEqual(
            respuesta.status_code,
            400
        )

    def test_signos_vitales_temperatura_invalida(self):
        respuesta = self.client.post(
            "/api/dispositivo/signos-vitales/",
            data=json.dumps({
                "identificador": "TEST-AUTH-001",
                "credencial": self.credencial,
                "temperatura": "abc",
            }),
            content_type="application/json",
        )

        self.assertEqual(
            respuesta.status_code,
            400
        )

    def test_signos_vitales_presion_invalida(self):
        respuesta = self.client.post(
            "/api/dispositivo/signos-vitales/",
            data=json.dumps({
                "identificador": "TEST-AUTH-001",
                "credencial": self.credencial,
                "presion_arterial": "120",
            }),
            content_type="application/json",
        )

        self.assertEqual(
            respuesta.status_code,
            400
        )

    def test_signos_vitales_sin_identificador(self):
        respuesta = self.client.post(
            "/api/dispositivo/signos-vitales/",
            data=json.dumps({
                "credencial": self.credencial,
                "frecuencia_cardiaca": 82,
            }),
            content_type="application/json",
        )

        self.assertEqual(
            respuesta.status_code,
            400
        )

    def test_signos_vitales_sin_credencial(self):
        respuesta = self.client.post(
            "/api/dispositivo/signos-vitales/",
            data=json.dumps({
                "identificador": "TEST-AUTH-001",
                "frecuencia_cardiaca": 82,
            }),
            content_type="application/json",
        )

        self.assertEqual(
            respuesta.status_code,
            401
        )

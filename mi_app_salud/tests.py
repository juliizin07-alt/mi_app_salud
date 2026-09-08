import json
from unittest.mock import patch

from django.test import TestCase, Client

from mi_app_salud.models import (
    Paciente,
    Dispositivo,
    SignoVital,
    AuditoriaJarvice,
)
from mi_app_salud.services.dispositivo_service import (
    establecer_credencial_dispositivo,
    verificar_credencial_dispositivo,
)
from mi_app_salud.services.alerta_service import (
    escalar_emergencia,
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
# ==================================================
# TESTS DEL ESCALAMIENTO DE EMERGENCIA
# ==================================================

class EscalamientoEmergenciaTests(TestCase):

    def setUp(self):
        self.paciente = Paciente.objects.create(
            nombre="Paciente",
            apellido="Emergencia",
            edad=40,
            contacto_emergencia="Contacto Uno",
            telefono_emergencia="+5491111111111",
            contacto_emergencia_2="Contacto Dos",
            telefono_emergencia_2="+5492222222222",
            contacto_emergencia_3="Contacto Tres",
            telefono_emergencia_3="+5493333333333",
        )

        self.signo = SignoVital.objects.create(
            paciente=self.paciente,
            frecuencia_cardiaca=145,
            saturacion_oxigeno=88,
            temperatura=39.2,
            presion_arterial="160/100",
            estado_emocional="ANGUSTIADO",
            origen="SMARTWATCH",
        )

        self.analisis = {
            "riesgo_vital": "CRITICO",
        }

    @patch(
        "mi_app_salud.services.alerta_service.enviar_whatsapp_a"
    )
    def test_contacto_1_notificado(self, enviar_mock):

        enviar_mock.return_value = True

        resultado = escalar_emergencia(
            paciente=self.paciente,
            signo=self.signo,
            analisis=self.analisis,
            usuario=None,
            ip="127.0.0.1",
        )

        self.assertEqual(
            resultado["nivel"],
            1
        )

        self.assertEqual(
            resultado["estado"],
            "CONTACTO_1_NOTIFICADO"
        )

        enviar_mock.assert_called_once()

        self.assertEqual(
            enviar_mock.call_args.args[0],
            self.paciente.telefono_emergencia
        )

    @patch(
        "mi_app_salud.services.alerta_service.enviar_whatsapp_a"
    )
    def test_falla_contacto_1_y_notifica_contacto_2(
        self,
        enviar_mock
    ):

        enviar_mock.side_effect = [
            False,
            True,
        ]

        resultado = escalar_emergencia(
            paciente=self.paciente,
            signo=self.signo,
            analisis=self.analisis,
            usuario=None,
            ip="127.0.0.1",
        )

        self.assertEqual(
            resultado["nivel"],
            2
        )

        self.assertEqual(
            resultado["estado"],
            "CONTACTO_2_NOTIFICADO"
        )

        self.assertEqual(
            enviar_mock.call_count,
            2
        )

        self.assertEqual(
            enviar_mock.call_args_list[0].args[0],
            self.paciente.telefono_emergencia
        )

        self.assertEqual(
            enviar_mock.call_args_list[1].args[0],
            self.paciente.telefono_emergencia_2
        )

    @patch(
        "mi_app_salud.services.alerta_service.enviar_whatsapp_a"
    )
    def test_fallan_contactos_1_y_2_y_notifica_contacto_3(
        self,
        enviar_mock
    ):

        enviar_mock.side_effect = [
            False,
            False,
            True,
        ]

        resultado = escalar_emergencia(
            paciente=self.paciente,
            signo=self.signo,
            analisis=self.analisis,
            usuario=None,
            ip="127.0.0.1",
        )

        self.assertEqual(
            resultado["nivel"],
            3
        )

        self.assertEqual(
            resultado["estado"],
            "CONTACTO_3_NOTIFICADO"
        )

        self.assertEqual(
            enviar_mock.call_count,
            3
        )

        self.assertEqual(
            enviar_mock.call_args_list[2].args[0],
            self.paciente.telefono_emergencia_3
        )

    @patch(
        "mi_app_salud.services.alerta_service.enviar_whatsapp_a"
    )
    def test_sin_contactos_disponibles(
        self,
        enviar_mock
    ):

        self.paciente.telefono_emergencia = ""
        self.paciente.telefono_emergencia_2 = ""
        self.paciente.telefono_emergencia_3 = ""

        self.paciente.save()

        resultado = escalar_emergencia(
            paciente=self.paciente,
            signo=self.signo,
            analisis=self.analisis,
            usuario=None,
            ip="127.0.0.1",
        )

        self.assertEqual(
            resultado["nivel"],
            0
        )

        self.assertEqual(
            resultado["estado"],
            "SIN_CONTACTO"
        )

        enviar_mock.assert_not_called()

        auditoria = AuditoriaJarvice.objects.filter(
            modulo="ESCALAMIENTO",
            accion="EMERGENCIA",
            datos_extra__estado="SIN_CONTACTO",
        ).exists()

        self.assertTrue(
            auditoria
        )

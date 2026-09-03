from unittest.mock import patch

from django.test import SimpleTestCase

from mi_app_salud.alerts import enviar_whatsapp


class WhatsAppTests(SimpleTestCase):

    @patch(
        "mi_app_salud.alerts.ULTIMOS_ENVIADOS",
        new_callable=dict
    )
    @patch("mi_app_salud.alerts.Client")
    @patch("mi_app_salud.alerts.AUTH_TOKEN", "test_auth_token")
    @patch("mi_app_salud.alerts.ACCOUNT_SID", "test_account_sid")
    @patch("mi_app_salud.alerts.FROM_NUMBER", "whatsapp:+10000000000")
    @patch("mi_app_salud.alerts.TO_NUMBER", "whatsapp:+10000000001")
    def test_enviar_whatsapp(
        self,
        mock_client,
        mock_ultimos_enviados
    ):

        mock_message = (
            mock_client
            .return_value
            .messages
            .create
            .return_value
        )

        mock_message.sid = "TEST_SID"

        resultado = enviar_whatsapp(
            "Test de WhatsApp desde Jarvice"
        )

        self.assertTrue(resultado)

        mock_client.return_value.messages.create.assert_called_once()

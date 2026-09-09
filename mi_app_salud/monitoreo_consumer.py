import json

from channels.generic.websocket import AsyncWebsocketConsumer


class MonitoreoConsumer(AsyncWebsocketConsumer):

    async def connect(self):

        usuario = self.scope.get("user")

        if not usuario or not usuario.is_authenticated:
            await self.close()
            return

        await self.channel_layer.group_add(
            "monitoreo",
            self.channel_name
        )

        await self.accept()

        await self.send(
            text_data=json.dumps({
                "tipo": "conexion",
                "estado": "CONECTADO",
                "mensaje": "Conectado al monitoreo en tiempo real.",
            })
        )

    async def disconnect(self, close_code):

        await self.channel_layer.group_discard(
            "monitoreo",
            self.channel_name
        )

    async def enviar_monitoreo(self, event):

        await self.send(
            text_data=json.dumps(
                event["data"]
            )
        )
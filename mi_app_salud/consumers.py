from channels.generic.websocket import AsyncWebsocketConsumer
import json

class EstadoConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        await self.channel_layer.group_add("estados", self.channel_name)
        await self.accept()

    async def disconnect(self, close_code):
        await self.channel_layer.group_discard("estados", self.channel_name)

    async def enviar_estado(self, event):
        await self.send(text_data=json.dumps(event["data"]))
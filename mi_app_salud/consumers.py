from channels.generic.websocket import AsyncWebsocketConsumer
import json

# ==================================================
# USUARIOS CONECTADOS EN TIEMPO REAL
# ==================================================

USUARIOS_ONLINE = {}

# ==================================================
# ESTADOS DE SALUD
# ==================================================

class EstadoConsumer(AsyncWebsocketConsumer):

    async def connect(self):

        await self.channel_layer.group_add(
            "estados",
            self.channel_name
        )

        await self.accept()

    async def disconnect(self, close_code):

        await self.channel_layer.group_discard(
            "estados",
            self.channel_name
        )

    async def enviar_estado(self, event):

        await self.send(
            text_data=json.dumps(
                event["data"]
            )
        )


class PresenciaConsumer(AsyncWebsocketConsumer):

    async def connect(self):

        # Inicializar atributos antes de cualquier operación
        self.usuario_id = None
        self.username = None

        usuario = self.scope.get("user")

        # --------------------------------------------------
        # VERIFICAR AUTENTICACIÓN
        # --------------------------------------------------

        if not usuario or not usuario.is_authenticated:

            await self.close()
            return

        # --------------------------------------------------
        # DATOS DEL USUARIO
        # --------------------------------------------------

        self.usuario_id = usuario.id
        self.username = usuario.username

        # --------------------------------------------------
        # REGISTRAR CONEXIÓN
        # --------------------------------------------------

        USUARIOS_ONLINE[self.usuario_id] = {
            "usuario_id": self.usuario_id,
            "username": self.username,
        }

        # --------------------------------------------------
        # CONECTAR AL GRUPO
        # --------------------------------------------------

        await self.channel_layer.group_add(
            "presencia",
            self.channel_name
        )

        await self.accept()

        # --------------------------------------------------
        # ENVIAR LISTA ACTUAL
        # --------------------------------------------------

        await self.send(
            text_data=json.dumps({
                "tipo": "lista_usuarios_online",
                "usuarios": list(
                    USUARIOS_ONLINE.values()
                ),
            })
        )

        # --------------------------------------------------
        # AVISAR AL RESTO
        # --------------------------------------------------

        await self.channel_layer.group_send(
            "presencia",
            {
                "type": "usuario_conectado",
                "usuario_id": self.usuario_id,
                "username": self.username,
            }
        )

    async def disconnect(self, close_code):

        # --------------------------------------------------
        # SI EL USUARIO LLEGÓ A CONECTARSE
        # --------------------------------------------------

        if self.usuario_id is not None:

            if self.usuario_id in USUARIOS_ONLINE:

                del USUARIOS_ONLINE[
                    self.usuario_id
                ]

            # ----------------------------------------------
            # SALIR DEL GRUPO
            # ----------------------------------------------

            await self.channel_layer.group_discard(
                "presencia",
                self.channel_name
            )

            # ----------------------------------------------
            # AVISAR DESCONEXIÓN
            # ----------------------------------------------

            await self.channel_layer.group_send(
                "presencia",
                {
                    "type": "usuario_desconectado",
                    "usuario_id": self.usuario_id,
                    "username": self.username,
                }
            )

    async def usuario_conectado(self, event):

        await self.send(
            text_data=json.dumps({
                "tipo": "usuario_conectado",
                "usuario_id": event["usuario_id"],
                "username": event["username"],
            })
        )

    async def usuario_desconectado(self, event):

        await self.send(
            text_data=json.dumps({
                "tipo": "usuario_desconectado",
                "usuario_id": event["usuario_id"],
                "username": event["username"],
            })
        )
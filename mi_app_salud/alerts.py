from twilio.rest import Client
import time

ULTIMOS_ENVIADOS = {}
COOLDOWN_SEGUNDOS = 30

def puede_enviar(numero):
    ahora = time.time()

    if numero not in ULTIMOS_ENVIADOS:
        ULTIMOS_ENVIADOS[numero] = ahora
        return True

    if ahora - ULTIMOS_ENVIADOS[numero] > COOLDOWN_SEGUNDOS:
        ULTIMOS_ENVIADOS[numero] = ahora
        return True

    return False

# =========================
# 🔐 TUS DATOS (FUNCIONAL AHORA)
# =========================

ACCOUNT_SID = "AC66b3facebf1b4f235fffaa6bc549a050"
AUTH_TOKEN = "1988868be7c69cf252567eca267a2f5a"  # ⚠️ reemplazalo si lo tenés real

FROM_NUMBER = "whatsapp:+14155238886"   # Twilio Sandbox
TO_NUMBER = "whatsapp:+5492494350360"    # Tu número (Argentina)

# =========================
# 🔌 CLIENTE TWILIO
# =========================

client = Client(ACCOUNT_SID, AUTH_TOKEN)


# =========================
# 📲 FUNCIÓN PRINCIPAL
# =========================

def enviar_whatsapp(mensaje: str) -> bool:
    """
    Envía mensaje por WhatsApp usando Twilio Sandbox.
    """

    # 🧪 Validación básica
    if not mensaje or mensaje.strip() == "":
        print("⚠️ Mensaje vacío, no se envía WhatsApp")
        return False

    if not FROM_NUMBER.startswith("whatsapp:"):
        print("❌ FROM_NUMBER inválido")
        return False

    if not TO_NUMBER.startswith("whatsapp:"):
        print("❌ TO_NUMBER inválido")
        return False

    try:
        print("📲 Enviando WhatsApp...")

        message = client.messages.create(
            body=mensaje,
            from_=FROM_NUMBER,
            to=TO_NUMBER
        )

        print("✅ WhatsApp enviado correctamente")
        print("SID:", message.sid)

        return True

    except Exception as e:
        print("❌ Error al enviar WhatsApp:", str(e))
        return False
    ULTIMOS_ENVIADOS = {}
    import time

def enviar_whatsapp(mensaje: str):
    try:
        print("📲 Enviando WhatsApp...")

        message = client.messages.create(
            body=mensaje,
            from_=FROM_NUMBER,
            to=TO_NUMBER
        )

        print("✅ ENVIADO!")
        print("SID:", message.sid)

        return True

    except Exception as e:
        print("❌ ERROR WHATSAPP:")
        print(str(e))
        return False
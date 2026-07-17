from twilio.rest import Client
import time

# =========================
# CONTROL ANTISPAM
# =========================

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
# TWILIO CONFIG
# =========================

ACCOUNT_SID = "AC66b3facebf1b4f235fffaa6bc549a050"
AUTH_TOKEN = "1988868be7c69cf252567eca267a2f5a"

FROM_NUMBER = "whatsapp:+14155238886"
TO_NUMBER = "whatsapp:+5492494350360"

client = Client(ACCOUNT_SID, AUTH_TOKEN)


# =========================
# ENVIAR WHATSAPP
# =========================

def enviar_whatsapp(mensaje):

    if not mensaje.strip():
        print("⚠️ Mensaje vacío")
        return False

    if not puede_enviar(TO_NUMBER):
        print("⏳ Esperando cooldown...")
        return False

    try:
        print("📲 Enviando WhatsApp...")

        message = client.messages.create(
            body=mensaje,
            from_=FROM_NUMBER,
            to=TO_NUMBER
        )

        print("✅ WhatsApp enviado")
        print("SID:", message.sid)

        return True

    except Exception as e:
        print("❌ Error:", str(e))
        return False
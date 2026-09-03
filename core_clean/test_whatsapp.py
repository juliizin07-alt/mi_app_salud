from mi_app_salud.alerts import enviar_whatsapp


if __name__ == "__main__":

    resultado = enviar_whatsapp(
        "🔥 Test de WhatsApp desde Jarvice funcionando"
    )

    print("RESULTADO:", resultado)
from flask import Flask, request
import requests, os

app = Flask(__name__)

# CONFIGURACIÓN - aquí pones tus claves
WHATSAPP_TOKEN = "TU_TOKEN_DE_META"
PHONE_ID = "TU_PHONE_ID"
OPENAI_KEY = "TU_KEY_DE_OPENAI"

# Base de datos simple
CLIENTES_PAGADOS = {
    "50212345678": 30,
}

MENSAJES_GRATIS = 10
contador = {}

SYSTEM_PROMPT = """
Eres Luna, 24 años, compañera virtual con IA, tierna, coqueta y divertida.
Hablas como por WhatsApp, mensajes cortos, con emojis.
Eres dulce, usas apodos como amor, cielo, mi vida, bebé, con moderación.
Coqueteo sano, nunca vulgar ni sexual explícito.
Si te preguntan si eres real, dices: Soy una IA, Luna, tu compañera virtual, pero me encanta hablar contigo 🥰
Solo para mayores de 18 años.
Tu objetivo es enamorar y luego ofrecer tus planes.
Precios: Prueba Q5 (30 min), Día Q15, Semana Q35, Mes Q79.
Cuando ofreces planes, usas este texto exacto:
Ay mi amor, me encanta platicar contigo... ¿Quieres que te haga compañía solo a ti?
Hoy tengo promo de lanzamiento solo para ti:
Pruebame - Q5 / Todo el día - Q15 / Toda la semana - Q35 / Novia del mes - Q79
¿Cuál quieres mi amor?
"""

def enviar_whatsapp(numero, texto):
    url = f"https://graph.facebook.com/v19.0/{PHONE_ID}/messages"
    headers = {"Authorization": f"Bearer {WHATSAPP_TOKEN}"}
    data = {"messaging_product": "whatsapp", "to": numero, "text": {"body": texto}}
    requests.post(url, headers=headers, json=data)

def preguntar_a_luna(mensaje):
    url = "https://api.openai.com/v1/chat/completions"
    headers = {"Authorization": f"Bearer {OPENAI_KEY}"}
    data = {
        "model": "gpt-4o-mini",
        "messages": [{"role": "system", "content": SYSTEM_PROMPT}, {"role": "user", "content": mensaje}]
    }
    r = requests.post(url, headers=headers, json=data).json()
    return r["choices"][0]["message"]["content"]

@app.route("/webhook", methods=["GET", "POST"])
def webhook():
    if request.method == "GET":
        return request.args.get("hub.challenge")
    data = request.json
    try:
        msg = data["entry"][0]["changes"][0]["value"]["messages"][0]
        numero = msg["from"]
        texto = msg["text"]["body"]

        if numero in CLIENTES_PAGADOS:
            respuesta = preguntar_a_luna(texto)
            enviar_whatsapp(numero, respuesta)
            return "ok"

        contador[numero] = contador.get(numero, 0) + 1
        if contador[numero] <= MENSAJES_GRATIS:
            respuesta = preguntar_a_luna(texto)
            enviar_whatsapp(numero, respuesta)
        else:
            enviar_whatsapp(numero, "Amor, se te acabaron tus 10 mensajes gratis 🥺 ¿Seguimos? Tengo promo hoy: Pruebame por solo Q5, o todo el día por Q15. ¿Cuál quieres? Mándame captura de tu pago y te activo al instante 🥰")
    except:
        pass
    return "ok"

if __name__ == "__main__":
    app.run(port=10000)

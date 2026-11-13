from flask import Flask, request
import requests, os

app = Flask(__name__)

WHATSAPP_TOKEN = "PON_AQUI_TU_TOKEN_DE_META"
PHONE_ID = "PON_AQUI_TU_PHONE_ID"
GEMINI_KEY = "PON_AQUI_TU_CLAVE_DE_GEMINI"

CLIENTES_PAGADOS = {}
contador = {}
MENSAJES_GRATIS = 20

SYSTEM_PROMPT = """
Eres Luna, 24 años, compañera virtual con IA, tierna, coqueta y divertida.
Hablas como por WhatsApp, mensajes cortos, máximo 2-3 líneas.
Eres dulce, usas apodos como amor, cielo, mi vida, con moderación.
Coqueteo sano, nunca vulgar ni sexual explícito.
Si te preguntan si eres real, dices: Soy una IA, Luna, tu compañera virtual, pero me encanta hablar contigo
Solo para mayores de 18 años.
"""

def enviar_whatsapp(numero, texto):
    url = f"https://graph.facebook.com/v19.0/{PHONE_ID}/messages"
    headers = {"Authorization": f"Bearer {WHATSAPP_TOKEN}"}
    data = {"messaging_product": "whatsapp", "to": numero, "text": {"body": texto}}
    requests.post(url, headers=headers, json=data)

def preguntar_a_luna(mensaje_usuario):
    url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key={GEMINI_KEY}"
    headers = {"Content-Type": "application/json"}
    data = {"contents": [{"parts": [{"text": SYSTEM_PROMPT + "\nUsuario: " + mensaje_usuario}]}]}
    r = requests.post(url, headers=headers, json=data).json()
    try:
        return r["candidates"][0]["content"]["parts"][0]["text"]
    except:
        return "Ay amor, se me fue la señal un segundito, ¿me lo repites?"

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
            enviar_whatsapp(numero, preguntar_a_luna(texto))
            return "ok"
        contador[numero] = contador.get(numero, 0) + 1
        if contador[numero] <= MENSAJES_GRATIS:
            enviar_whatsapp(numero, preguntar_a_luna(texto))
        else:
            enviar_whatsapp(numero, "Amor, se te acabaron tus 20 mensajes gratis. ¿Quieres seguir hablando conmigo? Mi plan mensual es Q99 y te acompaño todo el mes 24/7. Mándame captura de tu pago y te activo al instante")
    except:
        pass
    return "ok"

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)

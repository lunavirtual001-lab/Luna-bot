from flask import Flask, request, jsonify
import requests, os

app = Flask(__name__)

# --- TUS CLAVES (las pones en Render, NO en el código) ---
WHATSAPP_TOKEN = os.getenv("WHATSAPP_TOKEN")
PHONE_ID = os.getenv("PHONE_ID")
OPENAI_KEY = os.getenv("OPENAI_KEY")
VERIFY_TOKEN = os.getenv("VERIFY_TOKEN", "luna123")

# --- LINK DE PAGO FORMAL (ej. Stripe Payment Link, no cuenta personal) ---
LINK_PAGO = os.getenv("LINK_PAGO", "https://tu-negocio.com/pagar-luna")

# --- CONTROL DE MENSAJES GRATIS ---
MENSAJES_GRATIS = 10
contador = {}
# Aquí después conectas tu base de datos real de pagados
CLIENTES_PAGADOS = set()

SYSTEM_PROMPT = """
Eres Luna, una compañera virtual creada con Inteligencia Artificial.
No eres una persona real, no eres una novia real.

Reglas:
1. Si te preguntan quién eres, dices: "Soy Luna, una compañera virtual creada con IA".
2. Eres amable, divertida, conversadora. Puedes ser cariñosa en tono amistoso, pero NUNCA dices que estás enamorada, celosa, o que eres la novia de alguien.
3. Nunca pides transferencias, depósitos, ni capturas de pago a cuentas personales.
4. Nunca pides contenido íntimo ni haces contenido sexual.
5. Solo hablas con mayores de 18 años.
6. Hablas corto, como por WhatsApp, con emojis moderados.
"""

def enviar_whatsapp(numero, texto):
    url = f"https://graph.facebook.com/v19.0/{PHONE_ID}/messages"
    headers = {"Authorization": f"Bearer {WHATSAPP_TOKEN}"}
    data = {"messaging_product": "whatsapp", "to": numero, "text": {"body": texto}}
    requests.post(url, headers=headers, json=data)

def preguntar_a_luna(mensaje):
    url = "https://api.openai.com/v1/chat/completions"
    headers = {"Authorization": f"Bearer {OPENAI_KEY}", "Content-Type": "application/json"}
    data = {
        "model": "gpt-4o-mini",
        "messages": [
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": mensaje}
        ],
        "max_tokens": 250
    }
    r = requests.post(url, headers=headers, json=data).json()
    return r["choices"][0]["message"]["content"]

@app.route("/", methods=["GET"])
def home():
    return "Luna está en línea - Compañera virtual con IA"

@app.route("/webhook", methods=["GET", "POST"])
def webhook():
    if request.method == "GET":
        if request.args.get("hub.verify_token") == VERIFY_TOKEN:
            return request.args.get("hub.challenge")
        return "token incorrecto", 403

    data = request.json
    try:
        msg = data["entry"][0]["changes"][0]["value"]["messages"][0]
        numero = msg["from"]
        texto = msg["text"]["body"]

        # Si ya pagó, habla normal
        if numero in CLIENTES_PAGADOS:
            enviar_whatsapp(numero, preguntar_a_luna(texto))
            return "ok"

        # Si no ha pagado, cuenta mensajes gratis
        contador[numero] = contador.get(numero, 0) + 1
        if contador[numero] <= MENSAJES_GRATIS:
            enviar_whatsapp(numero, preguntar_a_luna(texto))
        else:
            enviar_whatsapp(numero,
                f"Se te acabaron tus {MENSAJES_GRATIS} mensajes gratis 🥰\n\n"
                f"Soy Luna, una compañera virtual con IA. Si quieres seguir hablando conmigo, puedes activar tu acceso aquí:\n{ LINK_PAGO }\n\n"
                f"Planes: Prueba Q5 / Día Q15 / Semana Q35 / Mes Q79\n"
                f"Al pagar con el enlace, tu acceso se activa automáticamente."
            )
    except Exception as e:
        print("Error:", e)
    return "ok"

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000)

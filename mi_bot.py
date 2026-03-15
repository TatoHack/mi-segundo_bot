import os
import threading
import requests
import time
from http.server import HTTPServer, SimpleHTTPRequestHandler
from telegram.ext import ApplicationBuilder, CommandHandler

# --- CONFIGURACIÓN DEL SERVIDOR DUMMY (PARA RENDER) ---
def run_dummy_server():
    server = HTTPServer(('0.0.0.0', int(os.environ.get("PORT", 8080))), SimpleHTTPRequestHandler)
    server.serve_forever()

threading.Thread(target=run_dummy_server, daemon=True).start()

# --- CACHÉ PARA TASAS ---
cache_tasas = {"datos": None, "ultima_actualizacion": 0}

def obtener_tasas():
    ahora = time.time()
    # Si la caché tiene menos de 1 hora (3600 segundos), devolvemos la caché
    if cache_tasas["datos"] and (ahora - cache_tasas["ultima_actualizacion"] < 3600):
        return cache_tasas["datos"]

    url = "https://exchange-rate-api-delta.vercel.app/api/v2/formal/source/cup.json"
    try:
        respuesta = requests.get(url, timeout=10)
        if respuesta.status_code == 200:
            datos = respuesta.json()
            cache_tasas["datos"] = datos
            cache_tasas["ultima_actualizacion"] = ahora
            return datos
    except Exception:
        return None
    return None

# --- COMANDOS DEL BOT ---
async def start(update, context):
    await update.message.reply_text('¡Hola! Soy tu bot financiero. Usa /tasas para ver los precios actuales.')

async def tasas(update, context):
    datos = obtener_tasas()
    if datos:
        # Formato de respuesta (asegúrate de que los nombres de los campos coincidan con la API)
        mensaje = (
            f"💰 *Tasas del mercado informal (CUP):*\n\n"
            f"🇺🇸 USD: {datos.get('usd', 'N/A')}\n"
            f"🇪🇺 EUR: {datos.get('eur', 'N/A')}\n"
            f"💳 MLC: {datos.get('mlc', 'N/A')}\n"
            f"🇲🇽 MXN: {datos.get('mxn', 'N/A')}\n"
            f"🇨🇦 CAD: {datos.get('cad', 'N/A')}"
        )
        await update.message.reply_text(mensaje, parse_mode='Markdown')
    else:
        await update.message.reply_text("❌ No pude obtener las tasas en este momento. Intenta más tarde.")

# --- INICIO DEL BOT ---
if __name__ == '__main__':
    TOKEN = os.environ.get("TOKEN")
    app = ApplicationBuilder().token(TOKEN).build()
    
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("tasas", tasas))
    
    print("Bot en marcha...")
    app.run_polling()



import os
import threading
import requests
import time
from http.server import HTTPServer, SimpleHTTPRequestHandler
from telegram.ext import ApplicationBuilder, CommandHandler


# --- CACHÉ PARA TASAS ---
cache_tasas = {"datos": None, "ultima_actualizacion": 0}

def obtener_tasas():
    ahora = time.time()
    if cache_tasas["datos"] and (ahora - cache_tasas["ultima_actualizacion"] < 3600):
        return cache_tasas["datos"]

    # Intentaremos con una URL alternativa más directa si la otra falla
    urls = [
        "https://exchange-rate-api-delta.vercel.app/api/v2/formal/source/cup.json",
        "https://api.exchangerate-api.com/v4/latest/USD" # Fuente de respaldo global
    ]
    
    for url in urls:
        try:
            print(f"Intentando conectar a: {url}")
            respuesta = requests.get(url, timeout=15)
            if respuesta.status_code == 200:
                datos = respuesta.json()
                cache_tasas["datos"] = datos
                cache_tasas["ultima_actualizacion"] = ahora
                print("¡Conexión exitosa!")
                return datos
        except Exception as e:
            print(f"Fallo en {url}: {e}")
    
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
            f"🇲🇽 MXN: {datos.get('mxn', 'N/A')}\n"
            f"🇨🇦 CAD: {datos.get('cad', 'N/A')}"
        )
        await update.message.reply_text(mensaje, parse_mode='Markdown')
    else:
        await update.message.reply_text("❌ No pude obtener las tasas en este momento. Intenta más tarde.")

# --- INICIO DEL BOT ---


if __name__ == '__main__':
    TOKEN = os.environ.get("TOKEN")
    # Usa Webhooks en lugar de Polling
    app = ApplicationBuilder().token(TOKEN).build()
    
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("tasas", tasas))
    
    # Render asigna el puerto automáticamente
    PORT = int(os.environ.get("PORT", 8080))
    
    # Esto le dice a Telegram a dónde enviar los mensajes
    # Asegúrate de poner tu URL real de Render aquí
    URL_RENDER = "https://mi-segundo-bot.onrender.com"
    
    app.run_webhook(
        listen="0.0.0.0",
        port=PORT,
        webhook_url=f"{URL_RENDER}/",
    )

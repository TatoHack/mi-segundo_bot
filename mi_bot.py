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
    # Verifica si hay datos en caché para no saturar las APIs
    if cache_tasas["datos"] and (ahora - cache_tasas["ultima_actualizacion"] < 3600):
        return cache_tasas["datos"]

    # Intentamos con la API de Cuba primero, y luego con una global si falla
    urls = [
        "https://exchange-rate-api-delta.vercel.app/api/v2/formal/source/cup.json",
        "https://open.er-api.com/v6/latest/USD"
    ]
    
    for url in urls:
        try:
            respuesta = requests.get(url, timeout=10)
            if respuesta.status_code == 200:
                cache_tasas["datos"] = respuesta.json()
                cache_tasas["ultima_actualizacion"] = ahora
                return cache_tasas["datos"]
        except Exception:
            continue
    return None

async def tasas(update, context):
    datos = obtener_tasas()
    if datos:
        # Buscamos 'usd' (API de Cuba) o 'USD' dentro de 'rates' (API Global)
        usd = datos.get('usd') or datos.get('rates', {}).get('USD', 'N/A')
        eur = datos.get('eur') or datos.get('rates', {}).get('EUR', 'N/A')
        mlc = datos.get('mlc', '---')
        mxn = datos.get('mxn') or datos.get('rates', {}).get('MXN', 'N/A')

        mensaje = (
            f"💰 *Tasas del mercado:*\n\n"
            f"🇺🇸 USD: {usd}\n"
            f"🇪🇺 EUR: {eur}\n"
            f"💳 MLC: {mlc}\n"
            f"🇲🇽 MXN: {mxn}"
        )
        await update.message.reply_text(mensaje, parse_mode='Markdown')
    else:
        await update.message.reply_text("❌ No se pudieron obtener las tasas en este momento.")





# --- COMANDOS DEL BOT ---
async def start(update, context):
    await update.message.reply_text('¡Hola! Soy tu bot financiero. Usa /tasas para ver los precios actuales.')



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

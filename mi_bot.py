import os
import threading
from http.server import HTTPServer, SimpleHTTPRequestHandler
from telegram.ext import ApplicationBuilder, CommandHandler

# Función para que Render no se queje por el puerto
def run_dummy_server():
    server = HTTPServer(('0.0.0.0', int(os.environ.get("PORT", 8080))), SimpleHTTPRequestHandler)
    server.serve_forever()

# Iniciamos el servidor en segundo plano
threading.Thread(target=run_dummy_server, daemon=True).start()

# --- AQUÍ VA EL RESTO DE TU CÓDIGO DEL BOT ---
TOKEN = os.environ.get("TOKEN")

async def start(update, context):
    await update.message.reply_text('¡El bot está vivo y funcionando!')

if __name__ == '__main__':
    app = ApplicationBuilder().token(TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.run_polling()


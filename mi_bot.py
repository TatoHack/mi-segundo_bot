import os
import logging
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes

# Esto toma el TOKEN de las variables de entorno del servidor (Render)
TOKEN = os.environ.get("TOKEN")

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text('¡Hola! El bot está funcionando de forma segura.')

if __name__ == '__main__':
    # Usamos el token que viene de la configuración
    app = ApplicationBuilder().token(TOKEN).build()
    
    app.add_handler(CommandHandler("start", start))
    
    print("Bot en marcha...")
    app.run_polling()

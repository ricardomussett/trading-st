#import logging
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes, MessageHandler, filters
import time
import os

from fun import AnalizeData

logging.basicConfig(
   format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
   level=logging.INFO
)

AD = AnalizeData()

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await update.message.reply_text("¡Hola! Soy tu bot de Telegram.")

async def inicio(update: Update, context: ContextTypes.DEFAULT_TYPE)  -> None:
    AD.cargar()
    await context.bot.send_message(chat_id=update.effective_chat.id, text=AD.name_coin)

async def actualizar(update: Update, context: ContextTypes.DEFAULT_TYPE)  -> None:
    await context.bot.send_message(chat_id=update.effective_chat.id, text="actualizando")
    AD.actualizar()
    await context.bot.send_message(chat_id=update.effective_chat.id, text="actualizado")

async def informar(update: Update, context: ContextTypes.DEFAULT_TYPE)  -> None:
    await context.bot.send_message(chat_id=update.effective_chat.id, text="comenzando informar")

    count = 0
    flag = True

    while flag:
        await context.bot.send_message(chat_id=update.effective_chat.id, text="actualizando datos")

        AD.actualizar()
        AD.verify_trigger(umbral_trigger = 10)

        type = "🐢 sideways"

        if AD.d_report["type"].lower() == "bull":
            type = "🐂 BULL"
        elif AD.d_report["type"].lower() == "bear":
            type = "🐻 BEAR"


        if AD.d_report:
            tipo_signal = type
            mensaje = f"""
                🚨 ALERTA DE TRADING 🚨

                📊 Tipo de Señal: {tipo_signal}
                ---------------------------------
                🎯 Referencia:
                💰 Valor: {AD.d_report["ref"]["value"]}
                ⌚ Fecha: {AD.d_report["ref"]["date"]}
                📐 Distancia: {AD.d_report["ref"]["distance"]}
                📏 Distancia: {AD.d_report["ref"]["distance_limit"]}
   
                ---------------------------------
                📈 Geneal
                🐂 BULL {AD.d_report["relation_general"].get("bull",0)} | 🐻 BEAR {AD.d_report["relation_general"].get("bear",0)}
                📊 Media: {AD.d_report["general"]["mean"]}
                ⬆️ Máximo: {AD.d_report["general"]["max"]}
                ⬇️ Mínimo: {AD.d_report["general"]["min"]}
                ---------------------------------
                📉 Limitado
                🐂 BULL {AD.d_report["relation_limit"].get("bull",0)} | 🐻 BEAR {AD.d_report["relation_limit"].get("bear",0)}
                📊 Media: {AD.d_report["limit"]["mean"]}
                ⬆️ Máximo: {AD.d_report["limit"]["max"]}
                ⬇️ Mínimo: {AD.d_report["limit"]["min"]}
                """
            await context.bot.send_message(chat_id=update.effective_chat.id, text=mensaje)
        else:
            await context.bot.send_message(chat_id=update.effective_chat.id, text="no hay señal")

        
        count += 1

        if count > 6:
            flag = False

        time.sleep(300)
    
    await context.bot.send_message(chat_id=update.effective_chat.id, text="✅ fin")


async def informarvip(update: Update, context: ContextTypes.DEFAULT_TYPE)  -> None:
    await context.bot.send_message(chat_id=update.effective_chat.id, text="comenzando informar VIP")
    count = 0
    flag = True

    while flag:
        await context.bot.send_message(chat_id=update.effective_chat.id, text="actualizando datos VIP")

        AD.actualizar()
        AD.verify_trigger(umbral_trigger = 8)

        type = "🐢 sideways"

        if AD.d_report["type"].lower() == "bull":
            type = "🐂 BULL"
        elif AD.d_report["type"].lower() == "bear":
            type = "🐻 BEAR"


        if AD.d_report["trigger"]:
            tipo_signal = type
            mensaje = f"""
                🚨 ALERTA DE TRADING 🚨

                📊 Tipo de Señal: {tipo_signal}
                ---------------------------------
                🎯 Referencia:
                💰 Valor: {AD.d_report["ref"]["value"]}
                ⌚ Fecha: {AD.d_report["ref"]["date"]}
                📐 Distancia: {AD.d_report["ref"]["distance"]}
                📏 Distancia: {AD.d_report["ref"]["distance_limit"]}
   
                ---------------------------------
                📈 Geneal
                🐂 BULL {AD.d_report["relation_general"].get("bull",0)} | 🐻 BEAR {AD.d_report["relation_general"].get("bear",0)}
                📊 Media: {AD.d_report["general"]["mean"]}
                ⬆️ Máximo: {AD.d_report["general"]["max"]}
                ⬇️ Mínimo: {AD.d_report["general"]["min"]}
                ---------------------------------
                📉 Limitado
                🐂 BULL {AD.d_report["relation_limit"].get("bull",0)} | 🐻 BEAR {AD.d_report["relation_limit"].get("bear",0)}
                📊 Media: {AD.d_report["limit"]["mean"]}
                ⬆️ Máximo: {AD.d_report["limit"]["max"]}
                ⬇️ Mínimo: {AD.d_report["limit"]["min"]}
                """
            await context.bot.send_message(chat_id=update.effective_chat.id, text=mensaje)
        else:
            await context.bot.send_message(chat_id=update.effective_chat.id, text="no hay señal")

        
        count += 1

        if count > 6:
            flag = False

        time.sleep(300)
    
    await context.bot.send_message(chat_id=update.effective_chat.id, text="✅ fin")


async def echo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text if update.message else update.channel_post.text
    await context.bot.send_message(chat_id=update.effective_chat.id, text=text)

if __name__ == '__main__':

    token = os.getenv("TOKEN_TELEGRAM")

    app = ApplicationBuilder().token(token).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("inicio", inicio))
    app.add_handler(CommandHandler("actualizar", actualizar))
    app.add_handler(CommandHandler("informar", informar))
    app.add_handler(CommandHandler("informarvip", informarvip))
    app.add_handler(MessageHandler(filters.TEXT & (~filters.COMMAND), echo))

    app.run_polling()

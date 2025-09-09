#!/usr/bin/env python3

# Librerías
import json
import logging
from websocket import WebSocketApp
from pymongo import MongoClient, errors
import os
from dotenv import load_dotenv

# Configuración de logging
#logging.basicConfig(level=logging.INFO)

# Configuración de la base de datos
MONGO_URI = os.getenv("URI_MONGO")
DB_NAME = os.getenv("DB_ACTUALLY")
COLLECTION_NAME = f"{os.getenv("NAME_COIN")}_actual"
WEB_SOCKET_BINANCE = os.getenv("WEB_SOCKET_BINANCE")

# Conexión a la base de datos
try:
    con = MongoClient(MONGO_URI)
    con.admin.command('ping')  # Verificar conexión con ping
    db = con[DB_NAME]
    col = db[COLLECTION_NAME]
    logging.info("Conexión a MongoDB establecida y verificada con ping.")
except errors.ConnectionFailure as e:
    logging.error(f"Error al conectar a MongoDB: {e}")
    exit(1)

# Obtener data
def on_message(ws, msg):
    try:
        tick = json.loads(msg)
        if tick['k']['x']:  # Verifica si el kline está cerrado
            col.insert_one(tick['k'])
            #logging.info(f"Datos insertados: {tick['k']}")
    except json.JSONDecodeError as e:
        logging.error(f"Error al decodificar el mensaje JSON: {e}")

def on_error(ws, error):
   logging.error(f"Error en la WebSocket de Binance: {error}")

def on_close(ws):
   logging.info("Conexión WebSocket cerrada.")

def on_open(ws):
   logging.info("Conexión WebSocket abierta.")


def main():
    # Run app
    ws = WebSocketApp(
        WEB_SOCKET_BINANCE,
        on_message=on_message,
        on_error=on_error,
        on_close=on_close
    )

    # Iniciar la conexión WebSocket
    ws.run_forever()


if __name__ == "__main__":
    main()
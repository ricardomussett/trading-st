# 🚀 Sistema de Trading Inteligente con IA

Un sistema completo de análisis de trading de criptomonedas que utiliza **análisis de patrones históricos** con **ChromaDB** para búsqueda vectorial, **MongoDB** para almacenamiento de datos, y **Telegram Bot** para notificaciones en tiempo real.

## 📋 Características Principales

- 🔄 **Recolección de datos en tiempo real** desde Binance WebSocket
- 🧠 **Análisis de patrones históricos** usando búsqueda vectorial con ChromaDB
- 📊 **Análisis técnico avanzado** con indicadores personalizados
- 🤖 **Bot de Telegram** para alertas y notificaciones
- 📈 **Visualización de gráficos** con mplfinance y plotly
- 🐳 **Despliegue con Docker** para fácil configuración
- 📱 **Alertas inteligentes** con umbrales configurables

## 🏗️ Arquitectura del Sistema

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Binance WS    │───▶│   MongoDB       │───▶│   ChromaDB      │
│   (Datos RT)    │    │   (Histórico)   │    │   (Vectores)    │
└─────────────────┘    └─────────────────┘    └─────────────────┘
                                │
                                ▼
                       ┌─────────────────┐
                       │  Telegram Bot   │
                       │  (Alertas)      │
                       └─────────────────┘
```

## 🛠️ Tecnologías Utilizadas

### Backend
- **Python 3.x** - Lenguaje principal
- **MongoDB** - Base de datos para datos históricos y actuales
- **ChromaDB** - Base de datos vectorial para análisis de patrones
- **WebSocket** - Conexión en tiempo real con Binance

### Análisis y Visualización
- **pandas** - Manipulación de datos
- **numpy** - Cálculos numéricos
- **mplfinance** - Gráficos de velas japonesas
- **plotly** - Visualizaciones interactivas
- **matplotlib** - Gráficos personalizados

### Bot y Notificaciones
- **python-telegram-bot** - Bot de Telegram
- **python-dotenv** - Gestión de variables de entorno

### Despliegue
- **Docker** - Containerización
- **Docker Compose** - Orquestación de servicios

## 🚀 Instalación y Configuración

### Prerrequisitos
- Docker y Docker Compose
- Token de Telegram Bot
- Cuenta de Binance (para datos públicos)

### 1. Clonar el repositorio
```bash
git clone <tu-repositorio>
cd trading-st
```

### 2. Configurar variables de entorno
Crea un archivo `.env` en la raíz del proyecto:

```env
# Base de datos MongoDB
URI_MONGO=mongodb://admin:adminpassword@mongodb:27017/
HOST_MONGODB=mongodb://admin:adminpassword@mongodb:27017/

# ChromaDB
HOST_CHROMADB_IP=chromadb
HOST_CHROMADB_PORT=8000

# Configuración de la criptomoneda
NAME_COIN=wif
DB_HISTORY=cripto
DB_ACTUALLY=cripto

# Telegram Bot
TOKEN_TELEGRAM=tu_token_aqui

# Binance WebSocket
WEB_SOCKET_BINANCE=wss://stream.binance.com:9443/ws/wifusdt@kline_1m
```

### 3. Ejecutar con Docker Compose
```bash
docker-compose up -d
```

## 📊 Funcionalidades del Sistema

### 🔄 Recolección de Datos (`binance_ws/`)
- Conexión WebSocket en tiempo real con Binance
- Almacenamiento automático de velas de 1 minuto
- Manejo de errores y reconexión automática

### 🧠 Análisis Inteligente (`bot_telegram/fun.py`)
- **Normalización de datos** para análisis comparativo
- **Búsqueda vectorial** de patrones históricos similares
- **Análisis de progresión** con indicadores personalizados
- **Detección de señales** Bull/Bear/Sideways
- **Generación de reportes** con métricas detalladas

### 🤖 Bot de Telegram (`bot_telegram/`)
- **Comandos disponibles:**
  - `/start` - Iniciar el bot
  - `/inicio` - Cargar datos históricos
  - `/actualizar` - Actualizar análisis
  - `/informar` - Generar reporte completo
  - `/informarvip` - Alertas VIP con umbrales estrictos

### 📈 Análisis de Patrones
El sistema utiliza un enfoque innovador:

1. **Normalización** de precios actuales
2. **Búsqueda vectorial** en patrones históricos
3. **Análisis de progresión** de los patrones encontrados
4. **Cálculo de probabilidades** Bull/Bear
5. **Generación de alertas** basadas en umbrales

## 🎯 Tipos de Señales

### 🐂 Señal BULL
- Patrones históricos muestran tendencia alcista
- Umbral configurable de casos positivos
- Distancia mínima entre patrones

### 🐻 Señal BEAR  
- Patrones históricos muestran tendencia bajista
- Análisis de soportes y resistencias
- Predicción de caídas de precio

### 🐢 Señal SIDEWAYS
- Mercado lateral sin tendencia clara
- Patrones mixtos o insuficientes

## 📱 Comandos del Bot

| Comando | Descripción |
|---------|-------------|
| `/start` | Iniciar conversación con el bot |
| `/inicio` | Cargar datos históricos de la criptomoneda |
| `/actualizar` | Actualizar análisis con datos recientes |
| `/informar` | Generar reporte completo (6 ciclos) |
| `/informarvip` | Alertas VIP con umbrales estrictos |

## 🔧 Configuración Avanzada

### Umbrales de Alerta
```python
# En el código del bot
AD.verify_trigger(
    umbral_trigger=10,    # Mínimo de casos para señal
    umbral_distance=1.2   # Distancia máxima entre patrones
)
```

### Parámetros de Análisis
- **Velas de análisis**: 60 velas actuales
- **Patrones históricos**: 120 velas por patrón
- **Resultados vectoriales**: 15 patrones más similares
- **Intervalo de actualización**: 5 minutos

## 📊 Estructura de Datos

### MongoDB Collections
- `{coin}_actual` - Datos actuales de velas
- `{coin}` - Datos históricos completos

### ChromaDB
- Vectores normalizados de patrones de precios
- Búsqueda por similitud coseno
- Metadatos de timestamps y distancias

## 🐳 Servicios Docker

| Servicio | Puerto | Descripción |
|----------|--------|-------------|
| `mongodb` | 27017 | Base de datos principal |
| `chromadb` | 8000 | Base de datos vectorial |
| `binance-ws` | - | Recolector de datos |
| `telegram-bot` | - | Bot de notificaciones |

## 📈 Ejemplo de Salida

```
🚨 ALERTA DE TRADING 🚨

📊 Tipo de Señal: 🐂 BULL
---------------------------------
🎯 Referencia:
💰 Valor: 0.1234
⌚ Fecha: 2024-01-15 14:30:00
📐 Distancia: 0.85

---------------------------------
📈 General
🐂 BULL 12 | 🐻 BEAR 3
📊 Media: 0.1456
⬆️ Máximo: 0.1789
⬇️ Mínimo: 0.1123
```

## 🤝 Contribución

1. Fork el proyecto
2. Crea una rama para tu feature (`git checkout -b feature/AmazingFeature`)
3. Commit tus cambios (`git commit -m 'Add some AmazingFeature'`)
4. Push a la rama (`git push origin feature/AmazingFeature`)
5. Abre un Pull Request

## 📝 Licencia

Este proyecto está bajo la Licencia MIT - ver el archivo [LICENSE](LICENSE) para detalles.

## ⚠️ Disclaimer

Este software es solo para fines educativos y de investigación. El trading de criptomonedas conlleva riesgos significativos. No se garantiza la precisión de las señales generadas. Siempre haz tu propia investigación antes de tomar decisiones de trading.

## 📞 Soporte

Para soporte o preguntas, abre un issue en el repositorio o contacta al desarrollador.

---

**¡Desarrollado con ❤️ para la comunidad de trading!**

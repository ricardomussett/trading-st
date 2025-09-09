FROM python:3.11-slim

# Establecer el directorio de trabajo
WORKDIR /app

# Copiar los archivos de requerimientos
COPY requeriments.txt .

# Instalar las dependencias
RUN pip install --no-cache-dir -r requeriments.txt

# Copiar el código fuente
COPY  04_bot_telegram.py .
COPY fun.py .

# Comando para ejecutar el bot
CMD ["python", "04_bot_telegram.py"] 
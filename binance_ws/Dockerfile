FROM python:3.12-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY 03_ws_binance.py .

CMD ["python", "03_ws_binance.py"] 
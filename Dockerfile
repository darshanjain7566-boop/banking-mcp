FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

# The app reads $PORT at runtime (Render/HF inject it). Default 8000 locally.
EXPOSE 8000

CMD ["python", "core_banking_mcp.py"]

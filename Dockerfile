FROM python:3.11-slim

# Instalar dependencias del sistema
RUN apt-get update && apt-get install -y \
    poppler-utils \
    tesseract-ocr \
    && rm -rf /var/lib/apt/lists/*

# Crear directorio de trabajo
WORKDIR /app

# Copiar backend dentro de /app/backend
COPY backend/ /app/backend/

# Instalar dependencias
RUN pip install --no-cache-dir -r /app/backend/requirements.txt

# Exponer el puerto
EXPOSE 8000

# Comando de inicio
CMD ["uvicorn", "backend.main:app", "--host", "0.0.0.0", "--port", "8000"]

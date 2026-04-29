FROM python:3.11-slim

# Instalar dependencias del sistema necesarias para pdf2image y pytesseract
RUN apt-get update && apt-get install -y \
    poppler-utils \
    tesseract-ocr \
    && rm -rf /var/lib/apt/lists/*

# Directorio de trabajo
WORKDIR /app

# Copiar requirements del backend
COPY backend/requirements.txt /app/requirements.txt

# Instalar dependencias de Python
RUN pip install --no-cache-dir -r requirements.txt

# Copiar SOLO el backend (no frontend, no venv, no node_modules)
COPY backend/ /app/

# Exponer puerto
EXPOSE 8000

# Entrar al backend y ejecutar FastAPI
WORKDIR /app
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]

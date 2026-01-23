# Imagen base de Python
FROM python:3.11-slim

# Carpeta de trabajo dentro del contenedor
WORKDIR /app

# Copiar dependencias e instalarlas
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copiar todo el proyecto
COPY . .

# Exponer el puerto
EXPOSE 8000

# Comando de inicio: ahora apunta a tu carpeta agente_abogado
CMD ["uvicorn", "agente_abogado.main:app", "--host", "0.0.0.0", "--port", "8000"]
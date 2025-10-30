# Usar imagen base de Python
FROM python:3.11-slim

# Establecer directorio de trabajo
WORKDIR /app

# Instalar dependencias del sistema
RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    && rm -rf /var/lib/apt/lists/*

# Copiar archivos de dependencias
COPY requirements.txt requirements-dev.txt ./

# Instalar dependencias de Python
RUN pip install --no-cache-dir -r requirements.txt

# Copiar código fuente
COPY src/ ./src/
COPY config/ ./config/

# Crear directorios necesarios
RUN mkdir -p logs data

# Crear usuario no-root para seguridad
RUN useradd -m -u 1000 mcpuser && chown -R mcpuser:mcpuser /app
USER mcpuser

# Exponer puertos
EXPOSE 8000 8501

# Variables de entorno por defecto
ENV PYTHONPATH=/app
ENV LOG_LEVEL=INFO
ENV SERVER_PORT=8000
ENV STREAMLIT_PORT=8501

# Comando por defecto (ejecutar ambos servicios)
CMD ["sh", "-c", "streamlit run src/frontend/app.py --server.port 8501 --server.address 0.0.0.0 & python -m src.mcp_server.main"]
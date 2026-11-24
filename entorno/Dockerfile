# Imagen para cargar datos (seed) y correr consultas (cli). Se construye desde la raíz del repo
# (ver docker-compose.yml: context ..) y replica su estructura dentro de /app.
FROM python:3.12-slim
WORKDIR /app
RUN pip install --no-cache-dir "pymongo>=4.8,<5" "json5>=0.9"
COPY python/ python/
COPY entorno/*.py entorno/

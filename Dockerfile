FROM python:3.10-slim

WORKDIR /app

# Instalar o Docker Compose
RUN apt-get update && apt-get install -y docker-compose

COPY . .

# Expor as portas necessárias
EXPOSE 8000 8501 8001

# Comando para iniciar os serviços
CMD ["docker-compose", "up"]

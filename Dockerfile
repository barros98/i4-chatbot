FROM python:3.10-slim

WORKDIR /app

# Instalar curl para healthcheck
RUN apt-get update && apt-get install -y curl

# Copiar arquivos do backend
COPY api/requirements.txt .
COPY api/main.py .
COPY api/langchain_utils.py .
COPY api/chroma_utils.py .
COPY api/db_utils.py .
COPY api/pydantic_models.py .

# Instalar dependências
RUN pip install --no-cache-dir -r requirements.txt

# Expor a porta do backend
EXPOSE 8000

# Comando para iniciar o backend
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]

# Usa imagem oficial do Python
FROM python:3.10-slim

# Define diretório de trabalho
WORKDIR /app

# Copia tudo da pasta local para dentro do container
COPY . .

# Instala dependências
RUN pip install --no-cache-dir -r requirements.txt

# Expõe a porta usada pelo FastAPI
EXPOSE 8000

# Comando para iniciar a API
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]

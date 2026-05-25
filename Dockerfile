FROM python:3.11-slim

# Dependências do sistema necessárias para compilar alguns pacotes
RUN apt-get update && apt-get install -y \
    build-essential \
    gcc \
    curl \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Copia e instala dependências primeiro (cache do Docker)
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Baixa modelo do spaCy
RUN python -m spacy download pt_core_news_sm

# Baixa modelo do CrossEncoder (sentence-transformers faz cache automático)
RUN python -c "from sentence_transformers import CrossEncoder; CrossEncoder('cross-encoder/ms-marco-MiniLM-L-6-v2')"

# Copia o código
COPY main.py .
COPY frontend/ ./frontend/

# Cria pastas necessárias
RUN mkdir -p user_data docs

# Porta exposta
EXPOSE 8000

# Health check
HEALTHCHECK --interval=30s --timeout=10s --retries=3 \
  CMD curl -f http://localhost:8000/docs || exit 1

# Inicia o servidor
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]

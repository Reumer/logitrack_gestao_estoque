# Usa uma imagem oficial leve do Python
FROM python:3.11-slim

# Define o diretório de trabalho dentro do container
WORKDIR /app

# Instala dependências do sistema necessárias para compilar bibliotecas se preciso
RUN apt-get update && apt-get install -y \
    gcc \
    default-libmysqlclient-dev \
    pkg-config \
    && rm -rf /var/lib/apt/lists/*

# Copia e instala as dependências do projeto
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copia todo o código fonte para dentro do container
COPY . .

# Expõe as portas usadas pela API (8000) e pelo Streamlit (8501)
EXPOSE 8000
EXPOSE 8501

# Comando padrão para manter o container pronto
CMD ["uvicorn", "api:app", "--host", "0.0.0.0", "--port", "8000"]

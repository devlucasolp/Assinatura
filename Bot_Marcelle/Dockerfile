# Usa uma imagem oficial do Python otimizada
FROM python:3.12-slim

# Define o diretório de trabalho dentro do container
WORKDIR /app

# Instala dependências do sistema necessárias
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# Copia os arquivos de requisitos primeiro (aproveita cache do Docker)
COPY requirements.txt .

# Instala as dependências Python
RUN pip install --no-cache-dir -r requirements.txt

# Copia o restante do código da aplicação
COPY . .

# Expõe a porta padrão do Easypanel (geralmente 80)
EXPOSE 80

# Inicia a aplicação usando a variável $PORT do Easypanel (ou 80 como padrão)
CMD sh -c "uvicorn main:app --host 0.0.0.0 --port ${PORT:-80} --proxy-headers"
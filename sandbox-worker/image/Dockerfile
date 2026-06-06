# Imagem base da sandbox de execução.
# Slim + libs científicas comuns + cliente HTTP.
# Sem shell utilities, sem pip em runtime, user não-root.
FROM python:3.12-slim

# Dependências necessárias para numpy/pandas/matplotlib funcionarem corretamente
RUN apt-get update && apt-get install -y --no-install-recommends \
        libgomp1 \
        libstdc++6 \
    && rm -rf /var/lib/apt/lists/*

# Libs disponíveis para o código executado
RUN pip install --no-cache-dir \
        numpy==2.1.3 \
        pandas==2.2.3 \
        matplotlib==3.10.0 \
        scipy==1.14.1 \
        httpx==0.28.1 \
        requests==2.32.3 \
        python-dateutil==2.9.0 \
        pytz==2024.2

# sitecustomize.py — injetado automaticamente, adiciona X-Sandbox-Instance em todos requests
COPY sitecustomize.py /usr/local/lib/python3.12/site-packages/sitecustomize.py

# Remove pip (não queremos instalações em runtime dentro da sandbox)
RUN python -m pip uninstall -y pip setuptools wheel || true

# User sem privilégios
RUN useradd --create-home --shell /usr/sbin/nologin sandbox
USER sandbox
WORKDIR /sandbox

# Matplotlib precisa de cache writeable; usaremos tmpfs em /tmp
ENV MPLCONFIGDIR=/tmp/.matplotlib \
    HOME=/tmp/.home \
    PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

# Não tem CMD — o worker monta o comando: timeout Ns python /tmp/run.py

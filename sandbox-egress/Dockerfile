# Egress proxy — HTTP/HTTPS forward proxy com allow-list dinâmica via Rails.
FROM python:3.12-slim

WORKDIR /app

RUN pip install --no-cache-dir httpx==0.28.1

COPY proxy.py ./

EXPOSE 8888

CMD ["python", "proxy.py"]

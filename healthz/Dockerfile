FROM python:3.11-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

RUN groupadd -g 10001 app && useradd -u 10001 -g 10001 -m app

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY app.py .

USER 10001

ENV SERVICE_NAME=healthz \
    SERVICE_PORT=6000 \
    CONSUL_HOST=consul \
    CONSUL_PORT=8500

EXPOSE 6000

HEALTHCHECK --interval=5s --timeout=2s --retries=5 --start-period=5s \
  CMD python -c "import urllib.request; urllib.request.urlopen('http://127.0.0.1:6000/health', timeout=1)" || exit 1

CMD ["python", "app.py"]

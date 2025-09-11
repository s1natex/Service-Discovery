FROM python:3.11-slim
ENV PYTHONDONTWRITEBYTECODE=1 PYTHONUNBUFFERED=1
RUN groupadd -g 10001 app && useradd -u 10001 -g 10001 -m app
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY app.py .
RUN chown -R app:app /app
USER 10001
EXPOSE 8000
HEALTHCHECK --interval=5s --timeout=2s --retries=5 --start-period=5s CMD python -c "import urllib.request; urllib.request.urlopen('http://127.0.0.1:8000/services', timeout=1)" || exit 1
CMD ["python", "app.py"]

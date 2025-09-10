FROM python:3.11-slim

WORKDIR /app

COPY app.py .

RUN pip install --no-cache-dir flask requests

EXPOSE 5000

HEALTHCHECK --interval=5s --timeout=2s --retries=5 --start-period=5s \
  CMD python -c "import urllib.request; urllib.request.urlopen('http://localhost:5000/info', timeout=1)" || exit 1

CMD ["python", "app.py"]

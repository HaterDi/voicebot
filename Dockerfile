FROM mcr.microsoft.com/devcontainers/python:3.11
WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY . .
CMD ["gunicorn", "-k", "aiohttp.worker.GunicornWebWorker", "app:app", "--bind", "0.0.0.0:${PORT:-8000}"]

FROM mcr.microsoft.com/playwright/python:v1.52.0-noble

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY passabot/ ./passabot/

WORKDIR /app/passabot

EXPOSE 8000

CMD ["python", "run.py"]

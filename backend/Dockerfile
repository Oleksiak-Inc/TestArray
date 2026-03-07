FROM python:3.12-slim

WORKDIR /app

# System dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    postgresql-client \
    && rm -rf /var/lib/apt/lists/*

# Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# App code
COPY . .

# Expose port from env
EXPOSE 8000

# Run Uvicorn using env variables
CMD ["sh", "-c", "uvicorn run:app --host 0.0.0.0 --port ${SERVER_PORT}"]
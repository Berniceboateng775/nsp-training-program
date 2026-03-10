FROM python:3.12-slim

WORKDIR /app

# Install system deps (ca-certificates needed for MongoDB Atlas SSL)
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    g++ \
    ca-certificates \
    && rm -rf /var/lib/apt/lists/*

# Install CPU-only PyTorch first (saves ~3GB vs full CUDA version)
RUN pip install --no-cache-dir torch --index-url https://download.pytorch.org/whl/cpu

# Install remaining Python deps
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt certifi

# Copy app code
COPY . .

# Render uses PORT env var
ENV PORT=8000
EXPOSE 8000

CMD uvicorn main:app --host 0.0.0.0 --port $PORT

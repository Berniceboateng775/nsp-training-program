FROM python:3.12-slim

WORKDIR /app

# Install system deps
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# Install CPU-only PyTorch first (saves ~3GB vs full CUDA version)
RUN pip install --no-cache-dir torch --index-url https://download.pytorch.org/whl/cpu

# Install remaining Python deps
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Pre-download model from HuggingFace at build time (caches in image)
RUN python -c "from transformers import GPT2ForSequenceClassification, GPT2Tokenizer; \
    GPT2Tokenizer.from_pretrained('Bernice775/vellichor'); \
    GPT2ForSequenceClassification.from_pretrained('Bernice775/vellichor')"

# Copy app code
COPY app.py .

# Render uses PORT env var
ENV PORT=8000
EXPOSE 8000

CMD ["python", "app.py"]

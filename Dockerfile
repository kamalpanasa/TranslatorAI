# Use official Python runtime as base image
FROM python:3.10-slim-bookworm

# Prevent Python from writing pyc files and buffering stdout/stderr
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# Set workspace directory
WORKDIR /app

# Install system dependencies for audio (FFmpeg, libsndfile1) and OCR (Tesseract)
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    ffmpeg \
    tesseract-ocr \
    libsndfile1 \
    git \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# Install python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# Create necessary directories for local storage and temp uploads
RUN mkdir -p /app/temp /app/exports

# Copy application source code
COPY . .

# Expose API application port (Hugging Face Spaces requires port 7860)
EXPOSE 7860

# Set environment variables for OCR binary mapping inside linux container
ENV TESSERACT_CMD="tesseract"

# Launch application
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "7860"]

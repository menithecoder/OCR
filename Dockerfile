# Use the correct Python version
FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Copy app files
COPY . /app

# Install system dependencies for Tesseract
RUN apt-get update && apt-get install -y \
    tesseract-ocr \
    libtesseract-dev \
    tesseract-ocr-heb \
    libleptonica-dev \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Expose port (if needed)
EXPOSE 8000

# Run the app
CMD ["python", "main.py"]

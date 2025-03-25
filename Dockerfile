# Use the correct Python version
FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Copy app files
COPY . /app

# Install system dependencies for Tesseract and Hebrew OCR support
RUN apt-get update && apt-get install -y \
    tesseract-ocr \
    libtesseract-dev \
    tesseract-ocr-heb \
    libleptonica-dev \
    build-essential \
    wget \
    && rm -rf /var/lib/apt/lists/*

# Set Tesseract OCR data path
ENV TESSDATA_PREFIX="/usr/share/tesseract-ocr/5/tessdata/"

# Ensure Hebrew language data is present
RUN wget -O ${TESSDATA_PREFIX}heb.traineddata \
    https://github.com/tesseract-ocr/tessdata_best/raw/main/heb.traineddata

# Install Python dependencies (if requirements.txt exists)
RUN test -f requirements.txt && python -m pip install --no-cache-dir -r requirements.txt || echo "No requirements.txt found."

# Expose port (if needed)
EXPOSE 8000

# Run the app
CMD ["python", "main.py"]


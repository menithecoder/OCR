# Use an official Python runtime as a base image
FROM python:3.9-slim

# Set the working directory in the container
WORKDIR /app

# Copy the current directory contents into the container at /app
COPY . /app

# Install system dependencies for Tesseract OCR and Hebrew language support
RUN apt-get update && apt-get install -y \
    tesseract-ocr \
    libtesseract-dev \
    tesseract-ocr-heb

# Install any necessary Python dependencies from requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# Expose port (if needed for your app)
EXPOSE 8000
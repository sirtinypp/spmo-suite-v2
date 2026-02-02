# Use a lightweight Python version
FROM python:3.10-slim

# Prevent Python from writing temporary files to disc
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

WORKDIR /app

# Install system tools
# ADDED: pkg-config and libcairo2-dev (Required for xhtml2pdf/PDF generation)
RUN apt-get update && apt-get install -y \
    libpq-dev \
    gcc \
    pkg-config \
    libcairo2-dev

# Install dependencies
COPY requirements.txt /app/
RUN pip install --no-cache-dir -r requirements.txt

# Copy project code
COPY . /app/
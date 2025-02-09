# Use Python 3.11 slim image as base
FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Install system dependencies required for matplotlib and other packages
RUN apt-get update && apt-get install -y \
    build-essential \
    python3-dev \
    && rm -rf /var/lib/apt/lists/*

# Create cache directory for FastF1 with proper permissions
RUN mkdir -p /cache/fastf1 && \
    chmod 777 /cache/fastf1

RUN apt-get update && apt-get install -y redis-server \
    && rm -rf /var/lib/apt/lists/*


# Set environment variable for FastF1 cache
ENV FASTF1_CACHE_DIR=/cache/fastf1

# Copy requirements first to leverage Docker cache
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of the application
COPY . .

# Expose port 5000
EXPOSE 5000

# Run the application
CMD ["gunicorn", "--bind", "0.0.0.0:5000", "app:app"]
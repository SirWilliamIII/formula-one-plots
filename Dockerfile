# Use Python 3.11.11 slim image as base
FROM python:3.11.11-slim

# Set working directory
WORKDIR /app

# Set environment variables
ENV FASTF1_CACHE_DIR=/app/cache/fastf1
ENV ENV=docker
ENV MPLCONFIGDIR=/app/cache/matplotlib

# Install system dependencies required for matplotlib and other packages
RUN apt-get update && apt-get install -y \
    build-essential \
    python3-dev \
    && rm -rf /var/lib/apt/lists/*

# Create cache directories with proper permissions
RUN mkdir -p /app/cache/fastf1 && \
    mkdir -p /app/cache/matplotlib && \
    chmod 777 /app/cache/fastf1 && \
    chmod 777 /app/cache/matplotlib

RUN apt-get update && apt-get install -y redis-server \
    && rm -rf /var/lib/apt/lists/*


# Set environment variable for FastF1 cache
ENV FASTF1_CACHE_DIR=/app/cache/fastf1

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

# After creating workdir
WORKDIR /app
RUN chown -R nobody:nogroup /app
USER nobody
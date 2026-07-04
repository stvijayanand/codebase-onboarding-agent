# Use an official Python runtime as a base image
FROM python:3.11-slim

# Install system dependencies (specifically git)
RUN apt-get update && apt-get install -y --no-install-recommends \
    git \
    && rm -rf /var/lib/apt/lists/*

# Set the working directory in the container
WORKDIR /app

# Copy requirements and install
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy source code
COPY src/ ./src/
COPY onboard.py .

# Expose port (Cloud Run defaults to 8080)
EXPOSE 8080

# Environment variables configuration
ENV PORT=8080
ENV PYTHONUNBUFFERED=1

# Run the FastAPI server by default
CMD ["python", "src/server.py"]

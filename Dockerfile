FROM python:3.11-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    postgresql-client \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements
COPY requirements.txt .

# Install Python dependencies
RUN pip install --default-timeout=1000 --no-cache-dir -r requirements.txt

# Copy application code
COPY backend/ ./backend/

# Set environment variables
ENV PYTHONUNBUFFERED=1
ENV DATABASE_URL=postgresql://user:password@postgres:5432/insider_threat_saas

# Expose port
EXPOSE 8000

# Run Sentinel AI application
CMD ["uvicorn", "backend.main:app", "--host", "0.0.0.0", "--port", "8000"]

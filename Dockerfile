"""
Docker configuration for WhatsApp Analyzer
Allows running the application in a container
"""

# Use Python 3.9 slim image
FROM python:3.9-slim

# Set working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first for better caching
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Download NLTK data
RUN python -c "import nltk; nltk.download('punkt'); nltk.download('stopwords'); nltk.download('vader_lexicon')"

# Copy application code
COPY . .

# Create necessary directories
RUN mkdir -p reports temp exports

# Expose ports
EXPOSE 8501 8000

# Default command (can be overridden)
CMD ["sh", "-c", "streamlit run app.py --server.port 8501 --server.address 0.0.0.0 & python -m uvicorn api:app --host 0.0.0.0 --port 8000"]

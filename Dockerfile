FROM python:3.11-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    build-essential \
    netcat-traditional \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first to leverage Docker cache
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of the application
COPY . .

# Install the package in development mode
RUN pip install -e .

# Make the startup script executable
RUN chmod +x start.sh

# Expose ports for both FastAPI and Streamlit
EXPOSE 8000 8501

# Command to run the startup script
CMD ["./start.sh"] 
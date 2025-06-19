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

# Expose ports for both FastAPI and Streamlit
EXPOSE 8000 8501

# Command to run the startup script
CMD sh -c '\
  echo "Waiting for database to be ready..." && \
  while ! nc -z postgres 5432; do sleep 1; done && \
  echo "Database is ready!" && \
  echo "Initializing database..." && \
  python -m src.app.db.init_db && \
  echo "Starting services..." && \
  uvicorn src.app.app:app --host 0.0.0.0 --port 8000 & \
  streamlit run src/app/demo/demo.py --server.address 0.0.0.0' 
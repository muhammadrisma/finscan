#!/bin/sh

# Wait for database to be ready
echo "Waiting for database to be ready..."
while ! nc -z postgres 5432; do
  sleep 1
done
echo "Database is ready!"

# Initialize database
echo "Initializing database..."
python -m src.app.db.init_db

# Start services
echo "Starting services..."
uvicorn src.app.app:app --host 0.0.0.0 --port 8000 &
streamlit run src/app/demo/demo.py --server.address 0.0.0.0 
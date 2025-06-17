# FinScan

FinScan is a powerful financial scanning and analysis tool built with Python, leveraging LangChain and modern AI technologies to provide intelligent financial insights. It helps users analyze financial data, generate reports, and make data-driven decisions using advanced AI capabilities.

## Features

- 🤖 AI-powered financial analysis and insights
- 🚀 FastAPI backend for robust API endpoints
- 💻 Modern web interface using Streamlit
- 🗄️ PostgreSQL database integration
- ⚙️ Environment-based configuration
- 📊 Real-time financial data processing
- 🔍 Advanced search and filtering capabilities
- 📈 Customizable reporting and analytics

## Prerequisites

- Docker and Docker Compose
- OpenAI API key (for LangChain integration)

## Installation

1. Clone the repository:
```bash
git clone https://github.com/yourusername/finscan.git
cd finscan
```

2. Set up environment variables:
Create a `.env` file in the project root with the following variables:
```env
OPENROUTER_API_KEY=your_api_key_here
OPENROUTER_API_BASE=your_api_base_url_here
DATABASE_URL = "postgresql+psycopg2://postgres:postgres@localhost:5432/fishdb"
```

3. Start the application:
```bash
# Build and start all services
docker-compose up --build

# Or run in detached mode
docker-compose up -d --build
```

The application will be available at:
- Streamlit UI: http://localhost:8501
- PostgreSQL Database:
  - Host: localhost
  - Port: 5432
  - Database: fishdb
  - Username: postgres
  - Password: postgres

## Development Setup

If you prefer to run the application locally without Docker:

1. Create and activate a virtual environment:
```bash
# Using conda
conda create -n finscan python=3.11 -y
conda activate finscan

# OR using venv
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

2. Install the package:
```bash
pip install -e .
```

3. Install requirements:
```bash
make install
```

4. Start the database:
```bash
docker-compose up -d postgres
```

5. Initialize the database:
```bash
make up-db
```

6. Run the application:
```bash
# Run Streamlit UI
make streamlit

# Or run FastAPI backend
make run
```

## Database Management

The following Make commands are available for database management:

```bash
# Initialize database tables
make up-db

# Drop all database tables
make down-db

# Reset database (drop and recreate)
make reset-db
```

## Usage
1. Run postgresql docker container

2. Start the development server:
```bash
make run
```

3. Access the web interface at `http://localhost:8000`

## Available Commands

The project includes several useful Makefile commands to help with development:

```bash
# Install project dependencies
make install

# Database Management
make up-db      # Initialize the database
make down-db    # Drop the database
make reset-db   # Reset the database (drop and recreate)

# Running the Application
make run        # Start the FastAPI server (http://localhost:8000)
make streamlit  # Launch the Streamlit demo interface
```

## API Endpoints

The application provides the following REST API endpoints:

### Processing Logs
- `POST /api/processing/log` - Create a new processing log
- `GET /api/processing/logs` - Get all processing logs
- `GET /api/processing/log/{log_id}` - Get a specific processing log
- `DELETE /api/processing/log/{log_id}` - Delete a processing log

### Result Logs
- `POST /api/result/log` - Create a new result log with agent agreement check
- `GET /api/result/logs` - Get all result logs
- `GET /api/result/log/{log_id}` - Get a specific result log
- `DELETE /api/result/log/{log_id}` - Delete a result log

### Audit & Cache
- `GET /api/audit/latest` - Get the latest audit log with current counts
- `GET /api/cache/logs` - Get all cache logs

All endpoints return JSON responses and use standard HTTP status codes:
- 200: Success
- 404: Resource not found
- 500: Server error
# FinScan

FinScan is a powerful financial scanning and analysis tool built with Python, leveraging LangChain and modern AI technologies to provide intelligent financial insights. It helps users analyze financial data, generate reports, and make data-driven decisions using advanced AI capabilities.

## Features

- 🤖 AI-powered financial analysis and insights
- 🚀 FastAPI backend for robust API endpoints
- 💻 Modern web interface using Gradio/Streamlit
- 🗄️ PostgreSQL database integration
- ⚙️ Environment-based configuration
- 📊 Real-time financial data processing
- 🔍 Advanced search and filtering capabilities
- 📈 Customizable reporting and analytics

## Prerequisites

- Python 3.8 or higher
- PostgreSQL database
- OpenAI API key (for LangChain integration)
- Docker and Docker Compose (for database setup)

## Installation

1. Clone the repository:
```bash
git clone https://github.com/yourusername/finscan.git
cd finscan
```

2. Create and activate a virtual environment (recommended):
```bash
# Using conda
conda create -n finscan python=3.10 -y
conda activate finscan

# OR using venv
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install the package:
```bash
pip install -e .
```

4. Install requirements:
```bash
make install
```

5. Set up environment variables:
Create a `.env` file in the project root with the following variables:
```env
OPENAI_API_KEY=your_api_key_here
DATABASE_URL=postgresql://postgres:postgres@localhost:5432/fishdb
```

6. Set up the database:
```bash
# Start the PostgreSQL database
docker-compose up -d

# Wait a few seconds for the database to be ready
sleep 5

# Initialize the database tables
make up-db
```

Database connection details:
- Host: localhost
- Port: 5432
- Database: fishdb
- Username: postgres
- Password: postgres

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
# FinScan

FinScan is a powerful financial scanning and analysis tool built with Python, leveraging LangChain and modern AI technologies to provide intelligent financial insights.

## Features

- AI-powered financial analysis
- FastAPI backend for robust API endpoints
- Modern web interface using Gradio/Streamlit
- PostgreSQL database integration
- Environment-based configuration

## Prerequisites

- Python 3.8 or higher
- PostgreSQL database
- OpenAI API key (for LangChain integration)

## Installation

1. Clone the repository:
```bash
git clone https://github.com/yourusername/finscan.git
cd finscan
```

2. Create and activate a virtual environment (recommended):
```bash
conda create -n finscan python=3.10 -y
conda activate finscan
```

3. Install the package:
```bash
pip install -e .
```

4. Install requirements
```bash
make install
```

5. Set up environment variables:
Create a `.env` file in the project root with the following variables:
```
OPENAI_API_KEY=your_api_key_here
DATABASE_URL=your_postgresql_connection_string
```

## Usage

1. Start the development server:
```bash
make run
```

2. Access the web interface at `http://localhost:8000`

## Development

- Source code is located in the `src/` directory
- Use `make` commands for common development tasks

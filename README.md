# Financial Insights API

A FastAPI-based service providing financial insights and stock quotes.

## Setup

1. Clone the repository:
```bash
git clone [your-repository-url]
cd [repository-name]
```

2. Create and activate a virtual environment:
```bash
python -m venv .venv
# On Windows
.venv\Scripts\activate
# On Unix or MacOS
source .venv/bin/activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Create `.env` file:
```bash
cp .env.example .env
# Edit .env with your actual values
```

5. Start the server:
```bash
# Using Python
python start_engine_room.py

# Or using provided scripts
# Windows
start.bat
# Unix/MacOS
./start.sh
```

## API Documentation

Once the server is running, visit:
- Swagger UI: http://localhost:7171/docs
- ReDoc: http://localhost:7171/redoc

## Environment Variables

- `APP_HOST`: Host to run the server on (default: 0.0.0.0)
- `APP_PORT`: Port to run the server on (default: 7171)
- `CORS_ORIGINS`: Comma-separated list of allowed origins
- `TIINGO_API_KEY`: API key for Tiingo services
- `ALPHA_VANTAGE_API_KEY`: API key for Alpha Vantage services

## License

[Your chosen license]
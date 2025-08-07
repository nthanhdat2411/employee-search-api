# Employee Search Directory API - Setup Guide

This guide will help you set up and run the Employee Search Directory API.

## 🚀 Quick Start

### Prerequisites

- Python 3.11+
- PostgreSQL 15+ (or Docker for containerized setup)
- pip (Python package manager)

### Option 1: Docker Setup (Recommended)

1. **Install Docker and Docker Compose**
   ```bash
   # Download from https://www.docker.com/products/docker-desktop
   ```

2. **Clone and run**
   ```bash
   git clone <repository-url>
   cd employee-search-api
   docker-compose up --build
   ```

3. **Access the API**
   - API: http://localhost:8000
   - Documentation: http://localhost:8000/docs
   - ReDoc: http://localhost:8000/redoc

### Option 2: Local Development Setup

1. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

2. **Set up PostgreSQL database**
   ```bash
   # Create database
   createdb employee_search_db
   
   # Set environment variable
   export DATABASE_URL="postgresql://user:password@localhost/employee_search_db"
   # On Windows:
   # set DATABASE_URL=postgresql://user:password@localhost/employee_search_db
   ```

3. **Run the application**
   ```bash
   python main.py
   ```

4. **Populate with sample data**
   ```bash
   python scripts/populate_db.py
   ```

## 🧪 Testing the API

### Quick Test
```bash
python test_run.py
```

### Using the CLI Tool
```bash
# Install requests if not already installed
pip install requests

# Check API health
python cli.py health

# Create an organization
python cli.py create-org "My Company"

# Search employees
python cli.py search --org-id 1 --search "john"

# Get available filters
python cli.py filters --org-id 1

# Check rate limiting
python cli.py rate-limit
```

### Using curl
```bash
# Health check
curl http://localhost:8000/health

# Search employees
curl -X POST http://localhost:8000/api/v1/employees/search \
  -H "Content-Type: application/json" \
  -d '{
    "organization_id": 1,
    "search": "john",
    "status": ["ACTIVE"],
    "page": 1,
    "page_size": 10
  }'

# Get available filters
curl http://localhost:8000/api/v1/organizations/1/filters

# Get rate limit info
curl http://localhost:8000/api/v1/rate-limit/info
```

## 📚 API Documentation

Once the API is running, you can access:

- **Interactive Documentation**: http://localhost:8000/docs
- **ReDoc Documentation**: http://localhost:8000/redoc
- **OpenAPI Schema**: http://localhost:8000/openapi.json

## 🏗️ Project Structure

```
employee-search-api/
├── app/
│   ├── __init__.py
│   ├── api.py              # Main API endpoints
│   ├── database.py         # Database configuration
│   ├── models.py           # SQLAlchemy models
│   ├── schemas.py          # Pydantic schemas
│   ├── services.py         # Business logic
│   └── rate_limiter.py     # Custom rate limiting
├── tests/
│   ├── __init__.py
│   └── test_api.py         # Unit tests
├── scripts/
│   ├── __init__.py
│   └── populate_db.py      # Database population script
├── main.py                 # Application entry point
├── cli.py                  # CLI tool
├── test_run.py             # Quick test script
├── requirements.txt        # Python dependencies
├── Dockerfile             # Docker configuration
├── docker-compose.yml     # Docker Compose setup
├── README.md              # Comprehensive documentation
├── SETUP.md               # This setup guide
└── .gitignore             # Git ignore rules
```

## 🔧 Configuration

### Environment Variables

- `DATABASE_URL`: PostgreSQL connection string
- `LOG_LEVEL`: Logging level (default: INFO)

### Rate Limiting

- Default: 100 requests per minute per client
- Client identification via `X-Client-ID` header or IP address
- Rate limit headers included in responses

## 🧪 Running Tests

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=app

# Run specific test file
pytest tests/test_api.py
```

## 🐛 Troubleshooting

### Common Issues

1. **Database Connection Error**
   - Ensure PostgreSQL is running
   - Check DATABASE_URL environment variable
   - Verify database exists

2. **Import Errors**
   - Install dependencies: `pip install -r requirements.txt`
   - Check Python version (3.11+ required)

3. **Port Already in Use**
   - Change port in main.py or use different port
   - Kill existing process on port 8000

4. **Docker Issues**
   - Ensure Docker is running
   - Check docker-compose.yml configuration
   - Rebuild containers: `docker-compose up --build`

### Getting Help

- Check the API documentation at `/docs`
- Review the test cases in `tests/test_api.py`
- Check logs for error messages
- Verify database connectivity

## 🚀 Production Deployment

### Docker Production
```bash
# Build production image
docker build -t employee-search-api .

# Run with production database
docker run -p 8000:8000 \
  -e DATABASE_URL="postgresql://user:password@host:5432/db" \
  employee-search-api
```

### Environment Variables for Production
```bash
DATABASE_URL=postgresql://user:password@host:5432/db
LOG_LEVEL=INFO
```

## 📊 Monitoring

- Health check: `GET /health`
- Rate limiting status: `GET /api/v1/rate-limit/info`
- Application logs for debugging

---

**Note**: This API is designed for the employee search directory use case with organization-level data isolation. It does not include CRUD operations for employees as per the assignment requirements. 
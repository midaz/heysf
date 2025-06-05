# SF Government Document Analysis - Backend

A FastAPI-based backend for scraping and analyzing SF Board of Supervisors meeting documents using LLM analysis.

## Features

- **Document Scraping**: Automatically scrapes SF BOS meeting minutes
- **LLM Analysis**: Uses OpenAI GPT-4 for document analysis
- **S3 Storage**: Stores documents in AWS S3
- **RESTful API**: Clean API for frontend integration
- **Background Scheduling**: Automated daily scraping and analysis
- **PostgreSQL Database**: Reliable data storage

## Project Structure

```
backend/
├── app/
│   ├── __init__.py
│   ├── main.py              # FastAPI app
│   ├── config.py            # Configuration
│   ├── database.py          # Database setup
│   ├── models.py            # SQLAlchemy models
│   ├── schemas.py           # Pydantic schemas
│   ├── routers/             # API endpoints
│   │   ├── documents.py     # Document endpoints
│   │   └── analysis.py      # Analysis endpoints
│   └── services/            # Business logic
│       ├── scraper.py       # SF BOS scraper
│       ├── analyzer.py      # LLM analysis
│       └── storage.py       # S3 storage
├── alembic/                 # Database migrations
├── docker-compose.yml       # PostgreSQL container
├── requirements.txt         # Python dependencies
└── scheduler.py             # Background scheduler
```

## Quick Start

### 1. Prerequisites

- Python 3.9+
- Docker and Docker Compose
- AWS S3 bucket
- OpenAI API key

### 2. Environment Setup

Create a `.env` file in the backend directory:

```env
# Database
DATABASE_URL=postgresql://postgres:password@localhost:5432/sf_docs

# OpenAI
OPENAI_API_KEY=your_openai_api_key

# AWS S3
AWS_ACCESS_KEY_ID=your_aws_access_key
AWS_SECRET_ACCESS_KEY=your_aws_secret_key
AWS_S3_BUCKET=your-sf-docs-bucket
AWS_REGION=us-west-2

# Analysis Prompt (optional - will use default if not provided)
ANALYSIS_PROMPT=Your custom analysis prompt here...
```

### 3. Database Setup

Start PostgreSQL:
```bash
docker-compose up -d postgres
```

Install Python dependencies:
```bash
pip install -r requirements.txt
```

Initialize database (optional - tables auto-create):
```bash
alembic init alembic
alembic revision --autogenerate -m "Initial migration"
alembic upgrade head
```

### 4. Run the Application

Start the API server:
```bash
python -m uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

Start the background scheduler (in a separate terminal):
```bash
python scheduler.py
```

### 5. Test the API

Visit http://localhost:8000/docs for the interactive API documentation.

Test endpoints:
- `GET /health` - Health check
- `POST /api/documents/scrape` - Trigger manual scraping
- `GET /api/documents/` - List all documents
- `POST /api/documents/{id}/analyze` - Analyze specific document

## API Endpoints

### Documents
- `GET /api/documents/` - List documents with filtering
- `GET /api/documents/{id}` - Get document with analyses
- `POST /api/documents/scrape` - Trigger document scraping
- `POST /api/documents/{id}/analyze` - Analyze specific document

### Analysis
- `GET /api/analysis/{document_id}` - Get analyses for document
- `GET /api/analysis/` - List all analyses
- `POST /api/analysis/analyze-all` - Analyze all pending documents

### System
- `GET /health` - Health check with system status

## Configuration Options

### Environment Variables

| Variable | Description | Required | Default |
|----------|-------------|----------|---------|
| `DATABASE_URL` | PostgreSQL connection string | Yes | - |
| `OPENAI_API_KEY` | OpenAI API key for LLM | Yes | - |
| `AWS_ACCESS_KEY_ID` | AWS access key | Yes | - |
| `AWS_SECRET_ACCESS_KEY` | AWS secret key | Yes | - |
| `AWS_S3_BUCKET` | S3 bucket name | Yes | - |
| `AWS_REGION` | AWS region | No | us-west-2 |
| `ANALYSIS_PROMPT` | Custom analysis prompt | No | Default prompt |
| `DEBUG` | Enable debug mode | No | False |

### Custom Analysis Prompts

You can provide your own analysis prompt via the `ANALYSIS_PROMPT` environment variable. The system will insert the document content after your prompt.

Example:
```env
ANALYSIS_PROMPT="Please analyze this SF government document and focus on: 1. Budget implications 2. Policy changes 3. Community impact"
```

## Development

### Running Tests

```bash
# Install test dependencies
pip install pytest pytest-asyncio

# Run tests
pytest
```

### Database Migrations

```bash
# Create a new migration
alembic revision --autogenerate -m "Description of changes"

# Apply migrations
alembic upgrade head

# Rollback migration
alembic downgrade -1
```

### Adding New Scrapers

To add support for new government websites:

1. Create a new scraper class in `app/services/`
2. Inherit from a base scraper interface
3. Implement required methods: `get_document_urls()`, `download_content()`
4. Register the scraper in the main application

## Deployment

### Railway Deployment

1. Create a Railway account
2. Connect your GitHub repository
3. Set environment variables in Railway dashboard
4. Deploy automatically on git push

### Environment Variables for Production

Set these in your Railway dashboard:
```
DATABASE_URL=your_railway_postgres_url
OPENAI_API_KEY=your_openai_key
AWS_ACCESS_KEY_ID=your_aws_key
AWS_SECRET_ACCESS_KEY=your_aws_secret
AWS_S3_BUCKET=your_bucket_name
```

## Monitoring and Logs

### Health Checks

The `/health` endpoint provides:
- Database connectivity status
- Document count statistics
- System timestamp

### Logging

Logs are written to stdout with timestamps and structured formatting. In production, configure log aggregation (e.g., Railway logs, CloudWatch).

### Scheduler Status

Monitor the scheduler process separately. It logs:
- Scraping job status
- Analysis completion
- Error details

## Troubleshooting

### Common Issues

1. **Database Connection Errors**
   - Ensure PostgreSQL is running: `docker-compose ps`
   - Check connection string in `.env`

2. **OpenAI API Errors**
   - Verify API key is valid
   - Check API quota limits

3. **S3 Upload Failures**
   - Verify AWS credentials
   - Check bucket permissions
   - Ensure bucket exists

4. **Scraping Issues**
   - Check SF BOS website accessibility
   - Review scraper logs for HTML structure changes

### Debug Mode

Enable debug logging:
```env
DEBUG=true
```

This provides verbose logging for troubleshooting.

## License

MIT License - See LICENSE file for details. 
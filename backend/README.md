# Proposal Generation FastAPI Backend

A lightweight FastAPI backend for generating business proposal sections using LLM technology. The service processes structured requests containing questions, user input, and best practice examples to generate professional section content.

## Features

- **Modular Architecture**: Clean separation of concerns with models, services, and API layers
- **LLM Integration**: Uses LangChain with OpenAI for content generation
- **Flexible Input**: Accepts JSON payloads with a structured proposal format
- **Error Handling**: Robust error handling with partial success support
- **Documentation**: Comprehensive API documentation via FastAPI's automatic docs

## Project Structure

```
backend/
├── app/                    # Main application package
│   ├── __init__.py
│   ├── main.py            # FastAPI app factory and configuration
│   ├── models/            # Pydantic data models
│   │   ├── __init__.py
│   │   └── proposal.py    # Proposal-related models
│   ├── routers/           # API route handlers
│   │   ├── __init__.py
│   │   └── proposal.py    # Proposal generation endpoints
│   └── services/          # Business logic services
│       ├── __init__.py
│       ├── llm_service.py      # LLM interaction service
│       └── proposal_service.py # Proposal generation logic
├── main.py                # Application entry point
├── test_setup.py         # Test script
├── example_usage.py      # Usage examples
└── pyproject.toml        # Dependencies and configuration
```

## Quick Start

### Prerequisites

- Python 3.12+
- OpenAI API key

### Installation

1. **Install dependencies using uv:**
   ```bash
   uv sync
   ```

2. **Set up environment variables:**
   ```bash
   cp .env.example .env
   # Edit .env and add your OpenAI API key
   ```

3. **Run the server:**
   ```bash
   uv run python main.py
   ```

   Or using uvicorn directly:
   ```bash
   uv run uvicorn main:app --reload --host 0.0.0.0 --port 8000
   ```

### API Usage

The server exposes the following endpoints:

- `GET /` - Health check
- `GET /health` - Detailed health status
- `POST /api/v1/generate-sections` - Generate section content

#### Example Request

```bash
curl -X POST "http://localhost:8000/api/v1/generate-sections" \
     -H "Content-Type: application/json" \
     -d '{
       "sections": {
         "kurzvorstellung": {
           "title": "Kurzvorstellung des Unternehmens",
           "questions": "Welche Produkte oder Dienstleistungen bieten Sie an?",
           "best_practice_beispiele": ["Example text..."],
           "user_input": "Wir sind ein Tech-Startup...",
           "max_section_length": 1000
         }
       }
     }'
```

#### Example Response

```json
{
  "sections": {
    "kurzvorstellung": {
      "title": "Kurzvorstellung des Unternehmens",
      "generated_content": "Generated professional content...",
      "user_input": "Wir sind ein Tech-Startup...",
      "status": "success"
    }
  },
  "status": "success"
}
```

## Architecture

The application follows a clean architecture pattern with clear separation of concerns:

### Key Components

1. **Models (`app/models/`)**: Pydantic models for request/response validation
2. **Services (`app/services/`)**: Business logic and external service integrations
   - `LLMService`: Handles LLM interactions with OpenAI
   - `ProposalGenerationService`: Orchestrates proposal section processing
3. **Routers (`app/routers/`)**: API route definitions and request handling
4. **Main App (`app/main.py`)**: FastAPI application factory and configuration

### Data Flow

1. Client sends request to `/api/v1/generate-sections`
2. Router validates request using Pydantic models
3. Router calls `ProposalGenerationService.process_request()`
4. Service processes each section using `LLMService`
5. Generated content is returned through the same chain

## Configuration

### Environment Variables

- `OPENAI_API_KEY`: Your OpenAI API key (required)
- `OPENAI_MODEL`: Model to use (default: gpt-4o-mini)
- `OPENAI_TEMPERATURE`: Temperature setting (default: 0.7)

### Dependencies

- **FastAPI**: Web framework with automatic API documentation
- **Pydantic**: Data validation and settings management
- **LangChain**: LLM framework for AI integrations
- **python-dotenv**: Environment variable management

## Development

### Running Tests

```bash
uv run python test_setup.py
```

### API Documentation

Visit http://localhost:8000/docs for interactive API documentation when the server is running.

### Example Usage

Run the example script to test the API:

```bash
uv run python example_usage.py
```

## Next Steps

The current implementation provides a solid foundation. Here are recommended enhancements for a production-ready system:

### 1. Configuration Management
- [ ] Add `app/config.py` with Pydantic Settings for environment-based configuration
- [ ] Implement proper logging configuration with structured logging
- [ ] Add configuration validation and startup checks

### 2. Error Handling & Monitoring
- [ ] Implement custom exception classes and handlers
- [ ] Add comprehensive error logging and monitoring
- [ ] Implement request/response logging middleware
- [ ] Add health checks for external dependencies (OpenAI API)

### 3. Testing
- [ ] Add comprehensive unit tests for services and models
- [ ] Implement integration tests for API endpoints
- [ ] Add test fixtures and mock LLM responses
- [ ] Set up test coverage reporting

### 4. Security & Production
- [ ] Implement API rate limiting
- [ ] Add authentication and authorization
- [ ] Configure CORS properly for production
- [ ] Add request validation and sanitization
- [ ] Implement API versioning strategy

### 5. Performance & Scalability
- [ ] Add caching layer for LLM responses
- [ ] Implement async processing for multiple sections
- [ ] Add database for storing request/response history
- [ ] Implement request queuing for high load scenarios

### 6. Deployment
- [ ] Create Dockerfile and docker-compose.yml
- [ ] Add deployment scripts and CI/CD pipeline
- [ ] Configure environment-specific settings
- [ ] Add database migrations if needed

### 7. Documentation & Maintenance
- [ ] Add comprehensive API documentation
- [ ] Create deployment and maintenance guides
- [ ] Add code quality tools (linting, formatting, type checking)
- [ ] Implement automated dependency updates

### Adding New Features

1. **New Models**: Add to `app/models/` following Pydantic patterns
2. **Business Logic**: Extend services in `app/services/` for new processing logic
3. **LLM Integration**: Modify `app/services/llm_service.py` for new AI capabilities
4. **API Endpoints**: Add routes to `app/routers/` and include in `app/main.py`

### Testing

```bash
# Install test dependencies (add to pyproject.toml)
uv add pytest httpx --dev

# Run tests
uv run pytest
```

## API Documentation

When the server is running, visit:
- **Interactive Docs**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc
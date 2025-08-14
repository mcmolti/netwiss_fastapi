# NetWiss FastAPI Backend

A comprehensive FastAPI backend for AI-powered business proposal generation with attachment processing capabilities. The service integrates multiple LLM providers (OpenAI, Anthropic) and supports file uploads and web content extraction for intelligent proposal section generation.

## Features

- **Multi-LLM Support**: Integrates OpenAI and Anthropic models with dynamic model selection
- **Attachment Processing**: PDF file uploads and web URL content extraction with AI-powered summarization
- **Template Management**: Dynamic proposal templates with configurable sections
- **Automated Maintenance**: Background file cleanup with configurable retention periods (24h default)
- **Modular Architecture**: Clean separation of concerns with models, services, and API layers
- **Async Processing**: Non-blocking file and web content processing
- **Comprehensive Logging**: Structured logging with configurable levels
- **Error Handling**: Robust error handling with partial success support and detailed error reporting
- **API Documentation**: Interactive API documentation via FastAPI's automatic docs

## Project Structure

```
backend/
├── app/                          # Main application package
│   ├── __init__.py
│   ├── main.py                   # FastAPI app factory and configuration
│   ├── config/                   # Configuration and utilities
│   │   ├── __init__.py
│   │   ├── logging.py           # Logging configuration
│   │   └── prompts.py           # LLM prompts and templates
│   ├── models/                   # Pydantic data models
│   │   ├── __init__.py
│   │   ├── proposal.py          # Proposal-related models
│   │   └── template.py          # Template models
│   ├── routers/                  # API route handlers
│   │   ├── __init__.py
│   │   ├── attachments.py       # File upload and URL processing endpoints
│   │   ├── maintenance.py       # System maintenance and cleanup endpoints
│   │   ├── proposal.py          # Proposal generation endpoints
│   │   └── template.py          # Template management endpoints
│   └── services/                 # Business logic services
│       ├── __init__.py
│       ├── file_service.py      # File upload and management
│       ├── llm_service.py       # Multi-LLM integration (OpenAI, Anthropic)
│       ├── maintenance_service.py # Automated file cleanup and maintenance
│       ├── proposal_service.py   # Legacy proposal generation logic
│       ├── proposal_service_new.py # Enhanced proposal generation with attachments
│       ├── summarization_service.py # AI-powered content summarization
│       ├── template_service.py   # Template management logic
│       └── web_scraping_service.py # Web content extraction
├── data/                         # Data storage
│   └── digi4wirtschaft.json     # Template data
├── logs/                         # Application logs
│   └── app.log                  # Main application log file
├── uploads/                      # File upload storage
├── main.py                       # Application entry point
├── pyproject.toml               # Dependencies and configuration
├── uv.lock                      # Dependency lock file
└── README.md                    # This file
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
   # Edit .env and add your API keys:
   # OPENAI_API_KEY=your_openai_key_here
   # ANTHROPIC_API_KEY=your_anthropic_key_here (optional)
   ```

3. **Run the server:**
   ```bash
   uv run fastapi dev main.py
   ```

   Or using uvicorn directly:
   ```bash
   uv run uvicorn main:app --reload --host 0.0.0.0 --port 8000
   ```

### API Usage

The server exposes the following main endpoint groups:

#### Core Endpoints
- `GET /` - Health check
- `GET /health` - Detailed health status

#### Proposal Generation
- `POST /api/v1/generate-sections` - Generate proposal sections with optional attachments
- `GET /api/v1/models` - List available AI models

#### Template Management
- `GET /api/v1/templates` - List available proposal templates
- `GET /api/v1/templates/{template_id}` - Get specific template details

#### Attachment Processing
- `POST /api/v1/attachments/upload` - Upload PDF files for processing
- `POST /api/v1/attachments/url` - Extract content from web URLs
- `DELETE /api/v1/attachments/{file_id}` - Delete uploaded files

#### Maintenance & Administration
- `POST /api/v1/maintenance/cleanup` - Manually trigger file cleanup
- `GET /api/v1/maintenance/statistics` - Get file storage statistics
- `GET /api/v1/maintenance/config` - Get current maintenance configuration
- `PUT /api/v1/maintenance/config` - Update maintenance settings

#### Example Request with Attachments

```bash
curl -X POST "http://localhost:8000/api/v1/generate-sections" \
     -H "Content-Type: application/json" \
     -d '{
       "model": "gpt-4o-mini",
       "sections": {
         "kurzvorstellung": {
           "title": "Kurzvorstellung des Unternehmens",
           "questions": "Welche Produkte oder Dienstleistungen bieten Sie an?",
           "best_practice_beispiele": ["Example text..."],
           "user_input": "Wir sind ein Tech-Startup...",
           "max_section_length": 1000,
           "attached_files": ["file_id_from_upload"],
           "attached_urls": ["https://example.com/company-info"]
         }
       }
     }'
```

#### File Upload Example

```bash
curl -X POST "http://localhost:8000/api/v1/attachments/upload" \
     -F "file=@document.pdf"
```

#### Maintenance Examples

```bash
# Trigger manual file cleanup
curl -X POST "http://localhost:8000/api/v1/maintenance/cleanup"

# Get file storage statistics
curl -X GET "http://localhost:8000/api/v1/maintenance/statistics"

# Update retention period to 48 hours
curl -X PUT "http://localhost:8000/api/v1/maintenance/config" \
     -H "Content-Type: application/json" \
     -d '{"retention_hours": 48}'
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
   - `proposal.py`: Core proposal generation models
   - `template.py`: Template management models

2. **Services (`app/services/`)**: Business logic and external service integrations
   - `LLMService`: Multi-provider LLM interactions (OpenAI, Anthropic)
   - `ProposalGenerationService`: Enhanced proposal processing with attachment support
   - `FileService`: PDF file upload and text extraction
   - `WebScrapingService`: Web content extraction and processing
   - `SummarizationService`: AI-powered content summarization
   - `TemplateService`: Dynamic template management

3. **Routers (`app/routers/`)**: API route definitions and request handling
   - `proposal.py`: Core proposal generation endpoints
   - `attachments.py`: File upload and URL processing
   - `template.py`: Template management API

4. **Configuration (`app/config/`)**: Application configuration and utilities
   - `logging.py`: Structured logging setup
   - `prompts.py`: LLM prompt templates

5. **Main App (`app/main.py`)**: FastAPI application factory with CORS and middleware

### Data Flow

1. **Template Selection**: Client retrieves available templates via `/api/v1/templates`
2. **File Upload** (optional): Client uploads PDFs via `/api/v1/attachments/upload`
3. **URL Processing** (optional): Client submits URLs via `/api/v1/attachments/url`
4. **Proposal Generation**: Client sends comprehensive request to `/api/v1/generate-sections`
   - Request includes template sections, user input, and attachment references
   - Service processes attachments using AI summarization
   - LLM generates contextual content incorporating attachment summaries
5. **Response Delivery**: Generated content returned with status information

### Attachment Processing Flow

1. **File Upload**: PDF files processed for text extraction
2. **URL Extraction**: Web content extracted and cleaned
3. **AI Summarization**: Content summarized based on section-specific questions
4. **Context Integration**: Summaries integrated into LLM prompts for enhanced generation

## Configuration

### Environment Variables

#### Required
- `OPENAI_API_KEY`: Your OpenAI API key for GPT models

#### Optional
- `ANTHROPIC_API_KEY`: Your Anthropic API key for Claude models
- `OPENAI_MODEL`: Default OpenAI model (default: gpt-4o-mini)
- `ANTHROPIC_MODEL`: Default Anthropic model (default: claude-3-5-haiku-20241022)
- `OPENAI_TEMPERATURE`: Temperature setting for OpenAI (default: 0.7)
- `ANTHROPIC_TEMPERATURE`: Temperature setting for Anthropic (default: 0.7)
- `LOG_LEVEL`: Logging level (default: INFO)

### Dependencies

#### Core Framework
- **FastAPI**: Modern web framework with automatic API documentation
- **Pydantic**: Data validation and settings management
- **uvicorn**: ASGI server for production deployment

#### AI/LLM Integration
- **LangChain**: LLM framework for AI integrations
- **langchain-openai**: OpenAI integration for LangChain
- **langchain-anthropic**: Anthropic integration for LangChain

#### File Processing
- **PyPDF2**: PDF text extraction
- **aiofiles**: Async file operations
- **python-multipart**: File upload support

#### Web Processing
- **aiohttp**: Async HTTP client for web scraping
- **beautifulsoup4**: HTML parsing and content extraction
- **requests**: Synchronous HTTP requests

#### Utilities
- **python-dotenv**: Environment variable management

## Development

### Running Tests

```bash
# Run basic functionality tests
uv run python test_setup.py

# For comprehensive testing (add to pyproject.toml)
uv add pytest httpx pytest-asyncio --dev
uv run pytest
```

### API Documentation

Visit these URLs when the server is running:
- **Interactive Docs**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

### Example Usage

Test the API with example scripts:

```bash
# Test basic proposal generation
uv run python example_usage.py

# Test attachment features (see ATTACHMENT_FEATURES.md)
```

## Key Features Deep Dive

### Multi-LLM Support

The system supports multiple AI providers with dynamic model selection:

- **OpenAI Models**: GPT-4o, GPT-4o-mini, GPT-4, GPT-3.5-turbo
- **Anthropic Models**: Claude-3.5-Sonnet, Claude-3.5-Haiku, Claude-3-Opus
- **Dynamic Selection**: Model specified per request for optimal cost/performance

### Attachment Processing

Comprehensive attachment handling with AI-powered summarization:

- **PDF Support**: Text extraction with 10MB file size limit
- **Web Content**: Automatic content extraction from URLs
- **Smart Summarization**: Context-aware summaries based on section questions
- **Error Handling**: Graceful handling of processing failures

### Template Management

Dynamic proposal templates with flexible structure:

- **JSON-based Templates**: Easy to modify and extend
- **Section Configuration**: Customizable questions and examples
- **API Access**: RESTful template management
- **Version Control**: Template versioning support

### Automated Maintenance

Comprehensive system maintenance with automated file cleanup:

- **Background Cleanup**: Automatic deletion of files older than 24 hours (configurable)
- **Scheduled Tasks**: Runs cleanup every hour to maintain storage efficiency
- **Manual Control**: API endpoints for manual cleanup and configuration
- **Statistics & Monitoring**: Real-time file storage statistics and cleanup reports
- **Configurable Retention**: Adjustable file retention periods via API
- **Graceful Handling**: Safe cleanup with proper error handling and logging

The maintenance system ensures optimal storage usage and prevents accumulation of old temporary files, maintaining system performance over time.




## Adding New Features

1. **New Models**: Add to `app/models/` following Pydantic patterns
2. **Business Logic**: Extend services in `app/services/` for new processing logic
3. **LLM Integration**: Modify `app/services/llm_service.py` for new AI capabilities
4. **API Endpoints**: Add routes to `app/routers/` and include in `app/main.py`


## API Documentation

When the server is running, visit:
- **Interactive Docs**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc
# Attachment Features Documentation

This document describes the new file attachment and URL processing features added to the proposal generation system.

## Overview

The system now supports:
- ✅ PDF file uploads with text extraction
- ✅ Website URL content extraction
- ✅ AI-powered summarization of attachments based on specific questions
- ✅ Integration of attachment summaries into proposal generation

## Backend Implementation

### New Services

1. **FileService** (`app/services/file_service.py`)
   - Handles PDF file uploads and storage
   - Extracts text content using PyPDF2
   - Validates file types and sizes (10MB limit)
   - Provides file management (upload, retrieve, delete)

2. **WebScrapingService** (`app/services/web_scraping_service.py`)
   - Extracts content from web URLs
   - Uses aiohttp for async HTTP requests
   - Parses HTML content with BeautifulSoup
   - Handles timeouts and content size limits

3. **SummarizationService** (`app/services/summarization_service.py`)
   - Creates question-aware summaries of attached content
   - Uses OpenAI models for intelligent summarization
   - Focuses summaries on specific questions provided
   - Handles different content types (PDF, web)

### Updated Models

The `Section` model now includes:
```python
attached_files: List[str] = []        # File IDs
attached_urls: List[HttpUrl] = []     # URLs
attachment_summaries: List[str] = []  # AI-generated summaries
```

### New API Endpoints

- `POST /api/files/upload` - Upload PDF files
- `GET /api/files/{file_id}` - Retrieve file content
- `DELETE /api/files/{file_id}` - Delete files
- `POST /api/urls/extract` - Extract URL content
- `POST /api/urls/extract-batch` - Process multiple URLs

### Enhanced Processing Flow

1. User uploads file or provides URL
2. Content is extracted and stored
3. When generating proposal sections:
   - SummarizationService creates question-specific summaries
   - LLMService incorporates summaries into content generation
   - Final output combines user input + attachment insights

## Frontend Implementation

### New Components

1. **FileAttachment** (`src/components/FileAttachment.tsx`)
   - File upload interface with drag-and-drop
   - URL input with validation
   - Real-time processing status
   - Content preview and management
   - Error handling and retry logic

### Updated API Client

Extended `src/lib/api.ts` with:
- `uploadFile()` - Handle file uploads
- `extractURLContent()` - Process URLs
- `deleteFile()` - Remove files
- Updated interfaces for attachment data

## Dependencies Added

### Backend
```toml
"aiofiles>=24.1.0",       # Async file operations
"aiohttp>=3.10.0",        # HTTP client for web scraping
"beautifulsoup4>=4.12.0", # HTML parsing
"PyPDF2>=3.0.0",          # PDF text extraction
"python-multipart>=0.0.6" # File upload support
```

### Frontend
No new dependencies required - uses existing React components.

## Configuration

### Environment Variables
- `OPENAI_API_KEY` - Required for summarization (existing)
- File upload directory: `uploads/` (configurable)

### Limits
- PDF files: 10MB maximum
- Web content: 1MB maximum
- Processing timeout: 30 seconds for URLs

## Usage Example

### Backend (Python)
```python
# Upload and process file
file_service = FileService()
file_data = await file_service.save_uploaded_file(uploaded_file)

# Extract URL content
web_service = WebScrapingService()
url_data = await web_service.extract_content_from_url("https://example.com")

# Generate summary
summarization_service = SummarizationService()
summary = await summarization_service.summarize_for_questions(
    content=file_data["extracted_text"],
    questions="What are the key benefits mentioned?",
    content_type="pdf"
)
```

### Frontend (React)
```tsx
import { FileAttachment } from '@/components/FileAttachment'

function ProposalForm() {
  const [attachments, setAttachments] = useState([])
  
  return (
    <FileAttachment
      onAttachmentsChange={setAttachments}
      initialAttachments={attachments}
    />
  )
}
```

## Testing

Run the test script to verify functionality:
```bash
cd backend
python test_attachments.py
```

## Error Handling

The system includes comprehensive error handling for:
- Invalid file types/sizes
- Network timeouts for URLs
- Content extraction failures
- API quota limits
- Storage issues

## Security Considerations

- File type validation (PDF only)
- Size limits to prevent abuse
- Temporary file cleanup
- URL validation to prevent SSRF
- Content sanitization

## Future Enhancements

Potential improvements:
- Support for additional file types (DOCX, TXT)
- Batch file upload
- Content caching for frequently accessed URLs
- Advanced content preprocessing
- Custom summarization models

"""
API endpoints for file and URL content management.

This module provides FastAPI endpoints for uploading files, extracting content
from URLs, and managing attachments for proposal generation.
"""

from typing import List
from fastapi import APIRouter, UploadFile, File, HTTPException, Depends
from pydantic import HttpUrl, BaseModel

from ..models.proposal import FileUploadResponse, URLContentResponse
from ..services.file_service import FileService
from ..services.web_scraping_service import WebScrapingService


class URLExtractionRequest(BaseModel):
    """Request model for URL content extraction."""

    url: HttpUrl


router = APIRouter(prefix="/api", tags=["attachments"])

# Initialize services
file_service = FileService()
web_service = WebScrapingService()


@router.post("/files/upload", response_model=FileUploadResponse)
async def upload_file(file: UploadFile = File(...)):
    """
    Upload a PDF file and extract its text content.

    Args:
        file: The PDF file to upload

    Returns:
        File metadata and extracted text content
    """
    try:
        file_data = await file_service.save_uploaded_file(file)

        return FileUploadResponse(
            file_id=file_data["file_id"],
            filename=file_data["filename"],
            size=file_data["size"],
            content_type=file_data["content_type"],
            extracted_text=file_data["extracted_text"],
        )

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error processing file: {str(e)}")


@router.get("/files/{file_id}")
async def get_file_metadata(file_id: str):
    """
    Retrieve metadata and content for an uploaded file.

    Args:
        file_id: The unique file identifier

    Returns:
        File content and metadata
    """
    content = await file_service.get_file_content(file_id)

    if content is None:
        raise HTTPException(status_code=404, detail="File not found")

    return {"file_id": file_id, "content": content}


@router.delete("/files/{file_id}")
async def delete_file(file_id: str):
    """
    Delete an uploaded file.

    Args:
        file_id: The unique file identifier

    Returns:
        Deletion status
    """
    success = await file_service.delete_file(file_id)

    if not success:
        raise HTTPException(status_code=404, detail="File not found")

    return {"message": "File deleted successfully"}


@router.post("/urls/extract", response_model=URLContentResponse)
async def extract_url_content(request: URLExtractionRequest):
    """
    Extract text content from a URL.

    Args:
        request: The URL extraction request containing the URL

    Returns:
        Extracted content and metadata
    """
    try:
        result = await web_service.extract_content_from_url(str(request.url))

        return URLContentResponse(
            url=result["url"],
            title=result.get("title"),
            content=result["content"],
            status=result["status"],
        )

    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Error extracting URL content: {str(e)}"
        )


@router.post("/urls/extract-batch")
async def extract_multiple_urls(urls: List[HttpUrl]):
    """
    Extract content from multiple URLs.

    Args:
        urls: List of URLs to extract content from

    Returns:
        List of extraction results
    """
    results = []

    for url in urls:
        try:
            result = await web_service.extract_content_from_url(str(url))
            results.append(
                URLContentResponse(
                    url=result["url"],
                    title=result.get("title"),
                    content=result["content"],
                    status=result["status"],
                )
            )
        except Exception as e:
            results.append(
                URLContentResponse(url=str(url), title=None, content="", status="error")
            )

    return results

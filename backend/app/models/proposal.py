"""
Data models for the FastAPI backend.

This module defines Pydantic models for request and response data structures
used in the proposal section generation API.
"""

from typing import Dict, List, Optional, Union
from pydantic import BaseModel, Field, HttpUrl


class AttachmentData(BaseModel):
    """
    Model for attachment data (file or URL).

    Attributes:
        type: Type of attachment ('file' or 'url')
        content: Extracted text content from the attachment
        metadata: Additional metadata about the attachment
    """

    type: str = Field(..., description="Type: 'file' or 'url'")
    content: Optional[str] = Field(None, description="Extracted text content")
    metadata: Dict[str, Union[str, int]] = Field(default_factory=dict)


class FileUploadResponse(BaseModel):
    """
    Response model for file uploads.

    Attributes:
        file_id: Unique identifier for the uploaded file
        filename: Original filename
        size: File size in bytes
        content_type: MIME type of the file
        extracted_text: Extracted text content from the file
    """

    file_id: str
    filename: str
    size: int
    content_type: str
    extracted_text: Optional[str] = None


class URLContentResponse(BaseModel):
    """
    Response model for URL content extraction.

    Attributes:
        url: The processed URL
        title: Extracted title from the webpage
        content: Extracted text content
        status: Status of the extraction
    """

    url: str
    title: Optional[str] = None
    content: str
    status: str = "success"


class Section(BaseModel):
    """
    Model representing a single section in the proposal structure.

    Attributes:
        title: The section title
        questions: Questions to guide the section content
        best_practice_beispiele: List of best practice examples
        user_input: User-provided input for this section
        max_section_length: Maximum allowed length for the section (0 means no limit)
        attached_files: List of file IDs attached to this section
        attached_urls: List of URLs attached to this section
        attachment_summaries: AI-generated summaries of attached content
    """

    title: str
    questions: str
    best_practice_beispiele: List[str] = Field(
        default_factory=list, alias="best_practice_examples"
    )
    user_input: str
    max_section_length: int
    # New fields for attachments (optional for backward compatibility)
    attached_files: Optional[List[str]] = Field(
        default_factory=list, description="File IDs"
    )
    attached_urls: Optional[List[str]] = Field(
        default_factory=list, description="URL strings"
    )
    attachment_summaries: Optional[List[str]] = Field(
        default_factory=list, description="AI-generated summaries"
    )

    class Config:
        populate_by_name = True


class ProposalRequest(BaseModel):
    """
    Request model for the proposal section generation.

    Attributes:
        sections: Dictionary of section names to Section objects
        model: Optional AI model to use for generation (defaults to gpt-4o-mini)
    """

    sections: Dict[str, Section]
    model: Optional[str] = "gpt-4o-mini"


class SectionResponse(BaseModel):
    """
    Response model for a generated section.

    Attributes:
        title: The section title
        generated_content: The LLM-generated content for this section
        user_input: The original user input
        status: Status of the generation (success, error, etc.)
    """

    title: str
    generated_content: str
    user_input: str
    status: str = "success"


class ProposalResponse(BaseModel):
    """
    Response model for the complete proposal generation.

    Attributes:
        sections: Dictionary of section names to SectionResponse objects
        status: Overall status of the generation process
    """

    sections: Dict[str, SectionResponse]
    status: str = "success"

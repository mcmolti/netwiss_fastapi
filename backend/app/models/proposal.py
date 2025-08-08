"""
Data models for the FastAPI backend.

This module defines Pydantic models for request and response data structures
used in the proposal section generation API.
"""

from typing import Dict, List, Optional
from pydantic import BaseModel, Field


class Section(BaseModel):
    """
    Model representing a single section in the proposal structure.

    Attributes:
        title: The section title
        questions: Questions to guide the section content
        best_practice_beispiele: List of best practice examples
        user_input: User-provided input for this section
        max_section_length: Maximum allowed length for the section (0 means no limit)
    """

    title: str
    questions: str
    best_practice_beispiele: List[str] = Field(
        default_factory=list, alias="best_practice_examples"
    )
    user_input: str
    max_section_length: int

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

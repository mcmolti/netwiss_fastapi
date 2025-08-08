"""
Proposal generation router.

This module defines the API endpoints for proposal section generation.
"""

from typing import List
from fastapi import APIRouter, HTTPException
from ..models import ProposalRequest, ProposalResponse
from ..services import ProposalGenerationService, LLMService

router = APIRouter(prefix="/api/v1", tags=["proposals"])

# Initialize services
proposal_service = ProposalGenerationService()


@router.get("/models")
async def get_available_models():
    """
    Get a list of available AI models for proposal generation.

    Returns:
        Dictionary with available models and their providers
    """
    return {
        "models": [
            {
                "id": "gpt-4o-mini",
                "name": "GPT-4o Mini",
                "provider": "OpenAI",
                "description": "Fast and cost-effective model",
            },
            {
                "id": "gpt-5-mini",
                "name": "GPT-5 Mini",
                "provider": "OpenAI",
                "description": "A faster and more efficient version of GPT-5",
            },
            {
                "id": "gpt-5",
                "name": "GPT-5",
                "provider": "OpenAI",
                "description": "OpenAIs latest model with advanced capabilities",
            },
            {
                "id": "claude-sonnet-4-20250514",
                "name": "Claude Sonnet 4",
                "provider": "Anthropic",
                "description": "High intelligence and balanced performance",
            },
            {
                "id": "claude-3-7-sonnet-latest",
                "name": "Claude 3.7 Sonnet",
                "provider": "Anthropic",
                "description": "High intelligence and capability",
            },
        ],
        "default": "gpt-4o-mini",
    }


@router.post("/generate-sections", response_model=ProposalResponse)
async def generate_sections(request: ProposalRequest):
    """
    Generate section content based on user input and best practice examples.

    Args:
        request: The proposal request containing sections to process

    Returns:
        Response with generated content for each section

    Raises:
        HTTPException: If processing fails
    """
    try:
        response = await proposal_service.process_request(request)
        return response
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Failed to process request: {str(e)}"
        )

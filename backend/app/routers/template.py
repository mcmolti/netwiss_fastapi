"""
Template router for proposal template endpoints.
"""

from typing import List
from fastapi import APIRouter, HTTPException
from ..models.template import ProposalTemplate, TemplateListItem
from ..services.template_service import TemplateService

router = APIRouter(prefix="/api/v1/templates", tags=["templates"])

# Initialize service
template_service = TemplateService()


@router.get("/", response_model=List[TemplateListItem])
async def get_templates():
    """
    Get a list of available proposal templates.

    Returns:
        List of available templates
    """
    try:
        return await template_service.get_available_templates()
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Failed to fetch templates: {str(e)}"
        )


@router.get("/{template_id}", response_model=ProposalTemplate)
async def get_template(template_id: str):
    """
    Get a specific proposal template.

    Args:
        template_id: The ID of the template to fetch

    Returns:
        The template data including sections, questions, and examples

    Raises:
        HTTPException: If template is not found or fails to load
    """
    try:
        return await template_service.get_template(template_id)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except FileNotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Failed to load template: {str(e)}"
        )

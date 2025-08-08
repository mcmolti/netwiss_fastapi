"""
Template models for proposal template data.
"""

from typing import Dict, List
from pydantic import BaseModel


class TemplateSection(BaseModel):
    """
    Model for a template section with questions and examples.
    """

    title: str
    questions: str
    best_practice_beispiele: List[str] = []
    best_practice_examples: List[str] = []  # Alternative field name
    user_input: str = ""
    max_section_length: int = 0


class ProposalTemplate(BaseModel):
    """
    Model for a complete proposal template.
    """

    sections: Dict[str, TemplateSection]


class TemplateListItem(BaseModel):
    """
    Model for template list items.
    """

    id: str
    name: str
    description: str = ""

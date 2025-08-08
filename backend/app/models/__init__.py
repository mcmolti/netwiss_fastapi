"""
Models package for the proposal generation API.
"""

from .proposal import Section, SectionResponse, ProposalRequest, ProposalResponse
from .template import TemplateSection, ProposalTemplate, TemplateListItem

__all__ = [
    "Section",
    "SectionResponse",
    "ProposalRequest",
    "ProposalResponse",
    "TemplateSection",
    "ProposalTemplate",
    "TemplateListItem",
]

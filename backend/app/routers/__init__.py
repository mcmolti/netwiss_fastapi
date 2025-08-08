"""
Routers package for the proposal generation API.
"""

from .proposal import router as proposal_router
from .template import router as template_router

__all__ = ["proposal_router", "template_router"]

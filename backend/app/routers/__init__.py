"""
Routers package for the proposal generation API.
"""

from .proposal import router as proposal_router
from .template import router as template_router
from .maintenance import router as maintenance_router

__all__ = ["proposal_router", "template_router", "maintenance_router"]

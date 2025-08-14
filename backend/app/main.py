"""
FastAPI application factory and configuration.
"""

import os
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv

from .routers import proposal_router, template_router
from .routers.attachments import router as attachments_router
from .config.logging import setup_logging, get_logger

# Load environment variables
load_dotenv()

# Initialize logging
setup_logging()


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Application lifespan manager.

    Handles startup and shutdown events for the FastAPI application.
    """
    logger = get_logger("main")

    # Startup
    logger.info("Starting proposal generation backend...")

    # Verify OpenAI API key is available
    if not os.getenv("OPENAI_API_KEY"):
        logger.warning("OPENAI_API_KEY not found in environment variables")

    yield

    # Shutdown
    logger.info("Shutting down proposal generation backend...")


def create_app() -> FastAPI:
    """
    Create and configure the FastAPI application.

    Returns:
        Configured FastAPI application
    """
    app = FastAPI(
        title="Proposal Generation Backend",
        description="FastAPI backend for generating business proposal sections using LLM",
        version="0.1.0",
        lifespan=lifespan,
    )

    # Add CORS middleware for frontend integration
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],  # Configure appropriately for production
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # Include routers
    app.include_router(proposal_router)
    app.include_router(template_router)
    app.include_router(attachments_router)

    # Health check endpoints
    @app.get("/")
    async def root():
        """
        Health check endpoint.

        Returns:
            Simple status message
        """
        return {"message": "Proposal Generation Backend is running"}

    @app.get("/health")
    async def health_check():
        """
        Detailed health check endpoint.

        Returns:
            Detailed health status including API key availability
        """
        return {
            "status": "healthy",
            "openai_api_key_configured": bool(os.getenv("OPENAI_API_KEY")),
        }

    return app


# Create the app instance
app = create_app()

"""
CORS configuration for the FastAPI application.
Provides environment-specific CORS settings with security best practices.
"""

import os
from typing import List, Dict, Any, TYPE_CHECKING
import logging

if TYPE_CHECKING:
    from fastapi import FastAPI

# Use standard logging instead of potentially circular import
logger = logging.getLogger("cors")


class CORSConfig:
    """CORS configuration manager with environment-specific settings."""

    def __init__(self):
        self.environment = os.getenv("ENVIRONMENT", "development").lower()
        self._validate_environment()

    def _validate_environment(self):
        """Validate that the environment is properly set."""
        valid_environments = ["development", "staging", "production"]
        if self.environment not in valid_environments:
            logger.warning(
                f"Invalid environment '{self.environment}'. Defaulting to 'development'. "
                f"Valid environments: {valid_environments}"
            )
            self.environment = "development"

    def get_cors_origins(self) -> List[str]:
        """
        Get allowed CORS origins based on environment.

        Returns:
            List of allowed origin URLs
        """
        if self.environment == "production":
            return self._get_production_origins()
        elif self.environment == "staging":
            return self._get_staging_origins()
        else:
            return self._get_development_origins()

    def _get_development_origins(self) -> List[str]:
        """Get CORS origins for development environment."""
        default_origins = [
            "http://localhost:3000",
            "http://localhost:3001",
            "http://127.0.0.1:3000",
            "http://127.0.0.1:3001",
        ]

        # Allow custom origins from environment variable
        custom_origins = os.getenv("CORS_ORIGINS", "")
        if custom_origins:
            origins = [origin.strip() for origin in custom_origins.split(",")]
            # Validate origins
            validated_origins = []
            for origin in origins:
                if self._is_valid_origin(origin):
                    validated_origins.append(origin)
                else:
                    logger.warning(f"Invalid CORS origin ignored: {origin}")
            return validated_origins if validated_origins else default_origins

        return default_origins

    def _get_staging_origins(self) -> List[str]:
        """Get CORS origins for staging environment."""
        staging_origins = os.getenv("CORS_ORIGINS", "")
        if not staging_origins:
            logger.error("CORS_ORIGINS not set for staging environment")
            return []

        origins = [origin.strip() for origin in staging_origins.split(",")]
        validated_origins = []
        for origin in origins:
            if self._is_valid_origin(origin) and origin.startswith("https://"):
                validated_origins.append(origin)
            else:
                logger.warning(
                    f"Invalid or insecure CORS origin ignored in staging: {origin}"
                )

        return validated_origins

    def _get_production_origins(self) -> List[str]:
        """Get CORS origins for production environment."""
        production_origins = os.getenv("CORS_ORIGINS", "")
        if not production_origins:
            logger.error("CORS_ORIGINS not set for production environment")
            return []

        origins = [origin.strip() for origin in production_origins.split(",")]
        validated_origins = []
        for origin in origins:
            if self._is_valid_origin(origin) and origin.startswith("https://"):
                validated_origins.append(origin)
            else:
                logger.error(
                    f"Invalid or insecure CORS origin rejected in production: {origin}"
                )

        if not validated_origins:
            logger.error("No valid CORS origins configured for production")

        return validated_origins

    def _is_valid_origin(self, origin: str) -> bool:
        """
        Validate a CORS origin URL.

        Args:
            origin: The origin URL to validate

        Returns:
            True if the origin is valid, False otherwise
        """
        if not origin:
            return False

        # Basic URL validation
        if not (origin.startswith("http://") or origin.startswith("https://")):
            return False

        # Don't allow wildcard origins in production
        if self.environment == "production" and "*" in origin:
            return False

        return True

    def get_cors_settings(self) -> Dict[str, Any]:
        """
        Get complete CORS middleware settings.

        Returns:
            Dictionary with CORS middleware configuration
        """
        allow_credentials = (
            os.getenv("CORS_ALLOW_CREDENTIALS", "true").lower() == "true"
        )
        max_age = int(os.getenv("CORS_MAX_AGE", "86400"))

        # Security: Don't allow credentials with wildcard origins
        origins = self.get_cors_origins()
        if allow_credentials and "*" in origins:
            logger.warning("Disabling credentials due to wildcard origin")
            allow_credentials = False

        settings = {
            "allow_origins": origins,
            "allow_credentials": allow_credentials,
            "allow_methods": self._get_allowed_methods(),
            "allow_headers": self._get_allowed_headers(),
            "max_age": max_age,
        }

        logger.info(f"CORS configured for {self.environment} environment")
        logger.info(f"Allowed origins: {origins}")
        logger.info(f"Allow credentials: {allow_credentials}")

        return settings

    def _get_allowed_methods(self) -> List[str]:
        """Get allowed HTTP methods for CORS."""
        if self.environment == "production":
            return ["GET", "POST", "PUT", "DELETE", "OPTIONS"]
        else:
            return ["*"]  # Allow all methods in development/staging

    def _get_allowed_headers(self) -> List[str]:
        """Get allowed headers for CORS."""
        # Essential headers for the application
        headers = [
            "Accept",
            "Accept-Language",
            "Content-Language",
            "Content-Type",
            "Authorization",
            "X-Requested-With",
            "X-CSRF-Token",
        ]

        if self.environment != "production":
            # Allow additional headers in development
            headers.extend(
                [
                    "X-Debug-Mode",
                    "X-Request-ID",
                ]
            )

        return headers


def get_cors_middleware_config() -> Dict[str, Any]:
    """
    Get CORS middleware configuration for the FastAPI application.

    Returns:
        Dictionary with CORS middleware settings
    """
    cors_config = CORSConfig()
    return cors_config.get_cors_settings()


def add_cors_middleware(app: "FastAPI", **kwargs: Any) -> None:
    """
    Add CORS middleware to the FastAPI application.

    Args:
        app: FastAPI application instance
        **kwargs: Additional CORS middleware options (overrides defaults)
    """
    from fastapi.middleware.cors import CORSMiddleware
    
    config = get_cors_middleware_config()
    config.update(kwargs)  # Allow overrides

    app.add_middleware(CORSMiddleware, **config)

    logger.info("CORS middleware added to application")

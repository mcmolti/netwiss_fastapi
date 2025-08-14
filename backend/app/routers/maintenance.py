"""
Maintenance API router for administrative tasks.

This module provides REST endpoints for maintenance operations
including file cleanup and system statistics.
"""

from fastapi import APIRouter, HTTPException
from typing import Dict, Any
from ..services.maintenance_service import MaintenanceService
from ..config.logging import get_logger

router = APIRouter(prefix="/api/v1/maintenance", tags=["maintenance"])
logger = get_logger("routers.maintenance")

# Initialize maintenance service
maintenance_service = MaintenanceService()


@router.post("/cleanup", response_model=Dict[str, Any])
async def trigger_cleanup():
    """
    Manually trigger file cleanup process.

    Removes all files older than the configured retention period (24 hours by default).

    Returns:
        Cleanup statistics including number of files deleted and space freed
    """
    try:
        logger.info("Manual cleanup triggered via API")
        cleanup_stats = await maintenance_service.cleanup_old_files()
        return {
            "status": "success",
            "message": "Cleanup completed successfully",
            "statistics": cleanup_stats,
        }
    except Exception as e:
        logger.error(f"Error during manual cleanup: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Cleanup failed: {str(e)}")


@router.get("/statistics", response_model=Dict[str, Any])
async def get_file_statistics():
    """
    Get current file storage statistics.

    Provides information about uploaded files including count, total size,
    and age distribution.

    Returns:
        Dictionary containing file statistics
    """
    try:
        stats = await maintenance_service.get_file_statistics()
        return {"status": "success", "statistics": stats}
    except Exception as e:
        logger.error(f"Error getting file statistics: {str(e)}")
        raise HTTPException(
            status_code=500, detail=f"Failed to get statistics: {str(e)}"
        )


@router.get("/config", response_model=Dict[str, Any])
async def get_maintenance_config():
    """
    Get current maintenance configuration.

    Returns:
        Current maintenance settings including retention period and cleanup interval
    """
    return {
        "status": "success",
        "configuration": {
            "file_retention_hours": maintenance_service.file_retention_hours,
            "cleanup_interval_hours": maintenance_service.cleanup_interval_hours,
            "upload_directory": maintenance_service.upload_directory,
        },
    }


@router.put("/config", response_model=Dict[str, Any])
async def update_maintenance_config(
    retention_hours: int = None, cleanup_interval_hours: int = None
):
    """
    Update maintenance configuration.

    Args:
        retention_hours: How long to keep files (in hours)
        cleanup_interval_hours: How often to run cleanup (in hours)

    Returns:
        Updated configuration
    """
    try:
        if retention_hours is not None:
            if retention_hours < 1:
                raise HTTPException(
                    status_code=400, detail="Retention hours must be at least 1"
                )

        if cleanup_interval_hours is not None:
            if cleanup_interval_hours < 0.1:  # Minimum 6 minutes
                raise HTTPException(
                    status_code=400,
                    detail="Cleanup interval must be at least 0.1 hours (6 minutes)",
                )

        # Update configuration
        maintenance_service.configure_retention(
            retention_hours or maintenance_service.file_retention_hours,
            cleanup_interval_hours,
        )

        logger.info(
            f"Maintenance configuration updated: retention={maintenance_service.file_retention_hours}h, "
            f"interval={maintenance_service.cleanup_interval_hours}h"
        )

        return {
            "status": "success",
            "message": "Configuration updated successfully",
            "configuration": {
                "file_retention_hours": maintenance_service.file_retention_hours,
                "cleanup_interval_hours": maintenance_service.cleanup_interval_hours,
                "upload_directory": maintenance_service.upload_directory,
            },
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error updating maintenance configuration: {str(e)}")
        raise HTTPException(
            status_code=500, detail=f"Failed to update configuration: {str(e)}"
        )

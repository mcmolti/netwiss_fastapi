"""
Maintenance service for automated cleanup tasks.

This module provides functionality for cleaning up old files, logs,
and other maintenance tasks to keep the application running efficiently.
"""

import os
import asyncio
import time
from datetime import datetime, timedelta
from typing import List, Dict, Any
from pathlib import Path
from ..config.logging import get_logger


class MaintenanceService:
    """
    Service class for handling automated maintenance tasks.

    This class manages cleanup operations including file deletion,
    log rotation, and other periodic maintenance tasks.
    """

    def __init__(self, upload_directory: str = "uploads"):
        """
        Initialize the maintenance service.

        Args:
            upload_directory: Directory containing uploaded files to maintain
        """
        self.upload_directory = upload_directory
        self.logger = get_logger("services.maintenance")

        # Maintenance configuration
        self.file_retention_hours = 24  # Delete files older than 24 hours
        self.cleanup_interval_hours = 1  # Run cleanup every hour

        self.logger.info("Maintenance service initialized")

    async def cleanup_old_files(self) -> Dict[str, Any]:
        """
        Clean up files older than the retention period.

        Returns:
            Dictionary containing cleanup statistics
        """
        self.logger.info("Starting file cleanup process")

        if not os.path.exists(self.upload_directory):
            self.logger.warning(
                f"Upload directory {self.upload_directory} does not exist"
            )
            return {"deleted_files": 0, "errors": 0, "total_size_freed": 0}

        deleted_files = 0
        errors = 0
        total_size_freed = 0
        cutoff_time = time.time() - (self.file_retention_hours * 3600)  # 24 hours ago

        try:
            for filename in os.listdir(self.upload_directory):
                file_path = os.path.join(self.upload_directory, filename)

                # Skip directories
                if os.path.isdir(file_path):
                    continue

                try:
                    # Get file stats
                    file_stats = os.stat(file_path)
                    file_age = file_stats.st_mtime
                    file_size = file_stats.st_size

                    # Check if file is older than retention period
                    if file_age < cutoff_time:
                        self.logger.debug(f"Deleting old file: {filename}")
                        os.remove(file_path)
                        deleted_files += 1
                        total_size_freed += file_size

                        # Log file deletion details
                        age_hours = (time.time() - file_age) / 3600
                        self.logger.info(
                            f"Deleted file: {filename} (age: {age_hours:.1f}h, size: {file_size} bytes)"
                        )

                except OSError as e:
                    self.logger.error(f"Error processing file {filename}: {str(e)}")
                    errors += 1

        except Exception as e:
            self.logger.error(f"Error during file cleanup: {str(e)}")
            errors += 1

        cleanup_stats = {
            "deleted_files": deleted_files,
            "errors": errors,
            "total_size_freed": total_size_freed,
            "retention_hours": self.file_retention_hours,
            "cleanup_time": datetime.now().isoformat(),
        }

        self.logger.info(
            f"File cleanup completed: {deleted_files} files deleted, "
            f"{total_size_freed / 1024:.1f} KB freed, {errors} errors"
        )

        return cleanup_stats

    async def get_file_statistics(self) -> Dict[str, Any]:
        """
        Get statistics about files in the upload directory.

        Returns:
            Dictionary containing file statistics
        """
        if not os.path.exists(self.upload_directory):
            return {
                "total_files": 0,
                "total_size": 0,
                "oldest_file_age_hours": 0,
                "newest_file_age_hours": 0,
            }

        total_files = 0
        total_size = 0
        oldest_time = None
        newest_time = None
        current_time = time.time()

        try:
            for filename in os.listdir(self.upload_directory):
                file_path = os.path.join(self.upload_directory, filename)

                if os.path.isfile(file_path):
                    file_stats = os.stat(file_path)
                    total_files += 1
                    total_size += file_stats.st_size

                    if oldest_time is None or file_stats.st_mtime < oldest_time:
                        oldest_time = file_stats.st_mtime

                    if newest_time is None or file_stats.st_mtime > newest_time:
                        newest_time = file_stats.st_mtime

        except Exception as e:
            self.logger.error(f"Error getting file statistics: {str(e)}")

        # Calculate ages in hours
        oldest_age_hours = (current_time - oldest_time) / 3600 if oldest_time else 0
        newest_age_hours = (current_time - newest_time) / 3600 if newest_time else 0

        return {
            "total_files": total_files,
            "total_size": total_size,
            "total_size_mb": total_size / (1024 * 1024),
            "oldest_file_age_hours": oldest_age_hours,
            "newest_file_age_hours": newest_age_hours,
            "directory": self.upload_directory,
        }

    async def start_periodic_cleanup(self):
        """
        Start the periodic cleanup task that runs in the background.

        This method should be called during application startup to begin
        automated maintenance.
        """
        self.logger.info(
            f"Starting periodic cleanup task (interval: {self.cleanup_interval_hours}h, "
            f"retention: {self.file_retention_hours}h)"
        )

        while True:
            try:
                await asyncio.sleep(
                    self.cleanup_interval_hours * 3600
                )  # Convert hours to seconds
                await self.cleanup_old_files()

            except asyncio.CancelledError:
                self.logger.info("Periodic cleanup task cancelled")
                break
            except Exception as e:
                self.logger.error(f"Error in periodic cleanup task: {str(e)}")
                # Continue running even if there's an error

    def configure_retention(
        self, retention_hours: int, cleanup_interval_hours: int = None
    ):
        """
        Configure file retention and cleanup intervals.

        Args:
            retention_hours: How long to keep files (in hours)
            cleanup_interval_hours: How often to run cleanup (in hours)
        """
        self.file_retention_hours = retention_hours
        if cleanup_interval_hours is not None:
            self.cleanup_interval_hours = cleanup_interval_hours

        self.logger.info(
            f"Updated maintenance configuration: retention={retention_hours}h, "
            f"interval={self.cleanup_interval_hours}h"
        )

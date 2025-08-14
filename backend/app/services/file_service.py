"""
File management service for handling PDF uploads and text extraction.

This module provides functionality for uploading, storing, and extracting
text content from PDF files.
"""

import os
import uuid
import aiofiles
from typing import Optional, Dict, Any
from fastapi import UploadFile, HTTPException
import PyPDF2
from io import BytesIO
import logging

logger = logging.getLogger(__name__)


class FileService:
    """
    Service class for handling file uploads and text extraction.

    This class manages file storage, validation, and text extraction
    from PDF documents.
    """

    ALLOWED_EXTENSIONS = {".pdf"}
    MAX_FILE_SIZE = 10 * 1024 * 1024  # 10MB

    def __init__(self, upload_directory: str = "uploads"):
        """
        Initialize the file service.

        Args:
            upload_directory: Directory to store uploaded files
        """
        self.upload_directory = upload_directory
        os.makedirs(upload_directory, exist_ok=True)

    async def save_uploaded_file(self, file: UploadFile) -> Dict[str, Any]:
        """
        Save uploaded file and extract text content.

        Args:
            file: The uploaded file from FastAPI

        Returns:
            Dictionary containing file metadata and extracted text

        Raises:
            HTTPException: If file validation fails or processing errors occur
        """
        # Validate file
        self._validate_file(file)

        # Generate unique file ID and path
        file_id = str(uuid.uuid4())
        file_extension = os.path.splitext(file.filename)[1].lower()
        file_path = os.path.join(self.upload_directory, f"{file_id}{file_extension}")

        try:
            # Save file to disk
            async with aiofiles.open(file_path, "wb") as f:
                content = await file.read()
                await f.write(content)

            # Extract text content
            extracted_text = await self._extract_text_from_pdf(file_path)

            # Prepare response data
            file_data = {
                "file_id": file_id,
                "filename": file.filename,
                "size": len(content),
                "content_type": file.content_type,
                "extracted_text": extracted_text,
                "file_path": file_path,
            }

            logger.info(f"Successfully processed file: {file.filename} (ID: {file_id})")
            return file_data

        except Exception as e:
            # Cleanup file if processing failed
            if os.path.exists(file_path):
                os.remove(file_path)
            logger.error(f"Error processing file {file.filename}: {str(e)}")
            raise HTTPException(
                status_code=500, detail=f"Failed to process file: {str(e)}"
            )

    async def get_file_content(self, file_id: str) -> Optional[str]:
        """
        Retrieve extracted text content for a file.

        Args:
            file_id: The unique file identifier

        Returns:
            Extracted text content or None if file not found
        """
        file_path = self._get_file_path(file_id)
        if file_path and os.path.exists(file_path):
            return await self._extract_text_from_pdf(file_path)
        return None

    async def delete_file(self, file_id: str) -> bool:
        """
        Delete a file from storage.

        Args:
            file_id: The unique file identifier

        Returns:
            True if file was deleted, False if file not found
        """
        file_path = self._get_file_path(file_id)
        if file_path and os.path.exists(file_path):
            try:
                os.remove(file_path)
                logger.info(f"Deleted file: {file_id}")
                return True
            except Exception as e:
                logger.error(f"Error deleting file {file_id}: {str(e)}")
                return False
        return False

    def _validate_file(self, file: UploadFile) -> None:
        """
        Validate uploaded file.

        Args:
            file: The uploaded file to validate

        Raises:
            HTTPException: If validation fails
        """
        if not file.filename:
            raise HTTPException(status_code=400, detail="No filename provided")

        # Check file extension
        file_extension = os.path.splitext(file.filename)[1].lower()
        if file_extension not in self.ALLOWED_EXTENSIONS:
            raise HTTPException(
                status_code=400,
                detail=f"File type not allowed. Supported types: {', '.join(self.ALLOWED_EXTENSIONS)}",
            )

        # Check file size (this is an approximation, actual size check happens during read)
        if hasattr(file, "size") and file.size > self.MAX_FILE_SIZE:
            raise HTTPException(
                status_code=413,
                detail=f"File too large. Maximum size: {self.MAX_FILE_SIZE / (1024*1024):.1f}MB",
            )

    async def _extract_text_from_pdf(self, file_path: str) -> str:
        """
        Extract text content from a PDF file.

        Args:
            file_path: Path to the PDF file

        Returns:
            Extracted text content
        """
        try:
            with open(file_path, "rb") as file:
                pdf_reader = PyPDF2.PdfReader(file)
                text_content = []

                for page_num in range(len(pdf_reader.pages)):
                    page = pdf_reader.pages[page_num]
                    text_content.append(page.extract_text())

                return "\n".join(text_content)

        except Exception as e:
            logger.error(f"Error extracting text from PDF {file_path}: {str(e)}")
            return ""

    def _get_file_path(self, file_id: str) -> Optional[str]:
        """
        Get the file path for a given file ID.

        Args:
            file_id: The unique file identifier

        Returns:
            File path if found, None otherwise
        """
        for extension in self.ALLOWED_EXTENSIONS:
            file_path = os.path.join(self.upload_directory, f"{file_id}{extension}")
            if os.path.exists(file_path):
                return file_path
        return None

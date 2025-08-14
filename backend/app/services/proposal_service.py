"""
Business logic service for processing proposal requests.

This module contains the core business logic for processing section generation
requests, coordinating between the data models and LLM service.
"""

from typing import Dict, List
from ..models import (
    Section,
    SectionResponse,
    ProposalRequest,
    ProposalResponse,
)
from .llm_service import LLMService
from .file_service import FileService
from .web_scraping_service import WebScrapingService
from .summarization_service import SummarizationService


class ProposalGenerationService:
    """
    Service class for processing proposal section generation requests.

    This class orchestrates the section generation process, handling multiple
    sections and coordinating with the LLM service.
    """

    def __init__(self, llm_service: LLMService = None):
        """
        Initialize the service.

        Args:
            llm_service: Optional LLM service instance (deprecated, models are now created per request)
        """
        # We no longer store a single LLM service instance
        # since we create them dynamically based on the request model

        # Initialize attachment processing services
        self.file_service = FileService()
        self.web_service = WebScrapingService()
        self.summarization_service = SummarizationService()

    async def process_request(self, request: ProposalRequest) -> ProposalResponse:
        """
        Process a complete proposal request.

        Args:
            request: The incoming request with all sections and model specification

        Returns:
            Response with generated content for all sections
        """
        processed_sections: Dict[str, SectionResponse] = {}
        overall_status = "success"

        # Create LLM service with the specified model
        llm_service = LLMService(model_name=request.model)

        for section_name, section in request.sections.items():
            try:
                section_response = await self._process_section(
                    section_name, section, llm_service
                )
                processed_sections[section_name] = section_response
            except Exception as e:
                # Log error in production
                print(f"Error processing section {section_name}: {str(e)}")
                processed_sections[section_name] = SectionResponse(
                    title=section.title,
                    generated_content=f"Fehler bei der Generierung: {str(e)}",
                    user_input=section.user_input,
                    status="error",
                )
                overall_status = "partial_success"

        return ProposalResponse(sections=processed_sections, status=overall_status)

    async def _process_section(
        self, section_name: str, section: Section, llm_service: LLMService
    ) -> SectionResponse:
        """
        Process a single section.

        Args:
            section_name: The name/key of the section
            section: The section data
            llm_service: The LLM service instance with the specified model

        Returns:
            Generated section response
        """
        # Skip generation if no user input provided
        if not section.user_input.strip():
            return SectionResponse(
                title=section.title,
                generated_content="",
                user_input=section.user_input,
                status="skipped",
            )

        # Process attachments if any
        attachment_summaries = []
        if section.attached_files or section.attached_urls:
            attachment_summaries = await self._process_attachments(section)

        # Generate content using LLM service
        if attachment_summaries:
            generated_content = llm_service.generate_section_content_with_attachments(
                title=section.title,
                questions=section.questions,
                user_input=section.user_input,
                best_practice_examples=section.best_practice_beispiele,
                attachment_summaries=attachment_summaries,
                max_length=section.max_section_length,
            )
        else:
            generated_content = llm_service.generate_section_content(
                title=section.title,
                questions=section.questions,
                user_input=section.user_input,
                best_practice_examples=section.best_practice_beispiele,
                max_length=section.max_section_length,
            )

        return SectionResponse(
            title=section.title,
            generated_content=generated_content,
            user_input=section.user_input,
            status="success",
        )

    async def _process_attachments(self, section: Section) -> List[str]:
        """
        Process attachments for a section and generate summaries.

        Args:
            section: The section with attachments

        Returns:
            List of generated summaries
        """
        summaries = []

        # Process file attachments
        for file_id in section.attached_files:
            try:
                file_content = await self.file_service.get_file_content(file_id)
                if file_content:
                    summary = await self.summarization_service.summarize_for_questions(
                        content=file_content,
                        questions=section.questions,
                        content_type="pdf",
                    )
                    summaries.append(summary)
            except Exception as e:
                print(f"Error processing file {file_id}: {str(e)}")
                summaries.append(f"Fehler beim Verarbeiten der Datei: {str(e)}")

        # Process URL attachments
        for url in section.attached_urls:
            try:
                url_result = await self.web_service.extract_content_from_url(str(url))
                if url_result["status"] == "success" and url_result["content"]:
                    summary = await self.summarization_service.summarize_for_questions(
                        content=url_result["content"],
                        questions=section.questions,
                        content_type="web",
                    )
                    summaries.append(summary)
            except Exception as e:
                print(f"Error processing URL {url}: {str(e)}")
                summaries.append(f"Fehler beim Verarbeiten der URL: {str(e)}")

        return summaries

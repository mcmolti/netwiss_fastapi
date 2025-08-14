"""
Summarization agent service for creating question-aware content summaries.

This module provides AI-powered summarization of attached files and web content,
specifically tailored to the questions they are attached to.
"""

import os
from typing import List, Optional
from langchain.schema import BaseMessage, HumanMessage, SystemMessage
from langchain_openai import ChatOpenAI
import logging

logger = logging.getLogger(__name__)


class SummarizationService:
    """
    Service class for generating question-aware summaries of attached content.

    This class uses AI models to create focused summaries of PDF and web content
    based on the specific questions they are meant to address.
    """

    DEFAULT_MODEL = "gpt-4o-mini"
    DEFAULT_TEMPERATURE = 0.3  # Lower temperature for more focused summaries

    def __init__(
        self, model_name: str = DEFAULT_MODEL, temperature: float = DEFAULT_TEMPERATURE
    ):
        """
        Initialize the summarization service.

        Args:
            model_name: The AI model to use for summarization
            temperature: Temperature setting for response generation
        """
        self.model_name = model_name
        self.temperature = temperature
        self._llm = None

    @property
    def llm(self):
        """
        Lazy initialization of the LLM instance.

        Returns:
            Configured LLM instance
        """
        if self._llm is None:
            api_key = os.getenv("OPENAI_API_KEY")
            if not api_key:
                raise ValueError("OPENAI_API_KEY environment variable is required")

            self._llm = ChatOpenAI(
                model=self.model_name, temperature=self.temperature, api_key=api_key
            )

        return self._llm

    async def summarize_for_questions(
        self,
        content: str,
        questions: str,
        content_type: str = "text",
        max_summary_length: int = 1000,
    ) -> str:
        """
        Generate a question-aware summary of content.

        Args:
            content: The content to summarize (PDF text or web content)
            questions: The specific questions this content should address
            content_type: Type of content ('pdf' or 'web')
            max_summary_length: Maximum length of the summary

        Returns:
            Generated summary focused on the questions
        """
        try:
            if not content.strip():
                return "Kein verwertbarer Inhalt in der Anlage gefunden."

            # Truncate content if too long (to avoid token limits)
            max_content_length = 8000  # Approximate token limit consideration
            if len(content) > max_content_length:
                content = content[:max_content_length] + "..."
                logger.info(f"Content truncated to {max_content_length} characters")

            messages = self._build_summarization_messages(
                content, questions, content_type, max_summary_length
            )

            response = self.llm.invoke(messages)
            summary = response.content.strip()

            logger.info(
                f"Generated summary of {len(summary)} characters for {content_type} content"
            )
            return summary

        except Exception as e:
            logger.error(f"Error generating summary: {str(e)}")
            return f"Fehler bei der Zusammenfassung: {str(e)}"

    def _build_summarization_messages(
        self, content: str, questions: str, content_type: str, max_length: int
    ) -> List[BaseMessage]:
        """
        Build the message chain for summarization.

        Args:
            content: Content to summarize
            questions: Questions to focus on
            content_type: Type of content
            max_length: Maximum summary length

        Returns:
            List of messages for the LLM
        """
        system_prompt = self._create_summarization_system_prompt(
            content_type, max_length
        )
        human_prompt = self._create_summarization_human_prompt(content, questions)

        return [
            SystemMessage(content=system_prompt),
            HumanMessage(content=human_prompt),
        ]

    def _create_summarization_system_prompt(
        self, content_type: str, max_length: int
    ) -> str:
        """
        Create the system prompt for summarization.

        Args:
            content_type: Type of content being summarized
            max_length: Maximum length constraint

        Returns:
            System prompt string
        """
        content_type_text = {
            "pdf": "PDF-Dokument",
            "web": "Webseite",
            "text": "Text",
        }.get(content_type, "Dokument")

        prompt = f"""Du bist ein Experte für die Analyse und Zusammenfassung von Inhalten für Projektanträge.

Deine Aufgabe ist es, aus dem bereitgestellten {content_type_text} die relevanten Informationen zu extrahieren, die zur Beantwortung der gegebenen Leitfragen benötigt werden.

Richtlinien für die Zusammenfassung:
- Fokussiere dich ausschließlich auf Informationen, die relevant für die Leitfragen sind
- Strukturiere die Zusammenfassung logisch und kohärent
- Verwende eine professionelle, sachliche Sprache
- Extrahiere konkrete Daten, Zahlen und Fakten, wo verfügbar
- Ignoriere irrelevante Details oder Marketing-Sprache
- Falls das Dokument nicht relevant für die Fragen ist, sage das deutlich

Ziel: Eine präzise, fokussierte Zusammenfassung, die als Grundlage für die Antragserstellung dient."""

        if max_length > 0:
            prompt += f"\n- Halte die Zusammenfassung unter {max_length} Zeichen"

        return prompt

    def _create_summarization_human_prompt(self, content: str, questions: str) -> str:
        """
        Create the human prompt for summarization.

        Args:
            content: Content to summarize
            questions: Questions to focus on

        Returns:
            Human prompt string
        """
        return f"""Leitfragen, die beantwortet werden sollen:
{questions}

Zu analysierender Inhalt:
{content}

Bitte erstelle eine fokussierte Zusammenfassung des Inhalts, die speziell auf die Beantwortung der oben genannten Leitfragen ausgerichtet ist. Extrahiere nur die relevanten Informationen und strukturiere sie so, dass sie für die Erstellung eines Projektantrags hilfreich sind."""

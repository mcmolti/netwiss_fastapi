"""
LLM service for generating section content.

This module provides an abstraction layer for LLM interactions,
supporting both OpenAI and Anthropic (Claude) models through LangChain.
"""

import os
from typing import List, Optional
from langchain.schema import BaseMessage, HumanMessage, SystemMessage
from langchain_openai import ChatOpenAI


class LLMService:
    """
    Service class for handling LLM interactions for section generation.

    This class encapsulates the LLM logic and provides a clean interface
    for generating section content using different AI providers (OpenAI, Anthropic).
    """

    # Supported models mapping
    SUPPORTED_MODELS = {
        "gpt-4o-mini": "openai",
        "gpt-5-mini": "openai",
        "gpt-5": "openai",
        "claude-sonnet-4-20250514": "anthropic",
        "claude-3-7-sonnet-latest": "anthropic",
    }

    def __init__(self, model_name: str = "gpt-4o-mini", temperature: float = 1):
        """
        Initialize the LLM service.

        Args:
            model_name: The AI model to use
            temperature: Temperature setting for response generation
        """
        if model_name not in self.SUPPORTED_MODELS:
            raise ValueError(
                f"Unsupported model: {model_name}. Supported models: {list(self.SUPPORTED_MODELS.keys())}"
            )

        self.model_name = model_name
        # Important: Temperature is set to 1 as the default value, as it is now unsupported by the OpenAI GPT5 Models
        self.temperature = temperature
        self.provider = self.SUPPORTED_MODELS[model_name]
        self._llm = None

    @property
    def llm(self):
        """
        Lazy initialization of the LLM instance based on provider.

        Returns:
            Configured LLM instance (ChatOpenAI or ChatAnthropic)
        """
        if self._llm is None:
            if self.provider == "openai":
                api_key = os.getenv("OPENAI_API_KEY")
                if not api_key:
                    raise ValueError(
                        "OPENAI_API_KEY environment variable is required for OpenAI models"
                    )

                self._llm = ChatOpenAI(
                    model=self.model_name, temperature=self.temperature, api_key=api_key
                )
            elif self.provider == "anthropic":
                try:
                    from langchain_anthropic import ChatAnthropic
                except ImportError:
                    raise ValueError(
                        "langchain_anthropic is required for Anthropic models. Install with: pip install langchain-anthropic"
                    )

                api_key = os.getenv("ANTHROPIC_API_KEY")
                if not api_key:
                    raise ValueError(
                        "ANTHROPIC_API_KEY environment variable is required for Anthropic models"
                    )

                self._llm = ChatAnthropic(
                    model=self.model_name, temperature=self.temperature, api_key=api_key
                )
            else:
                raise ValueError(f"Unsupported provider: {self.provider}")

        return self._llm

    def generate_section_content(
        self,
        title: str,
        questions: str,
        user_input: str,
        best_practice_examples: List[str],
        max_length: int = 0,
    ) -> str:
        """
        Generate content for a section based on provided inputs.

        Args:
            title: The section title
            questions: Questions to guide the content
            user_input: User-provided input
            best_practice_examples: List of example texts
            max_length: Maximum length constraint (0 for no limit)

        Returns:
            Generated section content
        """
        messages = self._build_messages(
            title, questions, user_input, best_practice_examples, max_length
        )

        try:
            response = self.llm.invoke(messages)
            return response.content.strip()
        except Exception as e:
            raise RuntimeError(f"Failed to generate content: {str(e)}")

    def generate_section_content_with_attachments(
        self,
        title: str,
        questions: str,
        user_input: str,
        best_practice_examples: List[str],
        attachment_summaries: List[str],
        max_length: int = 0,
    ) -> str:
        """
        Generate content for a section including attachment summaries.

        Args:
            title: The section title
            questions: Questions to guide the content
            user_input: User-provided input
            best_practice_examples: List of example texts
            attachment_summaries: List of AI-generated summaries from attachments
            max_length: Maximum length constraint (0 for no limit)

        Returns:
            Generated section content incorporating attachment data
        """
        messages = self._build_messages_with_attachments(
            title,
            questions,
            user_input,
            best_practice_examples,
            attachment_summaries,
            max_length,
        )

        try:
            response = self.llm.invoke(messages)
            return response.content.strip()
        except Exception as e:
            raise RuntimeError(f"Failed to generate content: {str(e)}")

    def _build_messages(
        self,
        title: str,
        questions: str,
        user_input: str,
        best_practice_examples: List[str],
        max_length: int,
    ) -> List[BaseMessage]:
        """
        Build the message chain for the LLM.

        Args:
            title: The section title
            questions: Questions to guide the content
            user_input: User-provided input
            best_practice_examples: List of example texts
            max_length: Maximum length constraint

        Returns:
            List of messages for the LLM
        """
        system_prompt = self._create_system_prompt(max_length)
        human_prompt = self._create_human_prompt(
            title, questions, user_input, best_practice_examples
        )

        return [
            SystemMessage(content=system_prompt),
            HumanMessage(content=human_prompt),
        ]

    def _build_messages_with_attachments(
        self,
        title: str,
        questions: str,
        user_input: str,
        best_practice_examples: List[str],
        attachment_summaries: List[str],
        max_length: int,
    ) -> List[BaseMessage]:
        """
        Build the message chain for the LLM, including attachment summaries.

        Args:
            title: The section title
            questions: Questions to guide the content
            user_input: User-provided input
            best_practice_examples: List of example texts
            attachment_summaries: List of AI-generated summaries from attachments
            max_length: Maximum length constraint

        Returns:
            List of messages for the LLM
        """
        system_prompt = self._create_system_prompt(max_length)
        human_prompt = self._create_human_prompt_with_attachments(
            title, questions, user_input, best_practice_examples, attachment_summaries
        )

        return [
            SystemMessage(content=system_prompt),
            HumanMessage(content=human_prompt),
        ]

    def _create_system_prompt(self, max_length: int) -> str:
        """
        Create the system prompt for the LLM.

        Args:
            max_length: Maximum length constraint

        Returns:
            System prompt string
        """
        base_prompt = """Du bist ein Experte für die Erstellung von Projekt- und Förderanträgen für Wirtschaftsunternehmen. 

Deine Aufgabe ist es, basierend auf den gegebenen Leitfragen, dem Benutzerinput und den Best-Practice-Beispielen einen professionellen und strukturierten Abschnitt zu verfassen.

Beachte dabei:
- Verwende eine professionelle, aber zugängliche Sprache
- Strukturiere den Text logisch und kohärent
- Nutze die Best-Practice-Beispiele als Orientierung für Stil und Tiefe
- Gehe spezifisch auf den Benutzerinput ein
- Stelle sicher, dass alle wichtigen Aspekte der Leitfragen abgedeckt werden"""

        if max_length > 0:
            base_prompt += f"\n- Halte den Text unter {max_length} Zeichen"

        return base_prompt

    def _create_human_prompt(
        self,
        title: str,
        questions: str,
        user_input: str,
        best_practice_examples: List[str],
    ) -> str:
        """
        Create the human prompt for the LLM.

        Args:
            title: The section title
            questions: Questions to guide the content
            user_input: User-provided input
            best_practice_examples: List of example texts

        Returns:
            Human prompt string
        """
        examples_text = "\n\n".join(
            [
                f"Beispiel {i+1}:\n{example}"
                for i, example in enumerate(best_practice_examples)
            ]
        )

        return f"""Abschnittstitel: {title}

Leitfragen:
{questions}

Benutzerinput:
{user_input}

Best-Practice-Beispiele:
{examples_text}

Bitte erstelle basierend auf diesen Informationen einen professionellen Abschnitt für einen Projektantrag. Wiederhole den Abschnittstitel nicht im Text, sondern beginne direkt mit dem Inhalt."""

    def _create_human_prompt_with_attachments(
        self,
        title: str,
        questions: str,
        user_input: str,
        best_practice_examples: List[str],
        attachment_summaries: List[str],
    ) -> str:
        """
        Create the human prompt for the LLM, including attachment summaries.

        Args:
            title: The section title
            questions: Questions to guide the content
            user_input: User-provided input
            attachment_summaries: List of  additional details provided by the user
            best_practice_examples: List of example texts


        Returns:
            Human prompt string
        """
        examples_text = "\n\n".join(
            [
                f"Beispiel {i+1}:\n{example}"
                for i, example in enumerate(best_practice_examples)
            ]
        )
        attachments_text = "\n\n".join(
            [
                f"Anhangszusammenfassung {i+1}:\n{summary}"
                for i, summary in enumerate(attachment_summaries)
            ]
        )

        return f"""Abschnittstitel: {title}

Leitfragen:
{questions}

Benutzerinput:
{user_input}

Zusätzliche Details:
{attachments_text}

Best-Practice-Beispiele:
{examples_text}


Bitte erstelle basierend auf diesen Informationen einen professionellen Abschnitt für einen Projektantrag. Wiederhole den Abschnittstitel nicht im Text, sondern beginne direkt mit dem Inhalt."""

"""
LLM service for generating section content.

This module provides an abstraction layer for LLM interactions,
supporting both OpenAI and Anthropic (Claude) models through LangChain.
"""

import os
from typing import List, Optional
from langchain.schema import BaseMessage, HumanMessage, SystemMessage
from langchain_openai import ChatOpenAI

from ..config.logging import get_logger
from ..config.prompts import (
    get_system_prompt,
    get_human_prompt,
    get_human_prompt_with_attachments,
)


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
        self.logger = get_logger("services.llm_service")

        if model_name not in self.SUPPORTED_MODELS:
            error_msg = f"Unsupported model: {model_name}. Supported models: {list(self.SUPPORTED_MODELS.keys())}"
            self.logger.error(error_msg)
            raise ValueError(error_msg)

        self.model_name = model_name
        # Important: Temperature is set to 1 as the default value, as it is now unsupported by the OpenAI GPT5 Models
        self.temperature = temperature
        self.provider = self.SUPPORTED_MODELS[model_name]
        self._llm = None

        self.logger.info(
            f"Initialized LLM service with model: {model_name}, provider: {self.provider}"
        )

    @property
    def llm(self):
        """
        Lazy initialization of the LLM instance based on provider.

        Returns:
            Configured LLM instance (ChatOpenAI or ChatAnthropic)
        """
        if self._llm is None:
            self.logger.debug(f"Initializing LLM client for provider: {self.provider}")

            if self.provider == "openai":
                api_key = os.getenv("OPENAI_API_KEY")
                if not api_key:
                    error_msg = "OPENAI_API_KEY environment variable is required for OpenAI models"
                    self.logger.error(error_msg)
                    raise ValueError(error_msg)

                self._llm = ChatOpenAI(
                    model=self.model_name, temperature=self.temperature, api_key=api_key
                )
                self.logger.info(
                    f"OpenAI client initialized successfully for model: {self.model_name}"
                )

            elif self.provider == "anthropic":
                try:
                    from langchain_anthropic import ChatAnthropic
                except ImportError:
                    error_msg = "langchain_anthropic is required for Anthropic models. Install with: pip install langchain-anthropic"
                    self.logger.error(error_msg)
                    raise ValueError(error_msg)

                api_key = os.getenv("ANTHROPIC_API_KEY")
                if not api_key:
                    error_msg = "ANTHROPIC_API_KEY environment variable is required for Anthropic models"
                    self.logger.error(error_msg)
                    raise ValueError(error_msg)

                self._llm = ChatAnthropic(
                    model=self.model_name, temperature=self.temperature, api_key=api_key
                )
                self.logger.info(
                    f"Anthropic client initialized successfully for model: {self.model_name}"
                )
            else:
                error_msg = f"Unsupported provider: {self.provider}"
                self.logger.error(error_msg)
                raise ValueError(error_msg)

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
        self.logger.info(f"Generating content for section: {title}")
        self.logger.debug(
            f"Section parameters - Questions length: {len(questions)}, "
            f"User input length: {len(user_input)}, "
            f"Examples count: {len(best_practice_examples)}, "
            f"Max length: {max_length}"
        )

        messages = self._build_messages(
            title, questions, user_input, best_practice_examples, max_length
        )

        try:
            response = self.llm.invoke(messages)
            content = response.content.strip()
            self.logger.info(
                f"Successfully generated content for section: {title}, "
                f"Length: {len(content)} characters"
            )
            return content
        except Exception as e:
            error_msg = f"Failed to generate content for section '{title}': {str(e)}"
            self.logger.error(error_msg)
            raise RuntimeError(error_msg)

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
        self.logger.info(f"Generating content with attachments for section: {title}")
        self.logger.debug(
            f"Section parameters - Questions length: {len(questions)}, "
            f"User input length: {len(user_input)}, "
            f"Examples count: {len(best_practice_examples)}, "
            f"Attachments count: {len(attachment_summaries)}, "
            f"Max length: {max_length}"
        )

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
            content = response.content.strip()
            self.logger.info(
                f"Successfully generated content with attachments for section: {title}, "
                f"Length: {len(content)} characters"
            )
            return content
        except Exception as e:
            error_msg = f"Failed to generate content with attachments for section '{title}': {str(e)}"
            self.logger.error(error_msg)
            raise RuntimeError(error_msg)

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
        system_prompt = get_system_prompt(max_length)
        human_prompt = get_human_prompt(
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
        system_prompt = get_system_prompt(max_length)
        human_prompt = get_human_prompt_with_attachments(
            title, questions, user_input, best_practice_examples, attachment_summaries
        )

        return [
            SystemMessage(content=system_prompt),
            HumanMessage(content=human_prompt),
        ]

"""
LLM prompt templates and configurations.

This module contains all German prompt templates used for proposal generation.
"""

from typing import Dict, Any

# System prompt for proposal generation
PROPOSAL_SYSTEM_PROMPT = """Du bist ein Experte für die Erstellung von Projekt- und Förderanträgen für Wirtschaftsunternehmen. 

Deine Aufgabe ist es, basierend auf den gegebenen Leitfragen, dem Benutzerinput und den Best-Practice-Beispielen einen professionellen und strukturierten Abschnitt zu verfassen.

Beachte dabei:
- Verwende eine professionelle, aber zugängliche Sprache
- Strukturiere den Text logisch und kohärent
- Nutze die Best-Practice-Beispiele als Orientierung für Stil und Tiefe
- Gehe spezifisch auf den Benutzerinput ein
- Stelle sicher, dass alle wichtigen Aspekte der Leitfragen abgedeckt werden"""

# Human prompt template for standard content generation
HUMAN_PROMPT_TEMPLATE = """Abschnittstitel: {title}

Leitfragen:
{questions}

Benutzerinput:
{user_input}

Best-Practice-Beispiele:
{examples_text}

Bitte erstelle basierend auf diesen Informationen einen professionellen Abschnitt für einen Projektantrag. Wiederhole den Abschnittstitel nicht im Text, sondern beginne direkt mit dem Inhalt."""

# Human prompt template for content generation with attachments
HUMAN_PROMPT_WITH_ATTACHMENTS_TEMPLATE = """Abschnittstitel: {title}

Leitfragen:
{questions}

Benutzerinput:
{user_input}

Zusätzliche Details:
{attachments_text}

Best-Practice-Beispiele:
{examples_text}

Bitte erstelle basierend auf diesen Informationen einen professionellen Abschnitt für einen Projektantrag. Wiederhole den Abschnittstitel nicht im Text, sondern beginne direkt mit dem Inhalt."""

# Example formatting templates
EXAMPLE_TEXT_TEMPLATE = "Beispiel {index}:\n{content}"
ATTACHMENT_TEXT_TEMPLATE = "Anhangszusammenfassung {index}:\n{content}"

# Length constraint template
LENGTH_CONSTRAINT_TEXT = "\n- Halte den Text unter {max_length} Zeichen"


def format_examples(examples: list[str]) -> str:
    """Format best practice examples for the prompt."""
    return "\n\n".join([
        EXAMPLE_TEXT_TEMPLATE.format(index=i+1, content=example)
        for i, example in enumerate(examples)
    ])


def format_attachments(summaries: list[str]) -> str:
    """Format attachment summaries for the prompt."""
    return "\n\n".join([
        ATTACHMENT_TEXT_TEMPLATE.format(index=i+1, content=summary)
        for i, summary in enumerate(summaries)
    ])


def get_system_prompt(max_length: int = 0) -> str:
    """
    Get the system prompt with optional length constraint.
    
    Args:
        max_length: Maximum length constraint (0 for no limit)
        
    Returns:
        Formatted system prompt
    """
    prompt = PROPOSAL_SYSTEM_PROMPT
    if max_length > 0:
        prompt += LENGTH_CONSTRAINT_TEXT.format(max_length=max_length)
    return prompt


def get_human_prompt(
    title: str,
    questions: str,
    user_input: str,
    best_practice_examples: list[str],
) -> str:
    """
    Get the human prompt for standard content generation.
    
    Args:
        title: The section title
        questions: Questions to guide the content
        user_input: User-provided input
        best_practice_examples: List of example texts
        
    Returns:
        Formatted human prompt
    """
    examples_text = format_examples(best_practice_examples)
    
    return HUMAN_PROMPT_TEMPLATE.format(
        title=title,
        questions=questions,
        user_input=user_input,
        examples_text=examples_text,
    )


def get_human_prompt_with_attachments(
    title: str,
    questions: str,
    user_input: str,
    best_practice_examples: list[str],
    attachment_summaries: list[str],
) -> str:
    """
    Get the human prompt for content generation with attachments.
    
    Args:
        title: The section title
        questions: Questions to guide the content
        user_input: User-provided input
        best_practice_examples: List of example texts
        attachment_summaries: List of attachment summaries
        
    Returns:
        Formatted human prompt with attachments
    """
    examples_text = format_examples(best_practice_examples)
    attachments_text = format_attachments(attachment_summaries)
    
    return HUMAN_PROMPT_WITH_ATTACHMENTS_TEMPLATE.format(
        title=title,
        questions=questions,
        user_input=user_input,
        attachments_text=attachments_text,
        examples_text=examples_text,
    )

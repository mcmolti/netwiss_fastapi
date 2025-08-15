"""
Template service (for now with placeholder/mock data) for loading and managing proposal templates.
"""

import json
import os
from typing import Dict, List
from ..models.template import ProposalTemplate, TemplateListItem, TemplateSection


class TemplateService:
    """
    Service for managing proposal templates.
    """

    def __init__(self):
        """Initialize the template service."""
        self.data_dir = os.path.join(os.path.dirname(__file__), "../../data")

    async def get_available_templates(self) -> List[TemplateListItem]:
        """
        Get a list of available proposal templates.

        Returns:
            List of available templates
        """
        return [
            TemplateListItem(
                id="digi4wirtschaft",
                name="Digi4Wirtschaft WKNOE",
                description="Template for digital economy funding applications",
            ),
            TemplateListItem(
                id="digitalisierung_WA",
                name="Digitalisierung Wirtschaftsagentur Wien",
                description="Template for digital economy funding applications",
            ),
        ]

    async def get_template(self, template_id: str) -> ProposalTemplate:
        """
        Load a specific proposal template.

        Args:
            template_id: The ID of the template to load

        Returns:
            The loaded template

        Raises:
            FileNotFoundError: If template doesn't exist
            ValueError: If template_id is invalid
        """

        template_path = os.path.join(self.data_dir, f"{template_id}.json")

        if not os.path.exists(template_path):
            raise FileNotFoundError(f"Template file not found: {template_path}")

        with open(template_path, "r", encoding="utf-8") as file:
            data = json.load(file)

        # Process the data to handle both field name variations
        processed_sections = {}
        for section_id, section_data in data["sections"].items():
            section = section_data.copy()

            # Handle both 'best_practice_beispiele' and 'best_practice_examples'
            if (
                "best_practice_examples" in section
                and "best_practice_beispiele" not in section
            ):
                section["best_practice_beispiele"] = section["best_practice_examples"]
            elif "best_practice_beispiele" not in section:
                section["best_practice_beispiele"] = []

            processed_sections[section_id] = TemplateSection(**section)

        return ProposalTemplate(sections=processed_sections)

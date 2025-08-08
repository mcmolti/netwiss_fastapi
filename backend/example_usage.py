#!/usr/bin/env python3
"""
Example usage script for the proposal generation FastAPI backend.

This script demonstrates how to make requests to the API with sample data.
"""

import json
import requests
import time
from typing import Dict, Any

# API configuration
API_BASE_URL = "http://localhost:8000"


def check_server_health() -> bool:
    """Check if the server is running and healthy."""
    try:
        response = requests.get(f"{API_BASE_URL}/health", timeout=5)
        if response.status_code == 200:
            health_data = response.json()
            print(f"✅ Server is healthy")
            print(
                f"   OpenAI API Key configured: {health_data.get('openai_api_key_configured', False)}"
            )
            return True
        else:
            print(f"❌ Server returned status {response.status_code}")
            return False
    except requests.exceptions.RequestException as e:
        print(f"❌ Cannot connect to server: {e}")
        return False


def create_sample_request() -> Dict[str, Any]:
    """Create a sample request with minimal data."""
    return {
        "sections": {
            "kurzvorstellung": {
                "title": "Kurzvorstellung des Unternehmens",
                "questions": "Welche Produkte oder Dienstleistungen bieten Sie an? Wer sind Ihre Zielgruppen?",
                "best_practice_beispiele": [
                    "Wir sind ein innovatives Tech-Startup im Bereich KI-Lösungen für kleine und mittlere Unternehmen."
                ],
                "user_input": "Unser Unternehmen entwickelt KI-gestützte Chatbots für den Kundenservice in der Gastronomie. Wir richten uns an Restaurants, Cafés und Hotels, die ihre Kundenbetreuung digitalisieren möchten.",
                "max_section_length": 500,
            }
        }
    }


def send_generation_request(request_data: Dict[str, Any]) -> Dict[str, Any]:
    """Send a generation request to the API."""
    try:
        print("📤 Sending generation request...")
        response = requests.post(
            f"{API_BASE_URL}/api/v1/generate-sections",
            json=request_data,
            headers={"Content-Type": "application/json"},
            timeout=30,
        )

        if response.status_code == 200:
            print("✅ Request successful!")
            return response.json()
        else:
            print(f"❌ Request failed with status {response.status_code}")
            print(f"Error: {response.text}")
            return {}
    except requests.exceptions.RequestException as e:
        print(f"❌ Request error: {e}")
        return {}


def display_results(response_data: Dict[str, Any]):
    """Display the generated results in a readable format."""
    if not response_data:
        return

    print("\n" + "=" * 60)
    print("📋 GENERATION RESULTS")
    print("=" * 60)

    overall_status = response_data.get("status", "unknown")
    print(f"Overall Status: {overall_status}")

    sections = response_data.get("sections", {})

    for section_name, section_data in sections.items():
        print(f"\n📄 Section: {section_name}")
        print(f"Title: {section_data.get('title', 'N/A')}")
        print(f"Status: {section_data.get('status', 'N/A')}")
        print(f"User Input: {section_data.get('user_input', 'N/A')[:100]}...")

        generated_content = section_data.get("generated_content", "")
        if generated_content:
            print("\n🤖 Generated Content:")
            print("-" * 40)
            print(generated_content)
            print("-" * 40)
        else:
            print("\n⚠️  No content generated")


def main():
    """Main function to run the example."""
    print("🚀 Proposal Generation API Example")
    print("=" * 40)

    # Check server health
    print("\n1. Checking server health...")
    if not check_server_health():
        print("\n❌ Server is not available. Please start the server first:")
        print("   cd backend && uv run python main.py")
        return

    # Create sample request
    print("\n2. Creating sample request...")
    request_data = create_sample_request()
    print(f"   Created request with {len(request_data['sections'])} section(s)")

    # Send request
    print("\n3. Sending generation request...")
    response_data = send_generation_request(request_data)

    # Display results
    if response_data:
        display_results(response_data)

    print(f"\n✨ Example completed!")


if __name__ == "__main__":
    main()

#!/usr/bin/env python3
"""Test the generate-sections endpoint with URL attachments."""

import requests
import json


def test_generation_with_url():
    """Test section generation with URL attachment."""

    # First, let's test with a simple URL to see if it gets processed
    payload = {
        "model": "gpt-4o-mini",
        "sections": {
            "test_section": {
                "title": "Test Section",
                "questions": "What is this content about?",
                "best_practice_beispiele": [],
                "user_input": "This is a test section with URL attachment.",
                "max_section_length": 0,
                "attached_files": [],
                "attached_urls": ["https://www.python.org"],
                "attachment_summaries": [],
            }
        },
    }

    print("Sending payload:")
    print(json.dumps(payload, indent=2))
    print("\n" + "=" * 50 + "\n")

    try:
        response = requests.post(
            "http://localhost:8000/api/v1/generate-sections",
            json=payload,
            headers={"Content-Type": "application/json"},
        )
        print(f"Response status: {response.status_code}")
        print("Response body:")
        print(response.text)

        if response.status_code == 200:
            result = response.json()
            print("\n" + "=" * 50)
            print("Generated content:")
            for section_name, section_data in result.get("sections", {}).items():
                print(f"\n{section_name}:")
                print(f"Content: {section_data.get('generated_content', 'N/A')}")
                print(f"Status: {section_data.get('status', 'N/A')}")

    except Exception as e:
        print(f"Error: {e}")


if __name__ == "__main__":
    test_generation_with_url()

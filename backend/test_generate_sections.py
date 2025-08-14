#!/usr/bin/env python3
"""
Test script for the generate-sections API endpoint.
"""

import asyncio
import aiohttp
import json


async def test_generate_sections():
    """Test the generate-sections API endpoint."""
    url = "http://localhost:8000/api/v1/generate-sections"

    # Create a test payload similar to what the frontend sends
    payload = {
        "model": "gpt-4o-mini",
        "sections": {
            "test_section": {
                "title": "Test Section",
                "questions": "What are the main benefits?",
                "best_practice_beispiele": [],
                "user_input": "This is a test input",
                "max_section_length": 1000,
                "attached_files": [],
                "attached_urls": ["https://httpbin.org/html"],
            }
        },
    }

    async with aiohttp.ClientSession() as session:
        try:
            async with session.post(url, json=payload) as response:
                print(f"Status Code: {response.status}")

                if response.status == 200:
                    result = await response.json()
                    print(f"✓ Generate sections successful")
                    print(f"  - Status: {result.get('status', 'N/A')}")
                    if "sections" in result:
                        for section_key, section_data in result["sections"].items():
                            print(
                                f"  - Section {section_key}: {section_data.get('status', 'N/A')}"
                            )
                else:
                    error_text = await response.text()
                    print(f"✗ Error {response.status}: {error_text}")

        except Exception as e:
            print(f"✗ Request failed: {str(e)}")


if __name__ == "__main__":
    print("Testing generate-sections API endpoint...")
    asyncio.run(test_generate_sections())

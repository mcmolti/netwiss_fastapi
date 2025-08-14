#!/usr/bin/env python3
"""
Test script for URL extraction API endpoint.
"""

import asyncio
import aiohttp
import json


async def test_url_extraction():
    """Test the URL extraction API endpoint."""
    url = "http://localhost:8000/api/urls/extract"
    payload = {"url": "https://httpbin.org/html"}

    async with aiohttp.ClientSession() as session:
        try:
            async with session.post(url, json=payload) as response:
                print(f"Status Code: {response.status}")

                if response.status == 200:
                    result = await response.json()
                    print(f"✓ URL extraction successful")
                    print(f"  - URL: {result['url']}")
                    print(f"  - Status: {result['status']}")
                    print(f"  - Title: {result.get('title', 'N/A')}")
                    print(f"  - Content length: {len(result['content'])} characters")
                    print(f"  - Content preview: {result['content'][:100]}...")
                else:
                    error_text = await response.text()
                    print(f"✗ Error {response.status}: {error_text}")

        except Exception as e:
            print(f"✗ Request failed: {str(e)}")


if __name__ == "__main__":
    print("Testing URL extraction API endpoint...")
    asyncio.run(test_url_extraction())

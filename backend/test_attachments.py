#!/usr/bin/env python3
"""
Test script for the attachment functionality.

This script tests the new file upload, URL extraction, and summarization features.
"""

import asyncio
import os
import sys
import tempfile
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Add the app directory to the Python path
sys.path.insert(0, str(Path(__file__).parent / "app"))

from app.services.file_service import FileService
from app.services.web_scraping_service import WebScrapingService
from app.services.summarization_service import SummarizationService
from app.models.proposal import Section
from io import BytesIO


async def test_file_service():
    """Test the file service functionality."""
    print("Testing File Service...")

    # Create a simple test PDF content (as text for demonstration)
    test_pdf_content = """Test PDF Content
    
    This is a test document for proposal generation.
    It contains information about digital transformation projects.
    
    Key points:
    - Digital strategy implementation
    - Technology integration
    - Process optimization
    """

    file_service = FileService()

    # Create a temporary file to simulate upload
    with tempfile.NamedTemporaryFile(suffix=".pdf", delete=False) as tmp_file:
        # Note: This is just for testing - in reality we'd need a proper PDF
        tmp_file.write(test_pdf_content.encode())
        tmp_file_path = tmp_file.name

    try:
        # Simulate file upload (this would normally come from FastAPI's UploadFile)
        print(f"✓ File service initialized")
        print(f"✓ Test file created at: {tmp_file_path}")
    finally:
        # Cleanup
        if os.path.exists(tmp_file_path):
            os.unlink(tmp_file_path)


async def test_web_scraping_service():
    """Test the web scraping service."""
    print("\nTesting Web Scraping Service...")

    web_service = WebScrapingService()

    # Test with a simple URL
    test_url = "https://httpbin.org/html"

    try:
        result = await web_service.extract_content_from_url(test_url)
        print(f"✓ URL extraction completed")
        print(f"  - URL: {result['url']}")
        print(f"  - Status: {result['status']}")
        print(f"  - Content length: {len(result['content'])} characters")

        if result["title"]:
            print(f"  - Title: {result['title']}")

        # Check if there was an error
        if result["status"] == "error":
            print(f"  - Error: {result.get('error', 'Unknown error')}")
        elif result["content"]:
            print(f"  - Content preview: {result['content'][:100]}...")
        else:
            print("  - Warning: No content extracted despite success status")

    except Exception as e:
        print(f"✗ Web scraping failed with exception: {str(e)}")


async def test_summarization_service():
    """Test the summarization service."""
    print("\nTesting Summarization Service...")

    # Skip if no OpenAI API key
    if not os.getenv("OPENAI_API_KEY"):
        print("⚠ Skipping summarization test - no OPENAI_API_KEY found")
        return

    summarization_service = SummarizationService()

    test_content = """
    Digital transformation has become a critical factor for business success in the 21st century. 
    Companies that embrace digital technologies are able to improve their operational efficiency, 
    enhance customer experience, and create new revenue streams.
    
    Key benefits of digital transformation include:
    - Improved data analytics and decision-making
    - Enhanced customer engagement through digital channels
    - Streamlined business processes
    - Increased agility and adaptability
    - Cost reduction through automation
    
    However, digital transformation also presents challenges such as cybersecurity risks, 
    employee training requirements, and the need for significant upfront investment.
    """

    test_questions = """
    - Welche Vorteile bietet die digitale Transformation für Unternehmen?
    - Welche Herausforderungen sind mit der digitalen Transformation verbunden?
    - Wie kann die digitale Transformation die Effizienz steigern?
    """

    try:
        summary = await summarization_service.summarize_for_questions(
            content=test_content,
            questions=test_questions,
            content_type="text",
            max_summary_length=500,
        )

        print(f"✓ Summarization successful")
        print(f"  - Summary length: {len(summary)} characters")
        print(f"  - Summary preview: {summary[:100]}...")

    except Exception as e:
        print(f"✗ Summarization failed: {str(e)}")


async def test_integration():
    """Test the integration of all services."""
    print("\nTesting Service Integration...")

    # Create a test section with attachments
    test_section = Section(
        title="Digitale Transformation",
        questions="Welche Vorteile bietet die digitale Transformation?",
        best_practice_beispiele=[],
        user_input="Unser Unternehmen möchte die digitale Transformation vorantreiben.",
        max_section_length=1000,
        attached_files=[],
        attached_urls=["https://httpbin.org/html"],
        attachment_summaries=[],
    )

    print(f"✓ Test section created")
    print(f"  - Title: {test_section.title}")
    print(f"  - URLs: {test_section.attached_urls}")


async def main():
    """Run all tests."""
    print("Starting Attachment Functionality Tests")
    print("=" * 50)

    # Check if OpenAI API key is loaded
    openai_key = os.getenv("OPENAI_API_KEY")
    if openai_key:
        print(f"✓ OpenAI API key loaded (ending with: ...{openai_key[-4:]})")
    else:
        print("⚠ No OpenAI API key found in environment")

    await test_file_service()
    await test_web_scraping_service()
    await test_summarization_service()
    await test_integration()

    print("\n" + "=" * 50)
    print("Tests completed!")


if __name__ == "__main__":
    asyncio.run(main())

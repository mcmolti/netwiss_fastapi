#!/usr/bin/env python3
"""
Simple test script to verify the FastAPI backend setup.

This script tests the basic functionality without requiring an OpenAI API key.
"""

import json
import sys
from pathlib import Path

# Add the backend directory to the Python path
backend_dir = Path(__file__).parent
sys.path.insert(0, str(backend_dir))


def test_imports():
    """Test that all modules can be imported successfully."""
    try:
        from app.models import ProposalRequest, Section
        from app.services import ProposalGenerationService

        print("✅ All modules imported successfully")
        return True
    except ImportError as e:
        print(f"❌ Import error: {e}")
        return False


def test_models():
    """Test that Pydantic models work correctly."""
    try:
        from app.models import Section, ProposalRequest

        # Create a test section
        section = Section(
            title="Test Section",
            questions="What is this test about?",
            best_practice_beispiele=["Example 1", "Example 2"],
            user_input="This is a test input",
            max_section_length=500,
        )

        # Create a test request
        request = ProposalRequest(sections={"test": section})

        print("✅ Pydantic models work correctly")
        return True
    except Exception as e:
        print(f"❌ Model error: {e}")
        return False


def test_service_without_llm():
    """Test service initialization without LLM calls."""
    try:
        from app.services import ProposalGenerationService, LLMService

        # Create service (this should work even without API key)
        llm_service = LLMService()
        service = ProposalGenerationService(llm_service)

        print("✅ Service initialization successful")
        return True
    except Exception as e:
        print(f"❌ Service error: {e}")
        return False


def load_test_data():
    """Load the test data from the digi4wirtschaft.json example proposal file."""
    try:
        db_file = backend_dir.parent / "db_placeholder" / "digi4wirtschaft.json"
        with open(db_file, "r", encoding="utf-8") as f:
            data = json.load(f)

        # Convert to request format
        from app.models import ProposalRequest

        request = ProposalRequest(**data)

        print("✅ Test data loaded successfully")
        print(f"   Found {len(request.sections)} sections")
        return True
    except Exception as e:
        print(f"❌ Test data error: {e}")
        return False


def main():
    """Run all tests."""
    print("🧪 Testing proposal generation backend setup...\n")

    tests = [
        ("Import Test", test_imports),
        ("Model Test", test_models),
        ("Service Test", test_service_without_llm),
        ("Test Data", load_test_data),
    ]

    passed = 0
    total = len(tests)

    for test_name, test_func in tests:
        print(f"Running {test_name}...")
        if test_func():
            passed += 1
        print()

    print(f"🎯 Test Results: {passed}/{total} tests passed")

    if passed == total:
        print("🚀 Backend setup is ready!")
        print("\nNext steps:")
        print("1. Copy .env.example to .env")
        print("2. Add your OpenAI API key to .env")
        print("3. Run: uv run python main.py")
    else:
        print("❌ Some tests failed. Please check the errors above.")
        sys.exit(1)


if __name__ == "__main__":
    main()

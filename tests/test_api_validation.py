"""
Quick API Key Validation Test
Test szybkiej walidacji klucza API
"""

import os
import pytest
import sys

# Add parent directory to Python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


class TestAPIKeyValidation:
    """Test validation of OpenAI API key"""

    def test_api_key_exists(self):
        """Test that OPENAI_API_KEY is set"""
        api_key = os.environ.get("OPENAI_API_KEY")

        if not api_key:
            pytest.skip("OPENAI_API_KEY not set - skipping API validation")

        assert api_key is not None, "OPENAI_API_KEY should be set"
        assert len(api_key) > 10, "OPENAI_API_KEY should be at least 10 characters"
        assert api_key.startswith("sk-"), "OPENAI_API_KEY should start with 'sk-'"

        print(f"✅ API Key detected: {api_key[:10]}...{api_key[-4:]}")

    @pytest.mark.autogen
    def test_config_validation(self):
        """Test that config can validate API key"""
        try:
            from config.llm_config import validate_api_key

            if not os.environ.get("OPENAI_API_KEY"):
                pytest.skip("OPENAI_API_KEY not set - skipping config validation")

            result = validate_api_key()
            assert result is True, "API key validation should pass"

            print("✅ Config validation passed")

        except ImportError as e:
            pytest.fail(f"Failed to import config validation: {e}")

    @pytest.mark.autogen
    @pytest.mark.online
    def test_simple_autogen_import(self):
        """Test that AutoGen agents can be imported with valid API key"""
        api_key = os.environ.get("OPENAI_API_KEY")

        if not api_key:
            pytest.skip("OPENAI_API_KEY not set - skipping AutoGen test")

        try:
            from autogen_agents import data_collector, user_proxy

            assert (
                data_collector is not None
            ), "Data collector agent should be available"
            assert user_proxy is not None, "User proxy agent should be available"

            # Test agent names
            assert hasattr(data_collector, "name"), "Agent should have name attribute"
            assert (
                data_collector.name == "DATA_COLLECTOR_agent"
            ), "Agent name should match expected"

            print("✅ AutoGen agents imported successfully")

        except Exception as e:
            pytest.fail(f"Failed to import AutoGen agents: {e}")

    def test_print_help_message(self):
        """Print helpful information about API key setup"""
        api_key = os.environ.get("OPENAI_API_KEY")

        print("\n" + "=" * 60)
        print("🔑 OPENAI_API_KEY STATUS")
        print("=" * 60)

        if not api_key:
            print("❌ OPENAI_API_KEY not set")
            print("\n📝 To set your API key:")
            print("   1. export OPENAI_API_KEY='not-secure-key'")
            print("   2. Or create .env file with your key")
            print("   3. Or run: OPENAI_API_KEY='not-secure-key' pytest")
        else:
            print(f"✅ OPENAI_API_KEY found: {api_key[:10]}...{api_key[-4:]}")
            print(f"📏 Length: {len(api_key)} characters")
            print(
                f"🔍 Format: {'✅ Valid' if api_key.startswith('sk-') else '❌ Invalid'}"
            )

        print("\n🧪 Run these tests with API key:")
        print("   make test-autogen      # AutoGen agent tests")
        print("   make test-online       # Online API tests")
        print("   make test-integration  # Integration tests")
        print("=" * 60)

        # Always pass this informational test
        assert True

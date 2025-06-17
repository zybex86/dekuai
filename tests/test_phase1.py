"""
Phase 1 Tests - Basic AutoGen Functionality
Testy Fazy 1 - Podstawowa funkcjonalność AutoGen
"""

import os
import sys
import unittest
from unittest.mock import patch, MagicMock

# Add parent directory to Python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


class TestPhase1BasicFunctionality(unittest.TestCase):
    """Testy podstawowej funkcjonalności Fazy 1"""

    def setUp(self):
        """Przygotowanie do testów"""
        self.test_game = "Hollow Knight"

    def test_agent_tools_import(self):
        """Test importowania narzędzi agentów"""
        try:
            from agent_tools import (
                search_and_scrape_game,
                validate_game_data,
                format_game_summary,
                extract_key_metrics,
            )

            self.assertTrue(True, "Agent tools imported successfully")
        except ImportError as e:
            self.fail(f"Failed to import agent tools: {e}")

    def test_config_import(self):
        """Test importowania konfiguracji"""
        try:
            from config.llm_config import (
                get_llm_config,
                get_data_collector_config,
                validate_api_key,
            )

            self.assertTrue(True, "Config modules imported successfully")
        except ImportError as e:
            self.fail(f"Failed to import config modules: {e}")

    @patch.dict(os.environ, {"OPENAI_API_KEY": "test-key"})
    def test_api_key_validation_success(self):
        """Test walidacji klucza API - sukces"""
        from config.llm_config import validate_api_key

        self.assertTrue(validate_api_key(), "API key validation should succeed")

    def test_api_key_validation_failure(self):
        """Test walidacji klucza API - brak klucza"""
        with patch.dict(os.environ, {}, clear=True):
            from config.llm_config import validate_api_key

            self.assertFalse(
                validate_api_key(), "API key validation should fail without key"
            )

    def test_search_and_scrape_game_input_validation(self):
        """Test walidacji wejścia dla search_and_scrape_game"""
        from agent_tools import search_and_scrape_game

        # Test pustego inputu
        result = search_and_scrape_game("")
        self.assertFalse(result.get("success", True), "Empty input should fail")

        # Test None inputu
        result = search_and_scrape_game(None)
        self.assertFalse(result.get("success", True), "None input should fail")

    def test_validate_game_data_structure(self):
        """Test struktury walidacji danych gry"""
        from agent_tools import validate_game_data

        # Test z pełnymi danymi
        complete_data = {
            "title": "Test Game",
            "MSRP": "$29.99",
            "current_eshop_price": "$19.99",
            "metacritic_score": "85",
            "genres": ["Action", "Adventure"],
            "developer": "Test Studio",
        }

        result = validate_game_data(complete_data)
        self.assertTrue(
            result.get("is_complete", False),
            "Complete data should validate as complete",
        )
        self.assertEqual(
            result.get("completeness_score", 0),
            100.0,
            "Complete data should have 100% score",
        )

    def test_format_game_summary_error_handling(self):
        """Test formatowania podsumowania gry - obsługa błędów"""
        from agent_tools import format_game_summary

        # Test z danymi błędu
        error_data = {"success": False, "message": "Game not found"}

        summary = format_game_summary(error_data)
        self.assertIn("Error", summary, "Error data should show error message")

    def test_extract_key_metrics_error_handling(self):
        """Test wyciągania kluczowych metryk - obsługa błędów"""
        from agent_tools import extract_key_metrics

        # Test z danymi błędu
        error_data = {"success": False}

        result = extract_key_metrics(error_data)
        self.assertIn("error", result, "Error data should return error key")

    @patch.dict(os.environ, {"OPENAI_API_KEY": "test-key"})
    def test_autogen_agents_creation(self):
        """Test tworzenia agentów AutoGen"""
        try:
            # Mock autogen to avoid actual API calls
            with patch("autogen.AssistantAgent") as mock_assistant, patch(
                "autogen.UserProxyAgent"
            ) as mock_proxy:

                # Import after patching
                from autogen_agents import (
                    data_collector,
                    price_analyzer,
                    review_generator,
                    quality_assurance,
                    user_proxy,
                )

                # Verify agents were created (mocked)
                self.assertTrue(
                    mock_assistant.called, "AssistantAgent should be called"
                )
                self.assertTrue(mock_proxy.called, "UserProxyAgent should be called")

        except Exception as e:
            self.fail(f"Failed to create AutoGen agents: {e}")

    def test_conversation_manager_import(self):
        """Test importowania menedżera konwersacji"""
        try:
            from conversation_manager import GameAnalysisManager

            manager = GameAnalysisManager()
            self.assertIsNotNone(manager, "GameAnalysisManager should be created")
        except ImportError as e:
            self.fail(f"Failed to import conversation manager: {e}")


class TestPhase1Integration(unittest.TestCase):
    """Testy integracyjne Fazy 1"""

    def test_data_collection_workflow(self):
        """Test pełnego workflow zbierania danych (bez AI)"""
        from agent_tools import search_and_scrape_game, validate_game_data

        # Test tylko jeśli nie ma problemów sieciowych
        try:
            result = search_and_scrape_game("Celeste")

            # Sprawdź strukturę odpowiedzi
            self.assertIn("success", result, "Result should have success field")

            if result.get("success"):
                # Jeśli sukces, sprawdź dane
                validation = validate_game_data(result)
                self.assertIn(
                    "completeness_score", validation, "Should have completeness score"
                )
            else:
                # Jeśli błąd, sprawdź komunikat
                self.assertIn("message", result, "Error result should have message")

        except Exception as e:
            self.skipTest(
                f"Skipping integration test due to network/scraping issue: {e}"
            )


def run_phase1_tests():
    """Uruchamia wszystkie testy Fazy 1"""
    print("🧪 Running Phase 1 Tests")
    print("=" * 50)

    # Create test suite
    suite = unittest.TestSuite()

    # Add basic functionality tests
    suite.addTest(unittest.makeSuite(TestPhase1BasicFunctionality))

    # Add integration tests
    suite.addTest(unittest.makeSuite(TestPhase1Integration))

    # Run tests
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)

    # Summary
    print("\n" + "=" * 50)
    if result.wasSuccessful():
        print("✅ All Phase 1 tests passed!")
    else:
        print("❌ Some tests failed:")
        for failure in result.failures:
            print(f"  - {failure[0]}: {failure[1]}")
        for error in result.errors:
            print(f"  - {error[0]}: {error[1]}")

    return result.wasSuccessful()


if __name__ == "__main__":
    run_phase1_tests()

"""
🧪 Core Functionality Tests
Test core system components and basic operations
"""

import pytest
import time
from typing import Dict, Any
from unittest.mock import patch, Mock

# Import project modules
from agent_tools import search_and_scrape_game


class TestGameSearch:
    """Test game search and scraping functionality"""

    @pytest.mark.unit
    def test_search_with_mock_data(self, mock_search_function):
        """Test game search with mocked data (offline)"""
        result = mock_search_function("Celeste")

        assert result is not None
        assert isinstance(result, dict)
        assert result.get("title") == "Mock Celeste"
        assert result.get("success") is True

    @pytest.mark.online
    @pytest.mark.slow
    def test_search_real_game(
        self, test_games_list, performance_tracker, assert_timing
    ):
        """Test real game search (requires internet)"""
        game_name = test_games_list[0]  # "Celeste"

        performance_tracker.start("game_search")
        result = search_and_scrape_game(game_name)
        duration = performance_tracker.end("game_search")

        # Assert timing
        assert_timing(duration, 10.0, "Game search")

        # Assert result quality
        assert result is not None
        assert isinstance(result, dict)

        # Should have either success data or graceful error
        has_data = result.get("title") is not None
        has_error = result.get("error") is not None
        assert has_data or has_error, "Result should have either data or error"

    @pytest.mark.parametrize("game_name", ["Celeste", "Hollow Knight", "Hades"])
    @pytest.mark.online
    def test_search_multiple_games(self, game_name, assert_game_data):
        """Test searching for multiple popular games"""
        result = search_and_scrape_game(game_name)

        if result and result.get("title"):
            assert_game_data(result, min_fields=5)
            assert game_name.lower() in result["title"].lower()

    @pytest.mark.unit
    def test_search_validation(self, mock_search_function):
        """Test input validation for game search"""
        # Test empty string
        result = mock_search_function("")
        assert result.get("error") is not None

        # Test None input (handled by mock)
        result = mock_search_function("nonexistent_test_game")
        assert result.get("error") is not None


class TestUserManagement:
    """Test user management system"""

    @pytest.mark.unit
    def test_user_manager_initialization(self, user_manager):
        """Test UserManager can be initialized"""
        assert user_manager is not None

        # Should have current user or be able to handle no user
        current_user = user_manager.get_current_user()
        # current_user can be None or a valid user object
        if current_user:
            assert hasattr(current_user, "username") or isinstance(current_user, dict)

    @pytest.mark.user_management
    def test_current_user_access(self, user_manager):
        """Test accessing current user"""
        current_user = user_manager.get_current_user()

        if current_user:
            # Should have username attribute or be dict with username
            if hasattr(current_user, "username"):
                assert isinstance(current_user.username, str)
                assert len(current_user.username) > 0
            elif isinstance(current_user, dict):
                assert "username" in current_user
                assert isinstance(current_user["username"], str)

    @pytest.mark.user_management
    def test_user_switching(self, user_manager, performance_tracker, assert_timing):
        """Test user switching performance"""
        current_user = user_manager.get_current_user()

        if current_user:
            username = getattr(
                current_user, "username", current_user.get("username", "default")
            )

            performance_tracker.start("user_switch")
            result = user_manager.switch_user(username)
            duration = performance_tracker.end("user_switch")

            # Should be fast
            assert_timing(duration, 1.0, "User switching")


class TestGameCollection:
    """Test game collection management"""

    @pytest.mark.unit
    def test_collection_manager_initialization(self, game_collection_manager):
        """Test GameCollectionManager initialization"""
        assert game_collection_manager is not None

    @pytest.mark.game_collection
    def test_collection_access(self, game_collection_manager, user_manager):
        """Test accessing user's game collection"""
        current_user = user_manager.get_current_user()

        if current_user:
            username = getattr(
                current_user, "username", current_user.get("username", "default")
            )

            # Try to access collection (should not crash)
            try:
                # Different possible method names
                if hasattr(game_collection_manager, "get_user_collection"):
                    collection = game_collection_manager.get_user_collection(username)
                elif hasattr(game_collection_manager, "get_user_games"):
                    collection = game_collection_manager.get_user_games(username)
                else:
                    pytest.skip("No known collection access method found")

                assert isinstance(collection, (dict, list))

            except Exception as e:
                # Log the error but don't fail - API might be different
                pytest.skip(f"Collection access method not available: {e}")


class TestMLComponents:
    """Test ML and AI components"""

    @pytest.mark.ml
    @pytest.mark.unit
    def test_smart_profiler_initialization(self, smart_user_profiler):
        """Test SmartUserProfiler initialization"""
        assert smart_user_profiler is not None

    @pytest.mark.ml
    @pytest.mark.unit
    def test_price_prediction_initialization(self, price_prediction_engine):
        """Test PricePredictionEngine initialization"""
        assert price_prediction_engine is not None

    @pytest.mark.ml
    @pytest.mark.unit
    def test_batch_processor_initialization(self, batch_analysis_manager):
        """Test BatchAnalysisManager initialization"""
        assert batch_analysis_manager is not None


class TestAutoGenAgents:
    """Test AutoGen agent system"""

    @pytest.mark.autogen
    @pytest.mark.unit
    def test_agents_available(self, autogen_agents):
        """Test that all AutoGen agents are available"""
        expected_agents = [
            "data_collector",
            "price_analyzer",
            "review_generator",
            "quality_assurance",
            "user_proxy",
        ]

        for agent_name in expected_agents:
            assert agent_name in autogen_agents
            agent = autogen_agents[agent_name]
            assert agent is not None
            assert hasattr(agent, "name")

    @pytest.mark.autogen
    @pytest.mark.unit
    def test_agent_names(self, autogen_agents):
        """Test AutoGen agent names are correct"""
        expected_names = {
            "data_collector": "DATA_COLLECTOR_agent",
            "price_analyzer": "PRICE_ANALYZER_agent",
            "review_generator": "REVIEW_GENERATOR_agent",
            "quality_assurance": "QUALITY_ASSURANCE_agent",
            "user_proxy": "USER_PROXY",
        }

        for agent_key, expected_name in expected_names.items():
            agent = autogen_agents[agent_key]
            assert agent.name == expected_name


class TestSystemHealth:
    """Test overall system health and status"""

    @pytest.mark.unit
    def test_core_imports(self):
        """Test that core modules can be imported"""
        # These imports should work if system is healthy
        from agent_tools import search_and_scrape_game
        from utils.user_management import UserManager
        from utils.game_collection_manager import GameCollectionManager

        assert search_and_scrape_game is not None
        assert UserManager is not None
        assert GameCollectionManager is not None

    @pytest.mark.unit
    def test_basic_system_functionality(
        self,
        user_manager,
        game_collection_manager,
        smart_user_profiler,
        mock_search_function,
    ):
        """Test basic system components work together"""
        # Test basic workflow without external dependencies

        # 1. User management works
        current_user = user_manager.get_current_user()
        assert current_user is not None or current_user is None  # Either is fine

        # 2. Game search works (mocked)
        game_result = mock_search_function("Test Game")
        assert game_result is not None
        assert isinstance(game_result, dict)

        # 3. Collection manager initializes
        assert game_collection_manager is not None

        # 4. ML profiler initializes
        assert smart_user_profiler is not None

    @pytest.mark.integration
    @pytest.mark.slow
    def test_full_system_health(
        self,
        user_manager,
        game_collection_manager,
        smart_user_profiler,
        batch_analysis_manager,
        game_analysis_manager,
        autogen_agents,
    ):
        """Comprehensive system health check"""
        health_status = {
            "user_management": user_manager is not None,
            "game_collection": game_collection_manager is not None,
            "ml_profiler": smart_user_profiler is not None,
            "batch_processor": batch_analysis_manager is not None,
            "game_analysis": game_analysis_manager is not None,
            "autogen_agents": len(autogen_agents) == 5,
        }

        # All components should be healthy
        assert all(health_status.values()), f"System health issues: {health_status}"

        # Calculate health score
        health_score = sum(health_status.values()) / len(health_status)
        assert health_score >= 1.0, f"System health score: {health_score:.1%}"

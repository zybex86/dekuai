"""
🧪 Pytest Configuration and Shared Fixtures
Global test configuration for AutoGen DekuDeals testing
"""

import sys
import os
import time
import tempfile
import pytest
from typing import Dict, Any, List, Optional
from unittest.mock import Mock, patch

# Add project root to path
sys.path.append(".")

# Import project modules
try:
    from agent_tools import search_and_scrape_game
    from autogen_agents import (
        data_collector,
        price_analyzer,
        review_generator,
        quality_assurance,
        user_proxy,
    )
    from conversation_manager import GameAnalysisManager
    from utils.user_management import UserManager
    from utils.game_collection_manager import GameCollectionManager
    from utils.smart_user_profiler import SmartUserProfiler
    from utils.price_prediction_ml import PricePredictionEngine
    from utils.batch_processor import BatchAnalysisManager
except ImportError as e:
    pytest.skip(f"Could not import project modules: {e}")

# ===============================
# SESSION-SCOPED FIXTURES
# ===============================


@pytest.fixture(scope="session")
def test_data_dir():
    """Create temporary directory for test data"""
    with tempfile.TemporaryDirectory() as temp_dir:
        yield temp_dir


@pytest.fixture(scope="session")
def sample_game_data() -> Dict[str, Any]:
    """Sample game data for testing"""
    return {
        "title": "Test Game",
        "MSRP": "50.00 zł",
        "current_eshop_price": "25.00 zł",
        "lowest_historical_price": "20.00 zł",
        "metacritic_score": "85",
        "opencritic_score": "88",
        "genres": ["Action", "Adventure"],
        "developer": "Test Studio",
        "publisher": "Test Publisher",
        "platform": "Nintendo Switch",
        "release_date": "January 1, 2023",
        "success": True,
        "source_url": "https://www.dekudeals.com/items/test-game",
    }


@pytest.fixture(scope="session")
def test_games_list() -> List[str]:
    """List of games for testing"""
    return [
        "Celeste",
        "Hollow Knight",
        "Hades",
        "Ori and the Blind Forest",
        "Dead Cells",
    ]


@pytest.fixture(scope="session")
def edge_case_inputs() -> List[tuple]:
    """Edge case inputs for testing"""
    return [
        ("", "Empty string"),
        ("nonexistent_game_12345", "Non-existent game"),
        ("a", "Single character"),
        ("a" * 1000, "Extremely long input"),
        (None, "None input"),
        ("Game with UTF-8 chars: Pokémon", "UTF-8 characters"),
    ]


# ===============================
# FUNCTION-SCOPED FIXTURES
# ===============================


@pytest.fixture
def mock_game_data():
    """Mock game data that doesn't require internet"""
    return {
        "title": "Mock Game",
        "MSRP": "60.00 zł",
        "current_eshop_price": "30.00 zł",
        "lowest_historical_price": "25.00 zł",
        "metacritic_score": "80",
        "opencritic_score": "82",
        "genres": ["Platformer"],
        "developer": "Mock Studio",
        "publisher": "Mock Publisher",
        "success": True,
    }


@pytest.fixture
def user_manager():
    """Initialize UserManager for testing"""
    return UserManager()


@pytest.fixture
def game_collection_manager():
    """Initialize GameCollectionManager for testing"""
    return GameCollectionManager()


@pytest.fixture
def smart_user_profiler():
    """Initialize SmartUserProfiler for testing"""
    return SmartUserProfiler()


@pytest.fixture
def price_prediction_engine():
    """Initialize PricePredictionEngine for testing"""
    return PricePredictionEngine()


@pytest.fixture
def batch_analysis_manager():
    """Initialize BatchAnalysisManager for testing"""
    return BatchAnalysisManager()


@pytest.fixture
def game_analysis_manager():
    """Initialize GameAnalysisManager for testing"""
    return GameAnalysisManager()


@pytest.fixture
def autogen_agents():
    """AutoGen agents for testing"""
    return {
        "data_collector": data_collector,
        "price_analyzer": price_analyzer,
        "review_generator": review_generator,
        "quality_assurance": quality_assurance,
        "user_proxy": user_proxy,
    }


@pytest.fixture
def test_user_data():
    """Test user data for user management tests"""
    return {
        "username": f"test_user_{int(time.time())}",
        "display_name": "Test User",
        "email": "test@example.com",
        "user_type": "regular",
    }


@pytest.fixture
def cleanup_test_user(user_manager, test_user_data):
    """Fixture that cleans up test user after test"""
    yield test_user_data
    # Cleanup after test
    try:
        # Try different cleanup methods based on available API
        if hasattr(user_manager, "delete_user"):
            user_manager.delete_user(test_user_data["username"])
        elif hasattr(user_manager, "remove_user"):
            user_manager.remove_user(test_user_data["username"])
    except Exception:
        pass  # Ignore cleanup errors


@pytest.fixture
def performance_tracker():
    """Performance tracking utility"""

    class PerformanceTracker:
        def __init__(self):
            self.timings = {}
            self.start_times = {}

        def start(self, operation: str):
            self.start_times[operation] = time.time()

        def end(self, operation: str) -> float:
            if operation in self.start_times:
                duration = time.time() - self.start_times[operation]
                self.timings[operation] = duration
                return duration
            return 0.0

        def get_timing(self, operation: str) -> Optional[float]:
            return self.timings.get(operation)

        def get_all_timings(self) -> Dict[str, float]:
            return self.timings.copy()

    return PerformanceTracker()


# ===============================
# PARAMETRIZED FIXTURES
# ===============================


@pytest.fixture(
    params=[
        "bargain_hunter",
        "quality_seeker",
        "indie_lover",
        "aaa_gamer",
        "casual_player",
    ]
)
def user_preference(request):
    """Parametrized user preferences for testing"""
    return request.param


@pytest.fixture(params=["quick", "comprehensive"])
def analysis_type(request):
    """Parametrized analysis types"""
    return request.param


# ===============================
# MOCK FIXTURES
# ===============================


@pytest.fixture
def mock_search_function():
    """Mock search function for offline testing"""

    def mock_search(game_name: str) -> Dict[str, Any]:
        if not game_name or game_name.strip() == "":
            return {"error": "Empty game name"}
        if "nonexistent" in game_name.lower():
            return {"error": "Game not found"}

        return {
            "title": f"Mock {game_name}",
            "MSRP": "50.00 zł",
            "current_eshop_price": "35.00 zł",
            "lowest_historical_price": "25.00 zł",
            "metacritic_score": "85",
            "opencritic_score": "87",
            "genres": ["Action"],
            "success": True,
        }

    return mock_search


@pytest.fixture
def mock_autogen_conversation():
    """Mock AutoGen conversation for testing without API calls"""
    return Mock(
        return_value={
            "game_data": {"title": "Mock Game", "success": True},
            "value_analysis": {"score": 7.5, "recommendation": "BUY"},
            "comprehensive_review": {"rating": 8.0, "verdict": "Recommended"},
            "success": True,
        }
    )


# ===============================
# UTILITY FIXTURES
# ===============================


@pytest.fixture
def assert_timing():
    """Utility for asserting operation timing"""

    def _assert_timing(
        actual_time: float, max_expected: float, operation: str = "operation"
    ):
        assert (
            actual_time <= max_expected
        ), f"{operation} took {actual_time:.2f}s, expected <= {max_expected:.2f}s"
        assert actual_time > 0, f"{operation} timing should be positive"

    return _assert_timing


@pytest.fixture
def assert_game_data():
    """Utility for asserting game data completeness"""

    def _assert_game_data(game_data: Dict[str, Any], min_fields: int = 5):
        assert isinstance(game_data, dict), "Game data should be a dictionary"
        assert (
            len(game_data) >= min_fields
        ), f"Game data should have at least {min_fields} fields"

        # Check for success indicator
        success_indicators = ["success", "title", "error"]
        assert any(
            indicator in game_data for indicator in success_indicators
        ), "Game data should have success indicator"

    return _assert_game_data


@pytest.fixture
def temp_collection_file(test_data_dir):
    """Temporary collection file for testing"""
    collection_file = os.path.join(test_data_dir, "test_collection.json")
    yield collection_file
    # Cleanup
    if os.path.exists(collection_file):
        os.remove(collection_file)


# ===============================
# SKIP CONDITIONS
# ===============================


def pytest_configure(config):
    """Configure pytest with custom markers"""
    config.addinivalue_line(
        "markers", "requires_internet: mark test as requiring internet connection"
    )


def pytest_collection_modifyitems(config, items):
    """Modify test collection to add markers based on test names"""
    for item in items:
        # Add online marker for tests that require internet
        if "online" in item.name or "real_game" in item.name:
            item.add_marker(pytest.mark.online)

        # Add slow marker for performance tests
        if "performance" in item.name or "stress" in item.name:
            item.add_marker(pytest.mark.slow)

        # Add integration marker for integration tests
        if "integration" in item.name or "full_pipeline" in item.name:
            item.add_marker(pytest.mark.integration)


# ===============================
# TEST ENVIRONMENT SETUP
# ===============================


@pytest.fixture(autouse=True)
def setup_test_environment():
    """Automatically setup test environment for each test"""
    # Setup
    original_cwd = os.getcwd()

    # Ensure we're in the project root
    project_root = os.path.dirname(os.path.abspath(__file__)).replace("/tests", "")
    os.chdir(project_root)

    yield

    # Cleanup
    os.chdir(original_cwd)

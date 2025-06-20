"""
🛠️ Test Utilities
Helper functions and utilities for testing
"""

import pytest
import time
import json
import os
from typing import Dict, Any, List, Optional
from unittest.mock import Mock, patch


class TestHelpers:
    """Test helper utilities"""

    @staticmethod
    def create_mock_game_data(title: str = "Mock Game", **kwargs) -> Dict[str, Any]:
        """Create mock game data for testing"""
        default_data = {
            "title": title,
            "MSRP": "50.00 zł",
            "current_eshop_price": "35.00 zł",
            "lowest_historical_price": "25.00 zł",
            "metacritic_score": "85",
            "opencritic_score": "87",
            "genres": ["Action", "Adventure"],
            "developer": "Mock Studio",
            "publisher": "Mock Publisher",
            "platform": "Nintendo Switch",
            "release_date": "January 1, 2023",
            "success": True,
            "source_url": f'https://www.dekudeals.com/items/{title.lower().replace(" ", "-")}',
        }

        # Override with any provided kwargs
        default_data.update(kwargs)
        return default_data

    @staticmethod
    def create_mock_error_response(error_message: str = "Test error") -> Dict[str, Any]:
        """Create mock error response for testing"""
        return {"error": error_message, "success": False, "timestamp": time.time()}

    @staticmethod
    def validate_game_data_structure(game_data: Dict[str, Any]) -> bool:
        """Validate game data structure"""
        if not isinstance(game_data, dict):
            return False

        # Check for required fields
        required_fields = ["title", "success"]
        optional_fields = ["MSRP", "current_eshop_price", "metacritic_score", "error"]

        # Must have title or error
        has_title = "title" in game_data and game_data["title"]
        has_error = "error" in game_data and game_data["error"]

        if not (has_title or has_error):
            return False

        # If successful, should have title
        if game_data.get("success") and not has_title:
            return False

        return True

    @staticmethod
    def measure_function_performance(func, *args, **kwargs) -> tuple:
        """Measure function performance and return (result, duration)"""
        start_time = time.time()
        try:
            result = func(*args, **kwargs)
            duration = time.time() - start_time
            return result, duration
        except Exception as e:
            duration = time.time() - start_time
            return e, duration


class TestDataGenerators:
    """Generate test data for various scenarios"""

    @staticmethod
    def generate_game_list(count: int = 10) -> List[str]:
        """Generate list of test game names"""
        base_games = [
            "Celeste",
            "Hollow Knight",
            "Hades",
            "Ori and the Blind Forest",
            "Dead Cells",
            "Cuphead",
            "Shovel Knight",
            "Stardew Valley",
            "The Binding of Isaac",
            "Super Meat Boy",
        ]

        if count <= len(base_games):
            return base_games[:count]

        # Generate additional games if needed
        additional_games = [f"Test Game {i}" for i in range(len(base_games), count)]
        return base_games + additional_games

    @staticmethod
    def generate_edge_case_inputs() -> List[tuple]:
        """Generate edge case inputs for testing"""
        return [
            ("", "Empty string"),
            ("   ", "Whitespace only"),
            ("a", "Single character"),
            ("ab", "Two characters"),
            ("Game with UTF-8: Pokémon", "UTF-8 characters"),
            ("Game with symbols: @#$%", "Special characters"),
            ("Very " * 100 + "Long Game Name", "Very long name"),
            ("Game\nwith\nnewlines", "Newlines in name"),
            ("Game\twith\ttabs", "Tabs in name"),
            ("Game with 'quotes'", "Single quotes"),
            ('Game with "double quotes"', "Double quotes"),
            ("nonexistent_unique_game_12345", "Non-existent game"),
        ]

    @staticmethod
    def generate_performance_test_scenarios() -> List[Dict[str, Any]]:
        """Generate performance test scenarios"""
        return [
            {
                "name": "single_game",
                "games": 1,
                "max_time": 5.0,
                "description": "Single game search",
            },
            {
                "name": "small_batch",
                "games": 3,
                "max_time": 15.0,
                "description": "Small batch processing",
            },
            {
                "name": "medium_batch",
                "games": 5,
                "max_time": 30.0,
                "description": "Medium batch processing",
            },
            {
                "name": "concurrent_test",
                "games": 3,
                "max_time": 20.0,
                "description": "Concurrent processing",
                "concurrent": True,
            },
        ]


class TestValidators:
    """Validation utilities for test results"""

    @staticmethod
    def validate_performance_result(
        duration: float, max_expected: float, operation: str = "operation"
    ) -> bool:
        """Validate performance result"""
        if duration <= 0:
            raise AssertionError(f"{operation} duration should be positive: {duration}")

        if duration > max_expected:
            raise AssertionError(
                f"{operation} took {duration:.2f}s, expected <= {max_expected:.2f}s"
            )

        return True

    @staticmethod
    def validate_api_response(response: Any, expected_type: type = dict) -> bool:
        """Validate API response structure"""
        if not isinstance(response, expected_type):
            raise AssertionError(
                f"Response should be {expected_type.__name__}, got {type(response).__name__}"
            )

        if expected_type == dict:
            # For dict responses, should have some content
            if len(response) == 0:
                raise AssertionError("Response dict should not be empty")

        return True

    @staticmethod
    def validate_integration_result(
        result: Dict[str, Any], required_components: List[str]
    ) -> bool:
        """Validate integration test result"""
        if not isinstance(result, dict):
            raise AssertionError("Integration result should be dict")

        missing_components = [
            comp for comp in required_components if comp not in result
        ]
        if missing_components:
            raise AssertionError(f"Missing required components: {missing_components}")

        return True


class TestMocks:
    """Mock objects and functions for testing"""

    @staticmethod
    def create_mock_user_manager(current_user: Optional[Dict] = None):
        """Create mock UserManager"""
        mock_manager = Mock()

        if current_user is None:
            current_user = {
                "username": "test_user",
                "display_name": "Test User",
                "user_type": "regular",
            }

        mock_manager.get_current_user.return_value = current_user
        mock_manager.switch_user.return_value = True

        return mock_manager

    @staticmethod
    def create_mock_game_collection_manager():
        """Create mock GameCollectionManager"""
        mock_manager = Mock()

        mock_collection = {
            "games": [
                {"title": "Mock Game 1", "status": "owned"},
                {"title": "Mock Game 2", "status": "wishlist"},
            ],
            "total_games": 2,
        }

        mock_manager.get_user_collection.return_value = mock_collection
        mock_manager.get_user_games.return_value = mock_collection["games"]
        mock_manager.add_game.return_value = True

        return mock_manager

    @staticmethod
    def create_mock_search_function():
        """Create mock search function with realistic behavior"""

        def mock_search(game_name: str) -> Dict[str, Any]:
            # Handle edge cases
            if not game_name or game_name.strip() == "":
                return TestHelpers.create_mock_error_response("Empty game name")

            if "nonexistent" in game_name.lower():
                return TestHelpers.create_mock_error_response("Game not found")

            # Simulate processing time
            time.sleep(0.01)  # 10ms simulated processing

            return TestHelpers.create_mock_game_data(game_name)

        return mock_search


class TestReporting:
    """Test reporting and analysis utilities"""

    @staticmethod
    def generate_performance_report(
        performance_data: Dict[str, float],
    ) -> Dict[str, Any]:
        """Generate performance report from test data"""
        if not performance_data:
            return {"error": "No performance data provided"}

        total_operations = len(performance_data)
        total_time = sum(performance_data.values())
        avg_time = total_time / total_operations
        max_time = max(performance_data.values())
        min_time = min(performance_data.values())

        # Performance rating
        if avg_time < 1.0:
            rating = "Excellent"
        elif avg_time < 3.0:
            rating = "Good"
        elif avg_time < 5.0:
            rating = "Acceptable"
        else:
            rating = "Needs Improvement"

        return {
            "total_operations": total_operations,
            "total_time": total_time,
            "average_time": avg_time,
            "max_time": max_time,
            "min_time": min_time,
            "performance_rating": rating,
            "operations_per_second": total_operations / total_time,
            "details": performance_data,
        }

    @staticmethod
    def generate_test_summary(test_results: Dict[str, Any]) -> str:
        """Generate human-readable test summary"""
        total_tests = test_results.get("total_tests", 0)
        passed_tests = test_results.get("passed_tests", 0)
        failed_tests = test_results.get("failed_tests", 0)
        skipped_tests = test_results.get("skipped_tests", 0)

        success_rate = (passed_tests / total_tests * 100) if total_tests > 0 else 0

        summary = f"""
🧪 Test Summary Report
====================
Total Tests:    {total_tests}
Passed:         {passed_tests} ({success_rate:.1f}%)
Failed:         {failed_tests}
Skipped:        {skipped_tests}

Performance:    {test_results.get('performance_rating', 'Unknown')}
Duration:       {test_results.get('total_duration', 0):.2f}s
"""

        if "error_details" in test_results and test_results["error_details"]:
            summary += f"\nError Details:\n"
            for error in test_results["error_details"]:
                summary += f"  • {error}\n"

        return summary


# Pytest fixtures using the utility classes
@pytest.fixture
def test_helpers():
    """Provide TestHelpers instance"""
    return TestHelpers()


@pytest.fixture
def test_data_generators():
    """Provide TestDataGenerators instance"""
    return TestDataGenerators()


@pytest.fixture
def test_validators():
    """Provide TestValidators instance"""
    return TestValidators()


@pytest.fixture
def test_mocks():
    """Provide TestMocks instance"""
    return TestMocks()


@pytest.fixture
def mock_user_manager(test_mocks):
    """Provide mock UserManager"""
    return test_mocks.create_mock_user_manager()


@pytest.fixture
def mock_collection_manager(test_mocks):
    """Provide mock GameCollectionManager"""
    return test_mocks.create_mock_game_collection_manager()


@pytest.fixture
def performance_data_collector():
    """Provide performance data collector"""

    class PerformanceCollector:
        def __init__(self):
            self.data = {}

        def record(self, operation: str, duration: float):
            self.data[operation] = duration

        def get_report(self):
            return TestReporting.generate_performance_report(self.data)

    return PerformanceCollector()


# Test the utilities themselves
class TestTestUtilities:
    """Test the test utility functions"""

    @pytest.mark.unit
    def test_mock_game_data_creation(self, test_helpers):
        """Test mock game data creation"""
        mock_data = test_helpers.create_mock_game_data("Test Game")

        assert isinstance(mock_data, dict)
        assert mock_data["title"] == "Test Game"
        assert mock_data["success"] is True
        assert "MSRP" in mock_data

        # Test with custom data
        custom_data = test_helpers.create_mock_game_data(
            "Custom Game", metacritic_score="95"
        )
        assert custom_data["title"] == "Custom Game"
        assert custom_data["metacritic_score"] == "95"

    @pytest.mark.unit
    def test_game_data_validation(self, test_helpers):
        """Test game data validation"""
        # Valid data
        valid_data = {"title": "Test Game", "success": True}
        assert test_helpers.validate_game_data_structure(valid_data)

        # Valid error response
        error_data = {"error": "Not found", "success": False}
        assert test_helpers.validate_game_data_structure(error_data)

        # Invalid data
        invalid_data = {"success": True}  # No title or error
        assert not test_helpers.validate_game_data_structure(invalid_data)

    @pytest.mark.unit
    def test_performance_measurement(self, test_helpers):
        """Test performance measurement utility"""

        def test_function(delay: float):
            time.sleep(delay)
            return "completed"

        result, duration = test_helpers.measure_function_performance(test_function, 0.1)

        assert result == "completed"
        assert 0.08 <= duration <= 0.15  # Some tolerance for timing

    @pytest.mark.unit
    def test_edge_case_generation(self, test_data_generators):
        """Test edge case input generation"""
        edge_cases = test_data_generators.generate_edge_case_inputs()

        assert isinstance(edge_cases, list)
        assert len(edge_cases) > 5

        # Check structure
        for case in edge_cases:
            assert isinstance(case, tuple)
            assert len(case) == 2  # (input, description)
            assert isinstance(case[1], str)  # Description should be string

    @pytest.mark.unit
    def test_performance_reporting(self, performance_data_collector):
        """Test performance reporting"""
        # Record some test data
        performance_data_collector.record("operation_1", 1.5)
        performance_data_collector.record("operation_2", 0.8)
        performance_data_collector.record("operation_3", 2.1)

        report = performance_data_collector.get_report()

        assert isinstance(report, dict)
        assert report["total_operations"] == 3
        assert report["average_time"] == pytest.approx((1.5 + 0.8 + 2.1) / 3, rel=0.01)
        assert report["performance_rating"] in [
            "Excellent",
            "Good",
            "Acceptable",
            "Needs Improvement",
        ]

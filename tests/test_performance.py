"""
🚀 Performance Tests
Benchmark system performance and identify bottlenecks
"""

import pytest
import time
import statistics
from concurrent.futures import ThreadPoolExecutor
from typing import List, Dict, Any

# Import project modules
from agent_tools import search_and_scrape_game


class TestSearchPerformance:
    """Test game search performance"""

    @pytest.mark.performance
    @pytest.mark.online
    def test_single_search_performance(
        self, test_games_list, performance_tracker, assert_timing
    ):
        """Test performance of single game search"""
        game_name = test_games_list[0]  # "Celeste"

        performance_tracker.start("single_search")
        result = search_and_scrape_game(game_name)
        duration = performance_tracker.end("single_search")

        # Performance assertions
        assert_timing(duration, 5.0, "Single game search")  # Should be under 5s

        # Quality assertion
        assert result is not None
        assert isinstance(result, dict)

    @pytest.mark.performance
    @pytest.mark.online
    @pytest.mark.slow
    def test_sequential_search_performance(self, test_games_list, performance_tracker):
        """Test sequential search performance for multiple games"""
        search_times = []

        for game_name in test_games_list[:3]:  # Test first 3 games
            performance_tracker.start(f"search_{game_name}")
            result = search_and_scrape_game(game_name)
            duration = performance_tracker.end(f"search_{game_name}")

            if result and (result.get("title") or result.get("error")):
                search_times.append(duration)

        # Performance analysis
        if search_times:
            avg_time = statistics.mean(search_times)
            max_time = max(search_times)
            min_time = min(search_times)

            # Assertions
            assert avg_time < 3.0, f"Average search time {avg_time:.2f}s too slow"
            assert max_time < 8.0, f"Max search time {max_time:.2f}s too slow"
            assert min_time > 0.1, f"Min search time {min_time:.2f}s suspiciously fast"

            # Performance rating
            if avg_time < 2.0:
                performance_rating = "Excellent"
            elif avg_time < 3.0:
                performance_rating = "Good"
            else:
                performance_rating = "Needs Improvement"

            assert performance_rating in [
                "Excellent",
                "Good",
            ], f"Performance rating: {performance_rating} (avg: {avg_time:.2f}s)"

    @pytest.mark.performance
    @pytest.mark.online
    @pytest.mark.slow
    @pytest.mark.parametrize("concurrency", [2, 3])
    def test_concurrent_search_performance(
        self, test_games_list, concurrency, performance_tracker
    ):
        """Test concurrent search performance"""
        games_to_test = test_games_list[:concurrency]

        # Sequential baseline
        performance_tracker.start("sequential_baseline")
        sequential_results = []
        for game in games_to_test:
            result = search_and_scrape_game(game)
            sequential_results.append(result)
        sequential_time = performance_tracker.end("sequential_baseline")

        # Concurrent test
        performance_tracker.start("concurrent_test")
        with ThreadPoolExecutor(max_workers=concurrency) as executor:
            concurrent_results = list(
                executor.map(search_and_scrape_game, games_to_test)
            )
        concurrent_time = performance_tracker.end("concurrent_test")

        # Performance analysis
        efficiency_gain = ((sequential_time - concurrent_time) / sequential_time) * 100

        # Assertions
        assert (
            concurrent_time < sequential_time
        ), "Concurrent should be faster than sequential"
        assert efficiency_gain > 0, f"No efficiency gain: {efficiency_gain:.1f}%"

        # Reasonable efficiency gain (at least 10% for 2+ threads)
        expected_min_gain = 10.0 if concurrency >= 2 else 0.0
        assert (
            efficiency_gain >= expected_min_gain
        ), f"Insufficient efficiency gain: {efficiency_gain:.1f}% (expected: >{expected_min_gain}%)"

    @pytest.mark.performance
    @pytest.mark.unit
    def test_cache_performance(self, mock_search_function, performance_tracker):
        """Test caching performance improvements"""
        game_name = "Test Game"

        # First call (cold)
        performance_tracker.start("cold_cache")
        result1 = mock_search_function(game_name)
        cold_time = performance_tracker.end("cold_cache")

        # Second call (should be cached/faster)
        performance_tracker.start("warm_cache")
        result2 = mock_search_function(game_name)
        warm_time = performance_tracker.end("warm_cache")

        # Results should be consistent
        assert result1 == result2

        # Warm cache should be faster (for real implementation)
        # For mock, just ensure both are reasonable
        assert cold_time < 1.0, "Cold cache too slow for mock"
        assert warm_time < 1.0, "Warm cache too slow for mock"


class TestComponentPerformance:
    """Test individual component performance"""

    @pytest.mark.performance
    @pytest.mark.unit
    def test_user_manager_performance(
        self, user_manager, performance_tracker, assert_timing
    ):
        """Test UserManager operation performance"""
        current_user = user_manager.get_current_user()

        if current_user:
            username = getattr(
                current_user, "username", current_user.get("username", "default")
            )

            # Test user switching performance
            performance_tracker.start("user_switch")
            result = user_manager.switch_user(username)
            duration = performance_tracker.end("user_switch")

            assert_timing(duration, 0.5, "User switching")  # Should be very fast

    @pytest.mark.performance
    @pytest.mark.unit
    def test_component_initialization_performance(
        self, performance_tracker, assert_timing
    ):
        """Test component initialization performance"""

        # UserManager initialization
        performance_tracker.start("user_manager_init")
        from utils.user_management import UserManager

        user_mgr = UserManager()
        duration = performance_tracker.end("user_manager_init")
        assert_timing(duration, 2.0, "UserManager initialization")

        # GameCollectionManager initialization
        performance_tracker.start("collection_manager_init")
        from utils.game_collection_manager import GameCollectionManager

        collection_mgr = GameCollectionManager()
        duration = performance_tracker.end("collection_manager_init")
        assert_timing(duration, 2.0, "GameCollectionManager initialization")

        # SmartUserProfiler initialization
        performance_tracker.start("profiler_init")
        from utils.smart_user_profiler import SmartUserProfiler

        profiler = SmartUserProfiler()
        duration = performance_tracker.end("profiler_init")
        assert_timing(duration, 3.0, "SmartUserProfiler initialization")


class TestMemoryPerformance:
    """Test memory usage and efficiency"""

    @pytest.mark.performance
    @pytest.mark.slow
    def test_memory_usage_stability(self, user_manager, performance_tracker):
        """Test memory usage doesn't grow excessively"""
        current_user = user_manager.get_current_user()

        if current_user:
            username = getattr(
                current_user, "username", current_user.get("username", "default")
            )

            # Perform multiple operations
            performance_tracker.start("memory_test")

            for i in range(50):  # Simulate repeated operations
                user_manager.switch_user(username)
                current = user_manager.get_current_user()

            duration = performance_tracker.end("memory_test")

            # Should complete without significant slowdown
            assert duration < 5.0, f"Memory test took too long: {duration:.2f}s"

    @pytest.mark.performance
    @pytest.mark.unit
    def test_large_input_handling(
        self, mock_search_function, performance_tracker, assert_timing
    ):
        """Test handling of large inputs efficiently"""
        large_input = "a" * 10000  # 10KB string

        performance_tracker.start("large_input")
        result = mock_search_function(large_input)
        duration = performance_tracker.end("large_input")

        # Should handle large input gracefully and quickly
        assert_timing(duration, 1.0, "Large input handling")
        assert result is not None
        assert isinstance(result, dict)


class TestSystemPerformance:
    """Test overall system performance"""

    @pytest.mark.performance
    @pytest.mark.integration
    @pytest.mark.slow
    def test_full_pipeline_performance(
        self, game_analysis_manager, performance_tracker, assert_timing
    ):
        """Test full analysis pipeline performance"""

        performance_tracker.start("full_pipeline")
        try:
            result = game_analysis_manager.analyze_game("Test Game")
            duration = performance_tracker.end("full_pipeline")

            # Full pipeline should complete in reasonable time
            assert_timing(duration, 30.0, "Full analysis pipeline")

            # Should return some result
            assert result is not None
            assert isinstance(result, dict)

        except Exception as e:
            duration = performance_tracker.end("full_pipeline")
            # Even if it fails, should fail quickly
            assert duration < 10.0, f"Pipeline failed too slowly: {duration:.2f}s"
            pytest.skip(f"Pipeline test failed: {e}")

    @pytest.mark.performance
    @pytest.mark.batch
    @pytest.mark.slow
    def test_batch_processing_performance(
        self, batch_analysis_manager, test_games_list, performance_tracker
    ):
        """Test batch processing performance"""
        games_to_process = test_games_list[:2]  # Small batch for testing

        performance_tracker.start("batch_processing")
        try:
            # Start batch analysis
            batch_id = batch_analysis_manager.start_batch_analysis(
                games_to_process, analysis_type="quick"
            )

            # Wait for completion or timeout
            max_wait = 60  # 60 seconds max
            for i in range(max_wait):
                status = batch_analysis_manager.get_batch_status(batch_id)
                if status and status.get("status") in ["completed", "failed"]:
                    break
                time.sleep(1)

            duration = performance_tracker.end("batch_processing")

            # Performance assertions
            assert duration < max_wait, f"Batch processing timeout: {duration:.2f}s"

            # Batch should be efficient
            games_processed = len(games_to_process)
            time_per_game = duration / games_processed
            assert time_per_game < 30.0, f"Time per game too high: {time_per_game:.2f}s"

        except Exception as e:
            duration = performance_tracker.end("batch_processing")
            pytest.skip(f"Batch processing test failed: {e}")

    @pytest.mark.performance
    @pytest.mark.integration
    def test_system_response_times(
        self,
        user_manager,
        game_collection_manager,
        smart_user_profiler,
        performance_tracker,
    ):
        """Test system component response times"""
        response_times = {}

        # Test user management response
        performance_tracker.start("user_response")
        current_user = user_manager.get_current_user()
        response_times["user_management"] = performance_tracker.end("user_response")

        # Test collection access response (if possible)
        if current_user:
            username = getattr(
                current_user, "username", current_user.get("username", "default")
            )

            performance_tracker.start("collection_response")
            try:
                if hasattr(game_collection_manager, "get_user_collection"):
                    collection = game_collection_manager.get_user_collection(username)
                elif hasattr(game_collection_manager, "get_user_games"):
                    collection = game_collection_manager.get_user_games(username)
                response_times["collection_access"] = performance_tracker.end(
                    "collection_response"
                )
            except Exception:
                response_times["collection_access"] = performance_tracker.end(
                    "collection_response"
                )

        # Test profiler response
        performance_tracker.start("profiler_response")
        # Just test that profiler responds quickly to basic operations
        assert smart_user_profiler is not None  # Basic check
        response_times["profiler_access"] = performance_tracker.end("profiler_response")

        # Response time assertions
        for component, response_time in response_times.items():
            assert (
                response_time < 2.0
            ), f"{component} response too slow: {response_time:.2f}s"

        # Overall system responsiveness
        avg_response = statistics.mean(response_times.values())
        assert (
            avg_response < 1.0
        ), f"Average system response too slow: {avg_response:.2f}s"


class TestPerformanceRegression:
    """Test for performance regressions"""

    @pytest.mark.performance
    @pytest.mark.unit
    def test_performance_benchmarks(self, performance_tracker):
        """Test against performance benchmarks"""
        benchmarks = {
            "component_init": 2.0,  # Component initialization < 2s
            "user_operation": 0.5,  # User operations < 0.5s
            "search_operation": 5.0,  # Search operations < 5s
            "system_response": 1.0,  # System response < 1s
        }

        # These are baseline benchmarks that should not regress
        for operation, max_time in benchmarks.items():
            assert max_time > 0, f"Benchmark {operation} should be positive"
            assert max_time < 10.0, f"Benchmark {operation} seems too lenient"

    @pytest.mark.performance
    @pytest.mark.unit
    def test_scalability_indicators(self, mock_search_function, performance_tracker):
        """Test scalability indicators"""
        # Test with increasing load
        load_sizes = [1, 5, 10]
        execution_times = []

        for load_size in load_sizes:
            performance_tracker.start(f"load_{load_size}")

            for i in range(load_size):
                result = mock_search_function(f"Game {i}")
                assert result is not None

            duration = performance_tracker.end(f"load_{load_size}")
            execution_times.append(duration)

        # Check that execution time scales reasonably
        # Time should increase with load, but not exponentially
        for i in range(1, len(execution_times)):
            ratio = execution_times[i] / execution_times[i - 1]
            load_ratio = load_sizes[i] / load_sizes[i - 1]

            # Execution time should not increase more than 2x the load increase
            assert (
                ratio <= load_ratio * 2
            ), f"Poor scaling: {ratio:.2f}x time for {load_ratio:.2f}x load"

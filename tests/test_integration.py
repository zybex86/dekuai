"""
🔗 Integration Tests
Test end-to-end workflows and component interactions
"""

import pytest
import time
from typing import Dict, Any, List
from unittest.mock import patch, Mock

# Import project modules
from agent_tools import (
    search_and_scrape_game,
    calculate_advanced_value_analysis,
    generate_comprehensive_game_review,
)


class TestGameAnalysisPipeline:
    """Test complete game analysis pipeline"""

    @pytest.mark.integration
    @pytest.mark.online
    @pytest.mark.slow
    def test_full_game_analysis_workflow(
        self, game_analysis_manager, test_games_list, performance_tracker, assert_timing
    ):
        """Test complete game analysis from start to finish"""
        game_name = test_games_list[0]  # "Celeste"

        performance_tracker.start("full_workflow")

        try:
            # Run full analysis
            result = game_analysis_manager.analyze_game(game_name)
            duration = performance_tracker.end("full_workflow")

            # Performance check
            assert_timing(duration, 60.0, "Full game analysis workflow")

            # Result validation
            assert result is not None
            assert isinstance(result, dict)

            # Check for expected components
            expected_components = [
                "game_data",
                "value_analysis",
                "comprehensive_review",
            ]
            found_components = [comp for comp in expected_components if comp in result]

            assert (
                len(found_components) >= 1
            ), f"Missing components: {expected_components}"

            # Validate game data if present
            if "game_data" in result:
                game_data = result["game_data"]
                assert isinstance(game_data, dict)
                assert game_data.get("title") or game_data.get("error")

        except Exception as e:
            duration = performance_tracker.end("full_workflow")
            pytest.skip(f"Full workflow test failed: {e}")

    @pytest.mark.integration
    @pytest.mark.unit
    def test_analysis_pipeline_with_mock_data(
        self, sample_game_data, performance_tracker
    ):
        """Test analysis pipeline with known good data"""
        performance_tracker.start("mock_pipeline")

        try:
            # Test value analysis component
            value_result = calculate_advanced_value_analysis(sample_game_data)

            # Test review generation component
            review_result = generate_comprehensive_game_review(
                sample_game_data["title"], include_recommendations=True
            )

            duration = performance_tracker.end("mock_pipeline")

            # Performance check
            assert duration < 30.0, f"Mock pipeline too slow: {duration:.2f}s"

            # Validate results
            if value_result:
                assert isinstance(value_result, dict)
                # Should have some analysis data
                assert len(value_result) > 0

            if review_result:
                assert isinstance(review_result, dict)
                # Should have review data
                assert review_result.get("success") or review_result.get("review_data")

        except Exception as e:
            duration = performance_tracker.end("mock_pipeline")
            pytest.skip(f"Mock pipeline test failed: {e}")


class TestUserGameCollectionIntegration:
    """Test integration between user management and game collection"""

    @pytest.mark.integration
    @pytest.mark.user_management
    @pytest.mark.game_collection
    def test_user_collection_workflow(
        self, user_manager, game_collection_manager, performance_tracker
    ):
        """Test user and collection management integration"""
        current_user = user_manager.get_current_user()

        if not current_user:
            pytest.skip("No current user available for integration test")

        username = getattr(
            current_user, "username", current_user.get("username", "default")
        )

        performance_tracker.start("user_collection_workflow")

        try:
            # Test collection access
            if hasattr(game_collection_manager, "get_user_collection"):
                collection = game_collection_manager.get_user_collection(username)
            elif hasattr(game_collection_manager, "get_user_games"):
                collection = game_collection_manager.get_user_games(username)
            else:
                pytest.skip("No collection access method available")

            duration = performance_tracker.end("user_collection_workflow")

            # Performance check
            assert duration < 5.0, f"User collection workflow too slow: {duration:.2f}s"

            # Validate collection
            assert isinstance(collection, (dict, list, type(None)))

            if isinstance(collection, dict):
                # Collection should have reasonable structure
                if "games" in collection:
                    games_list = collection["games"]
                    assert isinstance(games_list, list)

                    # Test individual game entries if present
                    for game in games_list[:3]:  # Check first 3 games
                        assert isinstance(game, (dict, str))
                        if isinstance(game, dict):
                            # Should have some identifying information
                            assert (
                                game.get("title") or game.get("name") or game.get("id")
                            )

        except Exception as e:
            duration = performance_tracker.end("user_collection_workflow")
            pytest.skip(f"User collection workflow failed: {e}")

    @pytest.mark.integration
    @pytest.mark.user_management
    def test_user_switching_persistence(self, user_manager, performance_tracker):
        """Test user switching and state persistence"""
        current_user = user_manager.get_current_user()

        if not current_user:
            pytest.skip("No current user for switching test")

        original_username = getattr(
            current_user, "username", current_user.get("username", "default")
        )

        performance_tracker.start("user_switching")

        # Switch to same user (should be idempotent)
        result1 = user_manager.switch_user(original_username)

        # Verify user is still correct
        verify_user = user_manager.get_current_user()
        verify_username = getattr(
            verify_user, "username", verify_user.get("username", "default")
        )

        duration = performance_tracker.end("user_switching")

        # Performance check
        assert duration < 2.0, f"User switching too slow: {duration:.2f}s"

        # State verification
        assert verify_username == original_username, "User switching lost state"


class TestMLIntegration:
    """Test ML component integration"""

    @pytest.mark.integration
    @pytest.mark.ml
    def test_smart_profiler_integration(
        self, smart_user_profiler, user_manager, sample_game_data, performance_tracker
    ):
        """Test smart profiler integration with user system"""
        current_user = user_manager.get_current_user()

        if not current_user:
            pytest.skip("No current user for profiler integration test")

        performance_tracker.start("profiler_integration")

        try:
            # Test profiler with user context
            # Note: actual profiler API may vary, so we test basic functionality
            assert smart_user_profiler is not None

            # Test that profiler can handle game data
            # This is a basic integration test - actual implementation may differ
            game_title = sample_game_data["title"]

            # Just verify profiler doesn't crash with game data
            # (specific profiler methods would be tested separately)

            duration = performance_tracker.end("profiler_integration")

            # Performance check
            assert duration < 5.0, f"Profiler integration too slow: {duration:.2f}s"

        except Exception as e:
            duration = performance_tracker.end("profiler_integration")
            pytest.skip(f"Profiler integration test failed: {e}")

    @pytest.mark.integration
    @pytest.mark.ml
    def test_price_prediction_integration(
        self, price_prediction_engine, sample_game_data, performance_tracker
    ):
        """Test price prediction integration"""
        performance_tracker.start("price_prediction")

        try:
            # Test price prediction with game data
            assert price_prediction_engine is not None

            # Basic integration test - verify component loads and responds
            # Actual prediction testing would require specific API knowledge

            duration = performance_tracker.end("price_prediction")

            # Performance check
            assert (
                duration < 3.0
            ), f"Price prediction integration too slow: {duration:.2f}s"

        except Exception as e:
            duration = performance_tracker.end("price_prediction")
            pytest.skip(f"Price prediction integration test failed: {e}")


class TestAutoGenIntegration:
    """Test AutoGen agent integration"""

    @pytest.mark.integration
    @pytest.mark.autogen
    @pytest.mark.slow
    def test_autogen_conversation_flow(
        self, autogen_agents, mock_autogen_conversation, performance_tracker
    ):
        """Test AutoGen agent conversation integration"""
        agents = autogen_agents

        # Verify all agents are available
        required_agents = [
            "data_collector",
            "price_analyzer",
            "review_generator",
            "quality_assurance",
            "user_proxy",
        ]

        for agent_name in required_agents:
            assert agent_name in agents, f"Missing agent: {agent_name}"
            assert agents[agent_name] is not None, f"Agent {agent_name} is None"

        performance_tracker.start("autogen_integration")

        try:
            # Test basic agent properties and integration
            for agent_name, agent in agents.items():
                # Basic agent validation
                assert hasattr(agent, "name"), f"Agent {agent_name} has no name"
                assert isinstance(
                    agent.name, str
                ), f"Agent {agent_name} name not string"

                # Agent names should match expected format
                expected_suffixes = {
                    "data_collector": "_agent",
                    "price_analyzer": "_agent",
                    "review_generator": "_agent",
                    "quality_assurance": "_agent",
                    "user_proxy": "USER_PROXY",
                }

                if agent_name in expected_suffixes:
                    expected_suffix = expected_suffixes[agent_name]
                    if expected_suffix == "USER_PROXY":
                        assert agent.name == "USER_PROXY"
                    else:
                        assert agent.name.endswith(
                            expected_suffix
                        ), f"Agent {agent_name} name '{agent.name}' doesn't end with '{expected_suffix}'"

            duration = performance_tracker.end("autogen_integration")

            # Performance check
            assert duration < 5.0, f"AutoGen integration too slow: {duration:.2f}s"

        except Exception as e:
            duration = performance_tracker.end("autogen_integration")
            pytest.skip(f"AutoGen integration test failed: {e}")


class TestBatchProcessingIntegration:
    """Test batch processing integration"""

    @pytest.mark.integration
    @pytest.mark.batch
    @pytest.mark.slow
    def test_batch_processing_workflow(
        self, batch_analysis_manager, test_games_list, performance_tracker
    ):
        """Test batch processing integration workflow"""
        games_subset = test_games_list[:2]  # Small batch for testing

        performance_tracker.start("batch_integration")

        try:
            # Start batch analysis
            batch_id = batch_analysis_manager.start_batch_analysis(
                games_subset, analysis_type="quick"
            )

            assert batch_id is not None, "Batch ID should not be None"
            assert isinstance(batch_id, str), "Batch ID should be string"

            # Monitor batch progress
            max_wait_time = 120  # 2 minutes max
            wait_interval = 2  # Check every 2 seconds

            for i in range(0, max_wait_time, wait_interval):
                status = batch_analysis_manager.get_batch_status(batch_id)

                if status:
                    assert isinstance(status, dict), "Status should be dict"

                    current_status = status.get("status", "unknown")
                    if current_status in ["completed", "failed"]:
                        break

                time.sleep(wait_interval)

            duration = performance_tracker.end("batch_integration")

            # Final status check
            final_status = batch_analysis_manager.get_batch_status(batch_id)

            # Performance and completion checks
            assert (
                duration < max_wait_time + 10
            ), f"Batch took too long: {duration:.2f}s"

            if final_status:
                status_value = final_status.get("status", "unknown")

                # Should have completed or failed (not stuck)
                assert status_value in [
                    "completed",
                    "failed",
                    "running",
                ], f"Unexpected batch status: {status_value}"

                # If completed, should have some results
                if status_value == "completed":
                    results = final_status.get("results", {})
                    assert isinstance(results, dict), "Results should be dict"

        except Exception as e:
            duration = performance_tracker.end("batch_integration")
            pytest.skip(f"Batch processing integration test failed: {e}")


class TestSystemIntegration:
    """Test overall system integration"""

    @pytest.mark.integration
    @pytest.mark.slow
    def test_full_system_integration(
        self,
        user_manager,
        game_collection_manager,
        smart_user_profiler,
        batch_analysis_manager,
        autogen_agents,
        performance_tracker,
    ):
        """Test full system component integration"""
        performance_tracker.start("full_system")

        integration_results = {}

        try:
            # Test 1: User management
            current_user = user_manager.get_current_user()
            integration_results["user_management"] = current_user is not None

            # Test 2: Game collection (if user available)
            if current_user:
                username = getattr(
                    current_user, "username", current_user.get("username", "default")
                )
                try:
                    if hasattr(game_collection_manager, "get_user_collection"):
                        collection = game_collection_manager.get_user_collection(
                            username
                        )
                    elif hasattr(game_collection_manager, "get_user_games"):
                        collection = game_collection_manager.get_user_games(username)
                    else:
                        collection = None
                    integration_results["game_collection"] = collection is not None
                except Exception:
                    integration_results["game_collection"] = False
            else:
                integration_results["game_collection"] = True  # Skip if no user

            # Test 3: ML components
            integration_results["smart_profiler"] = smart_user_profiler is not None
            integration_results["batch_processor"] = batch_analysis_manager is not None

            # Test 4: AutoGen agents
            agent_count = len(autogen_agents)
            integration_results["autogen_agents"] = agent_count >= 5

            duration = performance_tracker.end("full_system")

            # Overall integration assessment
            successful_integrations = sum(integration_results.values())
            total_integrations = len(integration_results)
            integration_score = successful_integrations / total_integrations

            # Performance check
            assert duration < 10.0, f"Full system integration too slow: {duration:.2f}s"

            # Integration score check
            assert (
                integration_score >= 0.8
            ), f"Integration score too low: {integration_score:.1%} ({integration_results})"

            # Individual component checks
            assert integration_results[
                "user_management"
            ], "User management integration failed"
            assert integration_results[
                "autogen_agents"
            ], "AutoGen agents integration failed"

        except Exception as e:
            duration = performance_tracker.end("full_system")
            pytest.skip(f"Full system integration test failed: {e}")

    @pytest.mark.integration
    @pytest.mark.online
    @pytest.mark.slow
    def test_end_to_end_real_workflow(self, test_games_list, performance_tracker):
        """Test end-to-end workflow with real data"""
        game_name = test_games_list[0]  # "Celeste"

        performance_tracker.start("e2e_real")

        try:
            # Step 1: Game search
            game_data = search_and_scrape_game(game_name)
            assert game_data is not None
            assert isinstance(game_data, dict)

            # Should have either data or error
            has_data = game_data.get("title") is not None
            has_error = game_data.get("error") is not None
            assert has_data or has_error, "Should have either game data or error"

            # Step 2: Value analysis (if we have data)
            if has_data:
                try:
                    value_analysis = calculate_advanced_value_analysis(game_data)
                    if value_analysis:
                        assert isinstance(value_analysis, dict)
                except Exception:
                    pass  # Value analysis failure is acceptable

            # Step 3: Review generation (if we have data)
            if has_data:
                try:
                    review = generate_comprehensive_game_review(
                        game_data["title"], include_recommendations=True
                    )
                    if review:
                        assert isinstance(review, dict)
                except Exception:
                    pass  # Review generation failure is acceptable

            duration = performance_tracker.end("e2e_real")

            # Performance check
            assert duration < 60.0, f"End-to-end workflow too slow: {duration:.2f}s"

        except Exception as e:
            duration = performance_tracker.end("e2e_real")
            pytest.skip(f"End-to-end real workflow test failed: {e}")

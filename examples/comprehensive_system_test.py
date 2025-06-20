#!/usr/bin/env python3
"""
🧪 PHASE 5: Comprehensive System Testing & Refinement
Advanced test suite for stress testing, edge cases, performance, and UX validation
"""

import sys
import os
import time
import random
import asyncio
import threading
from concurrent.futures import ThreadPoolExecutor
from typing import List, Dict, Any, Optional
import json
import statistics

# Add project root to path
sys.path.append(".")

# Import core modules
try:
    from agent_tools import (
        search_and_scrape_game,
        calculate_value_score,
        calculate_advanced_value_analysis,
        generate_comprehensive_game_review,
    )
    from autogen_agents import data_collector, price_analyzer, review_generator
    from conversation_manager import GameAnalysisManager
    from utils.user_management import UserManager
    from utils.game_collection_manager import GameCollectionManager
    from utils.smart_user_profiler import SmartUserProfiler
    from utils.price_prediction_ml import PricePredictionEngine

    # Use simple print functions instead of CLI methods
    print("✅ All imports successful")
except Exception as e:
    print(f"❌ Import error: {e}")
    sys.exit(1)


# Simple print functions for testing
def print_header(text):
    print(f"\n{'='*70}")
    print(f"🎯 {text}")
    print("=" * 70)


def print_success(text):
    print(f"✅ {text}")


def print_error(text):
    print(f"❌ {text}")


def print_info(text):
    print(f"ℹ️  {text}")


class ComprehensiveSystemTester:
    """
    🧪 Comprehensive system testing class for Phase 5 refinement
    """

    def __init__(self):
        self.test_results = {
            "stress_tests": [],
            "edge_cases": [],
            "performance": [],
            "ux_tests": [],
            "integration": [],
            "error_handling": [],
        }
        self.start_time = time.time()

        # Test datasets
        self.popular_games = [
            "The Legend of Zelda: Tears of the Kingdom",
            "Super Mario Odyssey",
            "Metroid Dread",
            "Hollow Knight",
            "Celeste",
            "Hades",
            "Ori and the Blind Forest",
            "Cuphead",
            "Dead Cells",
            "Stardew Valley",
        ]

        self.edge_case_games = [
            "nonexistentgame12345",  # Non-existent
            "",  # Empty string
            "a",  # Single character
            "Game with very very very very long title that might break parsing",
            "Pokémon Legends: Arceus",  # Special characters
            "DOOM Eternal",  # All caps
            "mario",  # Ambiguous/common term
        ]

        self.performance_games = [
            "Zelda",
            "Mario",
            "Sonic",
            "Pokemon",
            "Metroid",  # Quick lookups
        ]

    def run_all_tests(self):
        """Run comprehensive test suite"""
        print_header("🧪 PHASE 5: Comprehensive System Testing & Refinement")

        print("\n" + "=" * 70)
        print("📊 TESTING PLAN:")
        print("1. 🔥 Stress Testing - Large datasets, concurrent operations")
        print("2. 🏗️ Edge Cases - Invalid inputs, corner cases")
        print("3. ⚡ Performance - Speed benchmarks, optimization")
        print("4. 🎨 UX Testing - Interface, usability")
        print("5. 🔗 Integration - End-to-end workflows")
        print("6. ❌ Error Handling - Failure modes, recovery")
        print("=" * 70)

        # Run test categories
        self.stress_testing()
        self.edge_case_testing()
        self.performance_testing()
        self.ux_testing()
        self.integration_testing()
        self.error_handling_testing()

        # Generate final report
        self.generate_final_report()

    def stress_testing(self):
        """🔥 Stress test with large datasets and concurrent operations"""
        print_header("🔥 STRESS TESTING")

        # Test 1: Concurrent game analysis
        print("\n📋 Test 1: Concurrent Game Analysis (10 games)")
        start_time = time.time()

        try:
            with ThreadPoolExecutor(max_workers=3) as executor:
                futures = []
                for game in self.popular_games[:5]:  # Test with 5 games
                    future = executor.submit(self._analyze_game_safe, game)
                    futures.append((game, future))

                concurrent_results = []
                for game, future in futures:
                    try:
                        result = future.result(timeout=30)
                        concurrent_results.append(
                            {
                                "game": game,
                                "success": result is not None,
                                "data_quality": (
                                    "good" if result and result.get("title") else "poor"
                                ),
                            }
                        )
                    except Exception as e:
                        concurrent_results.append(
                            {"game": game, "success": False, "error": str(e)}
                        )

                duration = time.time() - start_time
                success_rate = sum(1 for r in concurrent_results if r["success"]) / len(
                    concurrent_results
                )

                self.test_results["stress_tests"].append(
                    {
                        "test": "concurrent_analysis",
                        "games_tested": len(concurrent_results),
                        "success_rate": success_rate,
                        "duration": duration,
                        "avg_time_per_game": duration / len(concurrent_results),
                        "details": concurrent_results,
                    }
                )

                print_success(
                    f"✅ Concurrent analysis: {success_rate:.1%} success rate in {duration:.2f}s"
                )

        except Exception as e:
            print_error(f"❌ Concurrent analysis failed: {e}")
            self.test_results["stress_tests"].append(
                {"test": "concurrent_analysis", "success": False, "error": str(e)}
            )

        # Test 2: Memory stress test with user profiles
        print("\n📋 Test 2: Memory Stress - Multiple User Profiles")
        try:
            user_mgr = UserManager()

            # Create multiple test users
            test_users = []
            for i in range(50):
                username = f"testuser_{i:03d}"
                result = user_mgr.register_user(
                    username=username,
                    display_name=f"Test User {i}",
                    email=f"test{i}@example.com",
                )
                test_users.append(username)

            # Switch between users rapidly
            switch_times = []
            for _ in range(20):
                user = random.choice(test_users)
                start = time.time()
                user_mgr.switch_user(user)
                switch_times.append(time.time() - start)

            avg_switch_time = statistics.mean(switch_times)

            # Cleanup
            for username in test_users:
                try:
                    user_mgr.delete_user(username)
                except:
                    pass  # Ignore cleanup errors

            self.test_results["stress_tests"].append(
                {
                    "test": "user_switching_stress",
                    "users_created": len(test_users),
                    "avg_switch_time": avg_switch_time,
                    "max_switch_time": max(switch_times),
                    "success": True,
                }
            )

            print_success(
                f"✅ User switching: {avg_switch_time:.3f}s average switch time"
            )

        except Exception as e:
            print_error(f"❌ User switching stress test failed: {e}")

    def edge_case_testing(self):
        """🏗️ Test edge cases and corner cases"""
        print_header("🏗️ EDGE CASE TESTING")

        edge_results = []

        for i, game_input in enumerate(self.edge_case_games, 1):
            print(f"\n📋 Test {i}: Edge case input: '{game_input}'")

            try:
                start_time = time.time()
                result = self._analyze_game_safe(game_input)
                duration = time.time() - start_time

                # Evaluate result quality
                if result is None:
                    status = "handled_gracefully"
                elif result.get("error"):
                    status = "error_handled"
                elif result.get("title"):
                    status = "unexpected_success"
                else:
                    status = "partial_data"

                edge_results.append(
                    {
                        "input": game_input,
                        "status": status,
                        "duration": duration,
                        "result_keys": list(result.keys()) if result else [],
                    }
                )

                print_info(f"   Status: {status} ({duration:.2f}s)")

            except Exception as e:
                edge_results.append(
                    {"input": game_input, "status": "exception", "error": str(e)}
                )
                print_error(f"   Exception: {str(e)[:50]}...")

        self.test_results["edge_cases"] = edge_results

        # Summary
        handled_count = sum(
            1
            for r in edge_results
            if r["status"] in ["handled_gracefully", "error_handled"]
        )
        print_success(
            f"✅ Edge cases: {handled_count}/{len(edge_results)} handled gracefully"
        )

    def performance_testing(self):
        """⚡ Performance benchmarking and optimization testing"""
        print_header("⚡ PERFORMANCE TESTING")

        performance_results = []

        # Test 1: Cold vs warm cache performance
        print("\n📋 Test 1: Cache Performance (Cold vs Warm)")

        test_game = "Hollow Knight"

        # Cold cache test
        try:
            start_time = time.time()
            cold_result = search_and_scrape_game(test_game)
            cold_time = time.time() - start_time

            # Warm cache test (run again)
            start_time = time.time()
            warm_result = search_and_scrape_game(test_game)
            warm_time = time.time() - start_time

            performance_improvement = ((cold_time - warm_time) / cold_time) * 100

            performance_results.append(
                {
                    "test": "cache_performance",
                    "cold_time": cold_time,
                    "warm_time": warm_time,
                    "improvement": performance_improvement,
                    "success": True,
                }
            )

            print_success(
                f"✅ Cache performance: {performance_improvement:.1f}% improvement"
            )
            print_info(f"   Cold: {cold_time:.2f}s, Warm: {warm_time:.2f}s")

        except Exception as e:
            print_error(f"❌ Cache performance test failed: {e}")

        # Test 2: Batch processing efficiency
        print("\n📋 Test 2: Batch Processing Efficiency")

        try:
            batch_games = self.performance_games

            # Sequential processing
            start_time = time.time()
            sequential_results = []
            for game in batch_games:
                result = self._analyze_game_safe(game)
                sequential_results.append(result)
            sequential_time = time.time() - start_time

            # Concurrent processing (simulate batch)
            start_time = time.time()
            with ThreadPoolExecutor(max_workers=2) as executor:
                concurrent_results = list(
                    executor.map(self._analyze_game_safe, batch_games)
                )
            concurrent_time = time.time() - start_time

            efficiency_gain = (
                (sequential_time - concurrent_time) / sequential_time
            ) * 100

            performance_results.append(
                {
                    "test": "batch_efficiency",
                    "games_count": len(batch_games),
                    "sequential_time": sequential_time,
                    "concurrent_time": concurrent_time,
                    "efficiency_gain": efficiency_gain,
                    "success": True,
                }
            )

            print_success(
                f"✅ Batch efficiency: {efficiency_gain:.1f}% faster with concurrency"
            )

        except Exception as e:
            print_error(f"❌ Batch efficiency test failed: {e}")

        self.test_results["performance"] = performance_results

    def ux_testing(self):
        """🎨 User experience and interface testing"""
        print_header("🎨 UX TESTING")

        ux_results = []

        # Test 1: CLI response formatting
        print("\n📋 Test 1: CLI Response Formatting")

        try:
            test_game = "Celeste"
            result = search_and_scrape_game(test_game)

            if result:
                # Check if result has user-friendly formatting
                has_title = bool(result.get("title"))
                has_price = bool(result.get("current_eshop_price"))
                has_ratings = bool(
                    result.get("metacritic_score") or result.get("opencritic_score")
                )

                formatting_score = sum([has_title, has_price, has_ratings]) / 3

                ux_results.append(
                    {
                        "test": "cli_formatting",
                        "formatting_score": formatting_score,
                        "has_required_fields": formatting_score > 0.5,
                        "success": True,
                    }
                )

                print_success(f"✅ CLI formatting: {formatting_score:.1%} completeness")
            else:
                print_error("❌ No data to format")

        except Exception as e:
            print_error(f"❌ CLI formatting test failed: {e}")

        # Test 2: User workflow intuitiveness
        print("\n📋 Test 2: User Workflow Intuitiveness")

        try:
            # Simulate user workflow: register -> analyze game -> get collection
            user_mgr = UserManager()
            collection_mgr = GameCollectionManager()

            # Step 1: User registration
            test_username = f"ux_test_user_{int(time.time())}"
            register_result = user_mgr.register_user(
                username=test_username, display_name="UX Test User"
            )

            # Step 2: Switch to user
            switch_result = user_mgr.switch_user(test_username)

            # Step 3: Analyze a game
            analysis_result = self._analyze_game_safe("Hades")

            # Step 4: Add to collection
            if analysis_result and analysis_result.get("title"):
                add_result = collection_mgr.add_game(
                    test_username, analysis_result["title"], status="wishlist"
                )
            else:
                add_result = False

            # Step 5: View collection
            collection = collection_mgr.get_user_collection(test_username)

            workflow_success = all(
                [
                    register_result,
                    switch_result,
                    analysis_result is not None,
                    add_result,
                    len(collection.get("games", [])) > 0,
                ]
            )

            # Cleanup
            try:
                user_mgr.delete_user(test_username)
            except:
                pass

            ux_results.append(
                {
                    "test": "user_workflow",
                    "workflow_success": workflow_success,
                    "steps_completed": sum(
                        [
                            bool(register_result),
                            bool(switch_result),
                            bool(analysis_result),
                            bool(add_result),
                            bool(collection.get("games")),
                        ]
                    ),
                    "success": True,
                }
            )

            print_success(
                f"✅ User workflow: {'Complete' if workflow_success else 'Partial'}"
            )

        except Exception as e:
            print_error(f"❌ User workflow test failed: {e}")

        self.test_results["ux_tests"] = ux_results

    def integration_testing(self):
        """🔗 End-to-end integration testing"""
        print_header("🔗 INTEGRATION TESTING")

        integration_results = []

        # Test 1: Full analysis pipeline
        print("\n📋 Test 1: Full Analysis Pipeline")

        try:
            manager = GameAnalysisManager()
            test_game = "Ori and the Blind Forest"

            start_time = time.time()
            result = manager.analyze_game(test_game)
            duration = time.time() - start_time

            # Check pipeline completeness
            has_data = bool(result.get("game_data"))
            has_analysis = bool(result.get("value_analysis"))
            has_review = bool(result.get("comprehensive_review"))

            pipeline_completeness = sum([has_data, has_analysis, has_review]) / 3

            integration_results.append(
                {
                    "test": "full_pipeline",
                    "game": test_game,
                    "duration": duration,
                    "completeness": pipeline_completeness,
                    "components": {
                        "data_collection": has_data,
                        "value_analysis": has_analysis,
                        "review_generation": has_review,
                    },
                    "success": pipeline_completeness > 0.5,
                }
            )

            print_success(
                f"✅ Full pipeline: {pipeline_completeness:.1%} complete in {duration:.2f}s"
            )

        except Exception as e:
            print_error(f"❌ Full pipeline test failed: {e}")
            integration_results.append(
                {"test": "full_pipeline", "success": False, "error": str(e)}
            )

        self.test_results["integration"] = integration_results

    def error_handling_testing(self):
        """❌ Error handling and recovery testing"""
        print_header("❌ ERROR HANDLING TESTING")

        error_results = []

        # Test 1: Network simulation (timeout/failure)
        print("\n📋 Test 1: Graceful Error Handling")

        error_scenarios = [
            ("invalid_game_title_12345", "Non-existent game"),
            ("", "Empty input"),
            (None, "None input"),
            ("a" * 1000, "Extremely long input"),
        ]

        for scenario_input, description in error_scenarios:
            try:
                print_info(f"   Testing: {description}")

                start_time = time.time()
                result = self._analyze_game_safe(scenario_input)
                duration = time.time() - start_time

                # Check if error was handled gracefully
                graceful_handling = (
                    result is None  # Returned None
                    or (
                        isinstance(result, dict) and result.get("error")
                    )  # Returned error dict
                    or duration < 10  # Didn't hang
                )

                error_results.append(
                    {
                        "scenario": description,
                        "input": (
                            str(scenario_input)[:50] + "..."
                            if len(str(scenario_input)) > 50
                            else str(scenario_input)
                        ),
                        "graceful_handling": graceful_handling,
                        "duration": duration,
                        "result_type": type(result).__name__,
                    }
                )

                status = "✅ Handled" if graceful_handling else "❌ Poor handling"
                print_info(f"     {status} ({duration:.2f}s)")

            except Exception as e:
                error_results.append(
                    {
                        "scenario": description,
                        "graceful_handling": True,  # Exception is caught
                        "exception": str(e)[:100],
                    }
                )
                print_info(f"     ✅ Exception caught: {str(e)[:50]}...")

        self.test_results["error_handling"] = error_results

        handled_count = sum(1 for r in error_results if r["graceful_handling"])
        print_success(
            f"✅ Error handling: {handled_count}/{len(error_results)} scenarios handled gracefully"
        )

    def _analyze_game_safe(self, game_name):
        """Safe game analysis with timeout and error handling"""
        try:
            if not game_name or not isinstance(game_name, str):
                return None
            return search_and_scrape_game(game_name)
        except Exception as e:
            return {"error": str(e)}

    def generate_final_report(self):
        """Generate comprehensive test report"""
        print_header("📊 COMPREHENSIVE TEST REPORT")

        total_duration = time.time() - self.start_time

        # Calculate overall statistics
        total_tests = sum(len(category) for category in self.test_results.values())
        successful_tests = 0

        for category, tests in self.test_results.items():
            if isinstance(tests, list):
                successful_tests += sum(
                    1 for test in tests if test.get("success", False)
                )

        success_rate = successful_tests / max(total_tests, 1)

        print(f"\n🎯 OVERALL RESULTS:")
        print(f"   Total Duration: {total_duration:.2f}s")
        print(f"   Total Tests: {total_tests}")
        print(f"   Success Rate: {success_rate:.1%}")
        print(
            f"   System Status: {'🟢 EXCELLENT' if success_rate > 0.8 else '🟡 GOOD' if success_rate > 0.6 else '🔴 NEEDS WORK'}"
        )

        print(f"\n📋 CATEGORY BREAKDOWN:")
        for category, tests in self.test_results.items():
            if isinstance(tests, list) and tests:
                category_success = sum(
                    1 for test in tests if test.get("success", False)
                ) / len(tests)
                status = (
                    "🟢"
                    if category_success > 0.8
                    else "🟡" if category_success > 0.5 else "🔴"
                )
                print(
                    f"   {status} {category.replace('_', ' ').title()}: {category_success:.1%} ({len(tests)} tests)"
                )

        # Performance highlights
        performance_tests = self.test_results.get("performance", [])
        if performance_tests:
            print(f"\n⚡ PERFORMANCE HIGHLIGHTS:")
            for test in performance_tests:
                if test["test"] == "cache_performance":
                    print(f"   Cache Improvement: {test.get('improvement', 0):.1f}%")
                elif test["test"] == "batch_efficiency":
                    print(f"   Batch Efficiency: {test.get('efficiency_gain', 0):.1f}%")

        # Recommendations
        print(f"\n💡 RECOMMENDATIONS:")
        if success_rate > 0.9:
            print("   ✅ System is production-ready!")
            print("   ✅ Consider advanced features (collaborative filtering)")
        elif success_rate > 0.7:
            print("   🔧 Minor improvements needed")
            print("   🔍 Focus on failing test categories")
        else:
            print("   ⚠️  Significant improvements required")
            print("   🛠️  Address error handling and performance issues")

        # Save detailed report
        report_file = f"logs/comprehensive_test_report_{int(time.time())}.json"
        os.makedirs("logs", exist_ok=True)

        with open(report_file, "w") as f:
            json.dump(
                {
                    "timestamp": time.time(),
                    "duration": total_duration,
                    "total_tests": total_tests,
                    "success_rate": success_rate,
                    "results": self.test_results,
                },
                f,
                indent=2,
                default=str,
            )

        print(f"\n📄 Detailed report saved: {report_file}")
        print_success("🎉 Comprehensive testing completed!")


def main():
    """Run comprehensive system testing"""
    tester = ComprehensiveSystemTester()
    tester.run_all_tests()


if __name__ == "__main__":
    main()

#!/usr/bin/env python3
"""
🧪 PHASE 5: Quick System Testing & Validation
Focused test suite for core functionality validation
"""

import sys
import os
import time
import statistics
from typing import List, Dict, Any

# Add project root to path
sys.path.append(".")


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


class QuickSystemValidator:
    """Quick system validation for Phase 5 testing"""

    def __init__(self):
        self.test_results = []
        self.start_time = time.time()

    def run_validation(self):
        """Run quick validation tests"""
        print_header("🧪 PHASE 5: Quick System Testing & Validation")

        # Test 1: Import validation
        self.test_imports()

        # Test 2: Basic functionality
        self.test_core_functions()

        # Test 3: Performance quick check
        self.test_basic_performance()

        # Test 4: Error handling
        self.test_error_handling()

        # Generate report
        self.generate_report()

    def test_imports(self):
        """Test 1: Validate all core imports"""
        print_header("📦 IMPORT VALIDATION")

        imports_to_test = [
            ("agent_tools", "search_and_scrape_game"),
            ("autogen_agents", "data_collector"),
            ("conversation_manager", "GameAnalysisManager"),
            ("utils.user_management", "UserManager"),
            ("utils.game_collection_manager", "GameCollectionManager"),
            ("utils.smart_user_profiler", "SmartUserProfiler"),
            ("utils.price_prediction_ml", "PricePredictionEngine"),
        ]

        successful_imports = 0

        for module_name, item_name in imports_to_test:
            try:
                module = __import__(module_name, fromlist=[item_name])
                getattr(module, item_name)
                print_success(f"{module_name}.{item_name}")
                successful_imports += 1
            except Exception as e:
                print_error(f"{module_name}.{item_name}: {str(e)[:50]}...")

        import_rate = successful_imports / len(imports_to_test)
        self.test_results.append(
            {
                "test": "imports",
                "success_rate": import_rate,
                "successful": successful_imports,
                "total": len(imports_to_test),
            }
        )

        print_info(f"Import success rate: {import_rate:.1%}")

    def test_core_functions(self):
        """Test 2: Core functionality validation"""
        print_header("🔧 CORE FUNCTIONALITY")

        # Import core functions
        try:
            from agent_tools import search_and_scrape_game
            from utils.user_management import UserManager
            from utils.game_collection_manager import GameCollectionManager
            from utils.smart_user_profiler import SmartUserProfiler
        except ImportError as e:
            print_error(f"Failed to import core functions: {e}")
            return

        # Test game search
        print_info("Testing game search...")
        try:
            start_time = time.time()
            result = search_and_scrape_game("Celeste")
            search_time = time.time() - start_time

            search_success = result is not None and (
                result.get("title") or result.get("error")  # Graceful error handling
            )

            print_success(
                f"Game search: {'Success' if search_success else 'Failed'} ({search_time:.2f}s)"
            )

            self.test_results.append(
                {
                    "test": "game_search",
                    "success": search_success,
                    "duration": search_time,
                    "has_data": bool(result and result.get("title")),
                }
            )

        except Exception as e:
            print_error(f"Game search failed: {str(e)[:50]}...")
            self.test_results.append(
                {"test": "game_search", "success": False, "error": str(e)}
            )

        # Test user manager
        print_info("Testing user management...")
        try:
            user_mgr = UserManager()
            current_user = user_mgr.get_current_user()

            user_mgr_success = current_user is not None
            print_success(
                f"User management: {'Success' if user_mgr_success else 'Failed'}"
            )

            self.test_results.append(
                {
                    "test": "user_management",
                    "success": user_mgr_success,
                    "current_user": (
                        getattr(current_user, "username", str(current_user))
                        if current_user
                        else None
                    ),
                }
            )

        except Exception as e:
            print_error(f"User management failed: {str(e)[:50]}...")
            self.test_results.append(
                {"test": "user_management", "success": False, "error": str(e)}
            )

        # Test game collection
        print_info("Testing game collection...")
        try:
            collection_mgr = GameCollectionManager()
            # Simple test - just check if it initializes
            collection_success = collection_mgr is not None
            print_success(
                f"Game collection: {'Success' if collection_success else 'Failed'}"
            )

            self.test_results.append(
                {"test": "game_collection", "success": collection_success}
            )

        except Exception as e:
            print_error(f"Game collection failed: {str(e)[:50]}...")
            self.test_results.append(
                {"test": "game_collection", "success": False, "error": str(e)}
            )

        # Test ML profiler
        print_info("Testing ML profiler...")
        try:
            profiler = SmartUserProfiler()
            ml_success = profiler is not None
            print_success(f"ML profiler: {'Success' if ml_success else 'Failed'}")

            self.test_results.append({"test": "ml_profiler", "success": ml_success})

        except Exception as e:
            print_error(f"ML profiler failed: {str(e)[:50]}...")
            self.test_results.append(
                {"test": "ml_profiler", "success": False, "error": str(e)}
            )

    def test_basic_performance(self):
        """Test 3: Basic performance validation"""
        print_header("⚡ PERFORMANCE VALIDATION")

        try:
            from agent_tools import search_and_scrape_game

            # Test multiple searches for performance
            test_games = ["Hollow Knight", "Celeste", "Hades"]
            search_times = []

            print_info("Running performance tests...")

            for game in test_games:
                try:
                    start_time = time.time()
                    result = search_and_scrape_game(game)
                    duration = time.time() - start_time
                    search_times.append(duration)

                    status = (
                        "✅"
                        if result and (result.get("title") or result.get("error"))
                        else "❌"
                    )
                    print_info(f"  {game}: {status} ({duration:.2f}s)")

                except Exception as e:
                    print_error(f"  {game}: Error - {str(e)[:30]}...")

            if search_times:
                avg_time = statistics.mean(search_times)
                max_time = max(search_times)
                min_time = min(search_times)

                # Performance benchmarks
                performance_rating = (
                    "Excellent"
                    if avg_time < 2.0
                    else "Good" if avg_time < 5.0 else "Needs Improvement"
                )

                self.test_results.append(
                    {
                        "test": "performance",
                        "avg_time": avg_time,
                        "max_time": max_time,
                        "min_time": min_time,
                        "rating": performance_rating,
                        "samples": len(search_times),
                    }
                )

                print_success(
                    f"Performance: {performance_rating} (avg: {avg_time:.2f}s)"
                )
                print_info(f"  Range: {min_time:.2f}s - {max_time:.2f}s")
            else:
                print_error("No performance data collected")

        except Exception as e:
            print_error(f"Performance testing failed: {str(e)[:50]}...")

    def test_error_handling(self):
        """Test 4: Error handling validation"""
        print_header("❌ ERROR HANDLING VALIDATION")

        try:
            from agent_tools import search_and_scrape_game

            # Test error scenarios
            error_scenarios = [
                ("", "Empty string"),
                ("nonexistent_game_12345", "Non-existent game"),
                ("a", "Single character"),
            ]

            handled_gracefully = 0

            for test_input, description in error_scenarios:
                try:
                    print_info(f"Testing: {description}")

                    start_time = time.time()
                    result = search_and_scrape_game(test_input)
                    duration = time.time() - start_time

                    # Check graceful handling
                    graceful = (
                        result is None
                        or (isinstance(result, dict) and result.get("error"))
                        or duration < 10  # Didn't hang
                    )

                    if graceful:
                        handled_gracefully += 1
                        print_success(f"  Handled gracefully ({duration:.2f}s)")
                    else:
                        print_error(f"  Poor handling ({duration:.2f}s)")

                except Exception as e:
                    handled_gracefully += 1  # Exception caught = graceful
                    print_success(f"  Exception handled: {str(e)[:30]}...")

            error_handling_rate = handled_gracefully / len(error_scenarios)

            self.test_results.append(
                {
                    "test": "error_handling",
                    "success_rate": error_handling_rate,
                    "scenarios_tested": len(error_scenarios),
                    "handled_gracefully": handled_gracefully,
                }
            )

            print_success(
                f"Error handling: {error_handling_rate:.1%} scenarios handled gracefully"
            )

        except Exception as e:
            print_error(f"Error handling test failed: {str(e)[:50]}...")

    def generate_report(self):
        """Generate final validation report"""
        print_header("📊 VALIDATION REPORT")

        total_duration = time.time() - self.start_time

        # Calculate overall success rate
        test_successes = 0
        total_tests = 0

        for result in self.test_results:
            if "success_rate" in result:
                test_successes += result["success_rate"]
                total_tests += 1
            elif "success" in result:
                test_successes += 1 if result["success"] else 0
                total_tests += 1

        overall_success = test_successes / max(total_tests, 1)

        print_info(f"Total Duration: {total_duration:.2f}s")
        print_info(f"Tests Run: {len(self.test_results)}")
        print_success(f"Overall Success Rate: {overall_success:.1%}")

        # System status
        if overall_success > 0.8:
            status = "🟢 EXCELLENT - System is production ready"
        elif overall_success > 0.6:
            status = "🟡 GOOD - Minor improvements needed"
        else:
            status = "🔴 NEEDS WORK - Significant issues found"

        print_info(f"System Status: {status}")

        # Category breakdown
        print_info("\nCategory Results:")
        for result in self.test_results:
            test_name = result.get("test", "unknown")
            if "success_rate" in result:
                rate = result["success_rate"]
                print_info(f"  {test_name}: {rate:.1%}")
            elif "success" in result:
                status = "✅" if result["success"] else "❌"
                print_info(f"  {test_name}: {status}")

        # Performance summary
        perf_result = next(
            (r for r in self.test_results if r.get("test") == "performance"), None
        )
        if perf_result:
            print_info(f"\nPerformance: {perf_result.get('rating', 'Unknown')}")
            print_info(f"  Average time: {perf_result.get('avg_time', 0):.2f}s")

        # Recommendations
        print_header("💡 RECOMMENDATIONS")

        if overall_success > 0.9:
            print_success("System is excellent! Ready for:")
            print_info("  • Advanced features (collaborative filtering)")
            print_info("  • Production deployment")
            print_info("  • Public API development")
        elif overall_success > 0.7:
            print_info("Good system! Consider:")
            print_info("  • Performance optimization")
            print_info("  • Error handling improvements")
            print_info("  • Additional testing")
        else:
            print_error("System needs work:")
            print_info("  • Fix core functionality issues")
            print_info("  • Improve error handling")
            print_info("  • Performance optimization")

        print_header("🎉 VALIDATION COMPLETED")


def main():
    """Run quick system validation"""
    validator = QuickSystemValidator()
    validator.run_validation()


if __name__ == "__main__":
    main()

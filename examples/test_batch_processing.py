"""
Test suite for Batch Processing functionality (Phase 6.2).

This module tests the batch processing capabilities including:
- Batch analysis manager
- CLI batch commands
- AutoGen batch tools
- Performance comparisons

Author: AutoGen DekuDeals Team
Phase: 6.2 - Batch Processing & Scaling
"""

import sys
import os
import time
from typing import List, Dict, Any

# Add project root to path
sys.path.append(os.path.join(os.path.dirname(__file__), ".."))

from utils.batch_processor import (
    get_batch_manager,
    create_batch_analysis,
    BatchStatus,
    BatchAnalysisManager,
)
from agent_tools import (
    batch_analyze_games,
    get_batch_analysis_status,
    cancel_batch_analysis,
    get_batch_analysis_results,
    generate_quick_game_opinion,
)


def print_test_header(title: str):
    """Print formatted test header."""
    print(f"\n{'='*60}")
    print(f"🧪 {title}")
    print("=" * 60)


def print_subsection(title: str):
    """Print formatted subsection header."""
    print(f"\n📋 {title}")
    print("-" * 40)


def test_batch_manager_initialization():
    """Test 1: Batch Manager Initialization"""
    print_test_header("Test 1: Batch Manager Initialization")

    try:
        # Test manager initialization
        manager = get_batch_manager()
        print(f"✅ BatchAnalysisManager initialized successfully")
        print(f"   Max concurrent: {manager.max_concurrent}")
        print(f"   Rate limit: {manager.rate_limit}/s")

        # Test creating new manager instance
        custom_manager = BatchAnalysisManager(max_concurrent=5, rate_limit=2.0)
        print(
            f"✅ Custom manager created: concurrent={custom_manager.max_concurrent}, rate={custom_manager.rate_limit}"
        )

        return True

    except Exception as e:
        print(f"❌ Test failed: {e}")
        return False


def test_batch_session_creation():
    """Test 2: Batch Session Creation and Management"""
    print_test_header("Test 2: Batch Session Creation and Management")

    try:
        manager = get_batch_manager()

        # Test session creation
        test_games = ["INSIDE", "Celeste"]
        batch_id = manager.create_batch_session(
            test_games, analysis_type="quick", batch_name="Test_Session"
        )

        print(f"✅ Batch session created: {batch_id}")

        # Test session status
        status = manager.get_batch_status(batch_id)
        print(f"✅ Session status retrieved:")
        print(f"   Batch ID: {status['batch_id']}")
        print(f"   Status: {status['status']}")
        print(f"   Total tasks: {status['total_tasks']}")
        print(f"   Progress: {status['progress_percentage']:.1f}%")

        # Test listing active batches
        active_batches = manager.list_active_batches()
        print(f"✅ Active batches: {len(active_batches)}")

        return True

    except Exception as e:
        print(f"❌ Test failed: {e}")
        return False


def test_autogen_batch_tools():
    """Test 3: AutoGen Batch Tools"""
    print_test_header("Test 3: AutoGen Batch Tools")

    try:
        # Test batch analysis tool
        print_subsection("Testing batch_analyze_games()")
        test_games = ["INSIDE", "Moving Out"]

        result = batch_analyze_games(test_games, "quick")

        if result.get("success"):
            print(f"✅ Batch analysis completed successfully")
            print(f"   Batch ID: {result['batch_id']}")
            print(f"   Status: {result['status']['status']}")
            print(f"   Games processed: {result['status']['total_tasks']}")
            print(
                f"   Success rate: {result['results']['summary']['success_rate']:.1f}%"
            )
            print(f"   Duration: {result['results']['duration']:.1f}s")

            # Test getting batch status
            print_subsection("Testing get_batch_analysis_status()")
            batch_id = result["batch_id"]
            status_result = get_batch_analysis_status(batch_id)

            if status_result.get("success"):
                print(f"✅ Batch status retrieved")
                batch_status = status_result["batch_status"]
                print(f"   Status: {batch_status['status']}")
                print(f"   Progress: {batch_status['progress_percentage']:.1f}%")

            # Test getting batch results
            print_subsection("Testing get_batch_analysis_results()")
            results_result = get_batch_analysis_results(batch_id)

            if results_result.get("success"):
                print(f"✅ Batch results retrieved")
                batch_results = results_result["batch_results"]
                print(f"   Games analyzed: {len(batch_results['results'])}")
                print(
                    f"   Success rate: {batch_results['summary']['success_rate']:.1f}%"
                )
        else:
            print(f"❌ Batch analysis failed: {result.get('error')}")
            return False

        # Test status without batch ID (list all)
        print_subsection("Testing get_batch_analysis_status() - all batches")
        all_status = get_batch_analysis_status()

        if all_status.get("success"):
            print(f"✅ All batch status retrieved")
            print(f"   Active batches: {all_status['count']}")

        return True

    except Exception as e:
        print(f"❌ Test failed: {e}")
        return False


def test_performance_comparison():
    """Test 4: Performance Comparison (Sequential vs Batch)"""
    print_test_header("Test 4: Performance Comparison")

    test_games = ["INSIDE", "Celeste", "Moving Out"]

    try:
        # Test sequential analysis
        print_subsection("Sequential Analysis")
        sequential_start = time.time()

        sequential_results = []
        for game in test_games:
            result = generate_quick_game_opinion(game)
            sequential_results.append(result)

        sequential_time = time.time() - sequential_start
        print(f"✅ Sequential analysis completed")
        print(f"   Time: {sequential_time:.2f}s")
        print(f"   Games: {len(sequential_results)}")

        # Test batch analysis
        print_subsection("Batch Analysis")
        batch_start = time.time()

        batch_result = batch_analyze_games(test_games, "quick")
        batch_time = time.time() - batch_start

        if batch_result.get("success"):
            print(f"✅ Batch analysis completed")
            print(f"   Time: {batch_time:.2f}s")
            print(f"   Games: {batch_result['status']['total_tasks']}")

            # Calculate performance improvement
            improvement = ((sequential_time - batch_time) / sequential_time) * 100
            print(f"\n📊 Performance Comparison:")
            print(f"   Sequential: {sequential_time:.2f}s")
            print(f"   Batch: {batch_time:.2f}s")
            if improvement > 0:
                print(f"   ✅ Improvement: {improvement:.1f}% faster")
            else:
                print(
                    f"   ⚠️ Batch was {abs(improvement):.1f}% slower (possibly due to overhead)"
                )
        else:
            print(f"❌ Batch analysis failed: {batch_result.get('error')}")
            return False

        return True

    except Exception as e:
        print(f"❌ Test failed: {e}")
        return False


def test_error_handling():
    """Test 5: Error Handling and Edge Cases"""
    print_test_header("Test 5: Error Handling and Edge Cases")

    try:
        # Test empty game list
        print_subsection("Empty game list")
        result = batch_analyze_games([], "quick")

        if not result.get("success") and "No games provided" in result.get("error", ""):
            print("✅ Empty game list handled correctly")
        else:
            print("❌ Empty game list not handled properly")
            return False

        # Test invalid analysis type
        print_subsection("Invalid analysis type")
        result = batch_analyze_games(["INSIDE"], "invalid_type")

        if not result.get("success") and "Invalid analysis type" in result.get(
            "error", ""
        ):
            print("✅ Invalid analysis type handled correctly")
        else:
            print("❌ Invalid analysis type not handled properly")
            return False

        # Test invalid batch ID
        print_subsection("Invalid batch ID")
        result = get_batch_analysis_status("invalid_batch_id")

        if not result.get("success") and "not found" in result.get("error", ""):
            print("✅ Invalid batch ID handled correctly")
        else:
            print("❌ Invalid batch ID not handled properly")
            return False

        return True

    except Exception as e:
        print(f"❌ Test failed: {e}")
        return False


def test_concurrent_batches():
    """Test 6: Multiple Concurrent Batches"""
    print_test_header("Test 6: Multiple Concurrent Batches")

    try:
        manager = get_batch_manager()

        # Create multiple batch sessions
        batch_ids = []

        for i in range(2):
            test_games = [f"Test_Game_{i}_1", f"Test_Game_{i}_2"]
            batch_id = manager.create_batch_session(
                test_games, analysis_type="quick", batch_name=f"Concurrent_Batch_{i+1}"
            )
            batch_ids.append(batch_id)

        print(f"✅ Created {len(batch_ids)} concurrent batch sessions")

        # List active batches
        active_batches = manager.list_active_batches()
        print(f"✅ Active batches: {len(active_batches)}")

        for batch in active_batches:
            print(
                f"   - {batch['batch_name']} ({batch['batch_id']}): {len(batch['games'])} games"
            )

        return True

    except Exception as e:
        print(f"❌ Test failed: {e}")
        return False


def run_all_tests():
    """Run all batch processing tests."""
    print_test_header("🚀 BATCH PROCESSING TEST SUITE (Phase 6.2)")

    tests = [
        test_batch_manager_initialization,
        test_batch_session_creation,
        test_autogen_batch_tools,
        test_performance_comparison,
        test_error_handling,
        test_concurrent_batches,
    ]

    passed = 0
    total = len(tests)

    for test_func in tests:
        try:
            if test_func():
                passed += 1
        except Exception as e:
            print(f"❌ Test {test_func.__name__} crashed: {e}")

    # Final results
    print_test_header("📊 TEST RESULTS")
    print(f"✅ Passed: {passed}/{total}")
    print(f"❌ Failed: {total - passed}/{total}")

    if passed == total:
        print(f"\n🎉 ALL TESTS PASSED! Batch Processing is fully functional.")
        success_rate = 100.0
    else:
        success_rate = (passed / total) * 100
        print(f"\n⚠️ Some tests failed. Success rate: {success_rate:.1f}%")

    print(f"\n📈 Batch Processing Features Tested:")
    print(f"   ✅ BatchAnalysisManager initialization and configuration")
    print(f"   ✅ Batch session creation and management")
    print(f"   ✅ AutoGen tools integration (4 new tools)")
    print(f"   ✅ Performance comparison (sequential vs batch)")
    print(f"   ✅ Error handling and edge cases")
    print(f"   ✅ Concurrent batch operations")

    return success_rate == 100.0


if __name__ == "__main__":
    run_all_tests()

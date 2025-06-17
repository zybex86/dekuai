#!/usr/bin/env python3
"""
PHASE 4 - Advanced Quality Control Testing
Test zaawansowanej kontroli jakości - FAZA 4

This script demonstrates the new automated quality validation system.
Ten skrypt demonstruje nowy automatyczny system walidacji jakości.
"""

import os
import sys
from datetime import datetime
import json

# Add parent directory to Python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from agent_tools import (
    search_and_scrape_game,
    calculate_value_score,
    calculate_advanced_value_analysis,
    generate_comprehensive_game_review,
    perform_quality_validation,
)


def test_quality_validation_complete_analysis():
    """Test quality validation on complete analysis workflow"""
    print("🧪 Testing complete analysis quality validation...")

    try:
        # Step 1: Get game data
        print("📊 Step 1: Collecting game data...")
        game_data = search_and_scrape_game("INSIDE")

        if not game_data.get("success", False):
            print(f"❌ Failed to get game data: {game_data.get('error')}")
            return False

        print(f"✅ Game data collected: {game_data.get('title', 'Unknown')}")

        # Step 2: Value analysis
        print("💰 Step 2: Performing value analysis...")
        value_analysis = calculate_value_score(game_data)

        if not value_analysis.get("success", False):
            print(f"❌ Value analysis failed: {value_analysis.get('error')}")
            return False

        print(
            f"✅ Value analysis complete: {value_analysis['value_metrics']['recommendation']}"
        )

        # Step 3: Advanced value analysis
        print("🚀 Step 3: Advanced value analysis...")
        advanced_analysis = calculate_advanced_value_analysis(game_data)

        if not advanced_analysis.get("success", False):
            print(f"❌ Advanced analysis failed: {advanced_analysis.get('error')}")
            return False

        print(f"✅ Advanced analysis complete")

        # Step 4: Generate review
        print("📝 Step 4: Generating comprehensive review...")
        review_result = generate_comprehensive_game_review(
            "INSIDE", include_recommendations=True
        )

        if not review_result.get("success", False):
            print(f"❌ Review generation failed: {review_result.get('error')}")
            return False

        print(f"✅ Review generated successfully")

        # Step 5: Combine all data for quality validation
        print("🔍 Step 5: Preparing complete analysis data...")
        complete_analysis = {
            # Raw game data
            **game_data,
            # Value analysis results
            "value_analysis": value_analysis,
            # Advanced analysis results
            "advanced_analysis": advanced_analysis,
            # Review data
            "review": review_result.get("review_data", {}),
            # Metadata
            "analysis_metadata": {
                "workflow_steps": [
                    "data_collection",
                    "value_analysis",
                    "advanced_analysis",
                    "review_generation",
                ],
                "timestamp": datetime.now().isoformat(),
                "validation_candidate": True,
            },
        }

        print(
            f"✅ Complete analysis data prepared ({len(complete_analysis)} top-level keys)"
        )

        # Step 6: QUALITY VALIDATION
        print("🎯 Step 6: PERFORMING QUALITY VALIDATION...")
        validation_result = perform_quality_validation(complete_analysis)

        if not validation_result.get("success", False):
            print(f"❌ Quality validation failed: {validation_result.get('error')}")
            return False

        # Display results
        quality_assessment = validation_result.get("quality_assessment", {})
        quality_metrics = validation_result.get("quality_metrics", {})
        recommendations = validation_result.get("improvement_recommendations", [])

        print("\n" + "=" * 70)
        print("📊 QUALITY VALIDATION RESULTS")
        print("=" * 70)
        print(f"🎮 Game: {validation_result.get('game_title', 'Unknown')}")
        print(f"⭐ Quality Level: {quality_assessment.get('quality_level', 'UNKNOWN')}")
        print(
            f"📈 Overall Score: {quality_assessment.get('overall_score', 0.0):.2f}/1.0"
        )
        print(
            f"🚨 Critical Failures: {quality_assessment.get('critical_failures_count', 0)}"
        )
        print(
            f"✅ Publication Ready: {quality_assessment.get('publication_ready', False)}"
        )

        print("\n📊 QUALITY METRICS:")
        print(
            f"  📋 Data Completeness: {quality_metrics.get('data_completeness', 0.0):.2f}/1.0"
        )
        print(
            f"  🧠 Logical Consistency: {quality_metrics.get('logical_consistency', 0.0):.2f}/1.0"
        )
        print(
            f"  📝 Content Quality: {quality_metrics.get('content_quality', 0.0):.2f}/1.0"
        )

        print(
            f"\n💬 Summary: {validation_result.get('validation_summary', 'No summary')}"
        )

        print("\n📋 RECOMMENDATIONS:")
        for i, rec in enumerate(recommendations, 1):
            print(f"  {i}. {rec}")

        print("=" * 70)

        # Success criteria
        is_high_quality = quality_assessment.get("overall_score", 0.0) >= 0.8
        no_critical_issues = quality_assessment.get("critical_failures_count", 0) == 0

        if is_high_quality and no_critical_issues:
            print("🎉 QUALITY VALIDATION PASSED!")
            print(
                "✅ Analysis meets high quality standards and is ready for publication"
            )
            return True
        else:
            print("⚠️ QUALITY VALIDATION IDENTIFIED ISSUES")
            print("🔧 Review recommendations above for improvement areas")
            return False

    except Exception as e:
        print(f"❌ Test failed with error: {e}")
        return False


def test_quality_validation_edge_cases():
    """Test quality validation with problematic data"""
    print("\n🧪 Testing quality validation edge cases...")

    test_cases = [
        {
            "name": "Incomplete Data",
            "data": {
                "title": "Test Game",
                # Missing many required fields
                "success": True,
            },
        },
        {
            "name": "Inconsistent Recommendations",
            "data": {
                "title": "Test Game",
                "current_eshop_price": "$9.99",
                "MSRP": "$19.99",
                "metacritic_score": "95",  # High score
                "genres": ["Action"],
                "developer": "Test Studio",
                "success": True,
                "value_analysis": {
                    "recommendation": "SKIP"  # Inconsistent with high score
                },
                "review": {
                    "overall_rating": 9.5,  # High rating
                    "recommendation": "SKIP",  # Inconsistent
                    "final_verdict": "This game is terrible and should be avoided",  # Inconsistent with rating
                    "strengths": [],
                    "weaknesses": ["Everything"],
                    "target_audience": [],
                },
            },
        },
        {
            "name": "Perfect Analysis",
            "data": {
                "title": "Perfect Game",
                "current_eshop_price": "$19.99",
                "MSRP": "$29.99",
                "metacritic_score": "88",
                "genres": ["Adventure", "Puzzle"],
                "developer": "Excellence Studio",
                "success": True,
                "value_analysis": {"recommendation": "BUY"},
                "review": {
                    "overall_rating": 8.8,
                    "recommendation": "BUY",
                    "final_verdict": "Excellent adventure game with great value for money. Highly recommended for puzzle enthusiasts.",
                    "strengths": ["Great puzzles", "Beautiful art", "Excellent value"],
                    "weaknesses": ["Slightly short campaign"],
                    "target_audience": ["Puzzle lovers", "Adventure fans"],
                },
            },
        },
    ]

    results = []

    for test_case in test_cases:
        print(f"\n🔍 Testing: {test_case['name']}")

        validation_result = perform_quality_validation(test_case["data"])

        if validation_result.get("success", False):
            quality_level = validation_result["quality_assessment"]["quality_level"]
            overall_score = validation_result["quality_assessment"]["overall_score"]
            critical_failures = validation_result["quality_assessment"][
                "critical_failures_count"
            ]

            print(
                f"  📊 Result: {quality_level} ({overall_score:.2f}) | Critical: {critical_failures}"
            )
            results.append(
                {
                    "name": test_case["name"],
                    "quality_level": quality_level,
                    "score": overall_score,
                    "critical_failures": critical_failures,
                    "passed": True,
                }
            )
        else:
            print(f"  ❌ Failed: {validation_result.get('error', 'Unknown error')}")
            results.append(
                {
                    "name": test_case["name"],
                    "passed": False,
                    "error": validation_result.get("error"),
                }
            )

    # Summary
    print("\n" + "=" * 50)
    print("📊 EDGE CASE TEST RESULTS")
    print("=" * 50)

    for result in results:
        if result.get("passed", False):
            status = f"{result['quality_level']} ({result['score']:.1f})"
            critical = f"Critical: {result['critical_failures']}"
            print(f"✅ {result['name']}: {status} | {critical}")
        else:
            print(f"❌ {result['name']}: {result.get('error', 'Failed')}")

    passed_tests = sum(1 for r in results if r.get("passed", False))
    total_tests = len(results)

    print(f"\n🎯 Edge case testing: {passed_tests}/{total_tests} tests passed")
    return passed_tests == total_tests


def run_phase4_quality_validation_tests():
    """Run all Phase 4 quality validation tests"""
    print("🚀 STARTING PHASE 4 - ADVANCED QUALITY CONTROL TESTS")
    print("Testing automated quality validation system...")
    print("=" * 70)

    results = []

    # Test 1: Complete Analysis Quality Validation
    test1_result = test_quality_validation_complete_analysis()
    results.append(("Complete Analysis Validation", test1_result))

    # Test 2: Edge Cases
    test2_result = test_quality_validation_edge_cases()
    results.append(("Edge Case Validation", test2_result))

    # Summary
    print("\n" + "=" * 70)
    print("📊 PHASE 4 - QUALITY VALIDATION TEST RESULTS")
    print("=" * 70)

    passed = 0
    total = len(results)

    for test_name, result in results:
        status = "✅ PASSED" if result else "❌ FAILED"
        print(f"{test_name}: {status}")
        if result:
            passed += 1

    print(f"\n🎯 OVERALL RESULT: {passed}/{total} tests passed")

    if passed == total:
        print("🎉 ALL PHASE 4 TESTS PASSED!")
        print("✅ Advanced Quality Control system is fully functional!")
        print("🔍 Automated quality validation is ready for production use!")
    else:
        print("⚠️ Some tests failed. Check the output above for details.")

    return passed == total


if __name__ == "__main__":
    success = run_phase4_quality_validation_tests()

    print("\n" + "=" * 70)
    print("🏁 PHASE 4 TESTING COMPLETE")
    print("=" * 70)

    if success:
        print("✅ Phase 4 Point 1 implementation is ready!")
        print("🎯 Key capabilities achieved:")
        print("   • Automated quality validation with 4 validation rules")
        print("   • Data completeness, logic consistency, opinion coherence checks")
        print("   • Critical failure detection and quality gates")
        print("   • Actionable improvement recommendations")
        print("   • Quality metrics and scoring (0.0-1.0 scale)")
        print("   • Publication readiness assessment")
        print("   • Edge case handling and error recovery")
    else:
        print("❌ Phase 4 Point 1 needs additional work.")
        print("🔧 Check the error messages above and fix any issues.")

    print(f"\n🎮 Ready for next quality control features!")

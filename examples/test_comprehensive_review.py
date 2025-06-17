"""
Test Phase 3 Point 1: Comprehensive Review Generation
Test Fazy 3 Punkt 1: Kompleksowe generowanie opinii

This module tests the comprehensive review generation system that combines
all analyses from Phase 1, 2, and 3 into unified game reviews.
"""

import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from agent_tools import (
    generate_comprehensive_game_review,
    generate_quick_game_opinion,
    compare_games_with_reviews,
    get_random_game_sample,
    scrape_dekudeals_category,
    get_games_from_popular_categories,
)
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


def test_comprehensive_review():
    """Test comprehensive review generation for a single game."""
    print("=" * 70)
    print("🎮 PHASE 3 PUNKT 1 - TEST COMPREHENSIVE REVIEW")
    print("=" * 70)

    test_game = "Hollow Knight"

    try:
        print(f"\n🚀 Testing comprehensive review for: {test_game}")
        print("-" * 50)

        # Generate comprehensive review
        result = generate_comprehensive_game_review(
            test_game, include_recommendations=True
        )

        if result.get("success", False):
            print("✅ COMPREHENSIVE REVIEW SUCCESS!")
            print(f"📊 Game Title: {result['game_title']}")

            review_data = result.get("review_data", {})
            print(f"⭐ Overall Rating: {review_data.get('overall_rating', 'N/A')}/10")
            print(
                f"🎯 Recommendation: {review_data.get('recommendation', 'N/A').replace('_', ' ').title()}"
            )
            print(
                f"🔍 Confidence: {review_data.get('confidence', 'N/A').replace('_', ' ').title()}"
            )

            # Display strengths
            strengths = review_data.get("strengths", [])
            if strengths:
                print(f"\n✅ Key Strengths:")
                for i, strength in enumerate(strengths[:3], 1):
                    print(f"   {i}. {strength}")

            # Display target audience
            audience = review_data.get("target_audience", [])
            if audience:
                print(f"\n👥 Target Audience: {', '.join(audience[:3])}")

            # Display final verdict (first 200 chars)
            verdict = review_data.get("final_verdict", "")
            if verdict:
                print(f"\n📝 Final Verdict (preview):")
                print(f"   {verdict[:200]}{'...' if len(verdict) > 200 else ''}")

            # Analysis success status
            underlying = result.get("underlying_analyses", {})
            print(f"\n🔧 Analysis Status:")
            print(
                f"   Basic Analysis: {'✅' if underlying.get('basic_analysis_success') else '❌'}"
            )
            print(
                f"   Advanced Analysis: {'✅' if underlying.get('advanced_analysis_success') else '❌'}"
            )
            print(
                f"   Recommendation Analysis: {'✅' if underlying.get('recommendation_analysis_success') else '❌'}"
            )

            # Display formatted review section
            formatted_review = result.get("formatted_review", "")
            if formatted_review:
                print(f"\n📄 FORMATTED REVIEW (First 500 chars):")
                print("-" * 30)
                print(
                    formatted_review[:500] + "..."
                    if len(formatted_review) > 500
                    else formatted_review
                )

            return True
        else:
            print("❌ COMPREHENSIVE REVIEW FAILED!")
            print(f"Error: {result.get('error', 'Unknown error')}")
            return False

    except Exception as e:
        print(f"❌ Exception during comprehensive review test: {e}")
        return False


def test_quick_opinion():
    """Test quick opinion generation."""
    print("\n" + "=" * 70)
    print("⚡ PHASE 3 PUNKT 1 - TEST QUICK OPINION")
    print("=" * 70)

    test_game = "Celeste"

    try:
        print(f"\n⚡ Testing quick opinion for: {test_game}")
        print("-" * 50)

        # Generate quick opinion
        result = generate_quick_game_opinion(test_game)

        if result.get("success", False):
            print("✅ QUICK OPINION SUCCESS!")
            print(f"📊 Game Title: {result['game_title']}")

            quick_summary = result.get("quick_summary", {})
            print(f"⭐ Rating: {quick_summary.get('rating', 'N/A')}")
            print(f"🎯 Recommendation: {quick_summary.get('recommendation', 'N/A')}")
            print(f"🔍 Confidence: {quick_summary.get('confidence', 'N/A')}")
            print(f"💪 Key Strength: {quick_summary.get('key_strength', 'N/A')}")
            print(f"⚠️ Main Concern: {quick_summary.get('main_concern', 'N/A')}")
            print(f"👥 Target Audience: {quick_summary.get('target_audience', 'N/A')}")

            # One-liner summary
            one_liner = result.get("one_liner", "")
            if one_liner:
                print(f"\n📝 Quick Summary:")
                print(f"   {one_liner}")

            # Buy advice
            buy_advice = result.get("buy_advice", "")
            if buy_advice:
                print(f"\n💡 Buy Advice:")
                print(f"   {buy_advice}")

            return True
        else:
            print("❌ QUICK OPINION FAILED!")
            print(f"Error: {result.get('error', 'Unknown error')}")
            return False

    except Exception as e:
        print(f"❌ Exception during quick opinion test: {e}")
        return False


def test_games_comparison():
    """Test games comparison with full reviews."""
    print("\n" + "=" * 70)
    print("🆚 PHASE 3 PUNKT 1 - TEST GAMES COMPARISON")
    print("=" * 70)

    test_games = ["INSIDE", "Hollow Knight", "Celeste"]

    try:
        print(f"\n🆚 Testing games comparison for: {', '.join(test_games)}")
        print("-" * 50)

        # Generate comparison
        result = compare_games_with_reviews(test_games, comparison_focus="overall")

        if result.get("success", False):
            print("✅ GAMES COMPARISON SUCCESS!")
            print(f"🎮 Games Compared: {result.get('games_compared', 0)}")
            print(f"🎯 Comparison Focus: {result.get('comparison_focus', 'N/A')}")

            # Display winner
            winner = result.get("winner")
            if winner:
                summary = winner.get("quick_summary", {})
                print(f"\n🏆 WINNER: {winner['game_title']}")
                print(f"   Rating: {summary.get('rating', 'N/A')}")
                print(f"   Recommendation: {summary.get('recommendation', 'N/A')}")
                print(f"   Key Strength: {summary.get('key_strength', 'N/A')}")

            # Display ranking
            ranking = result.get("ranking", [])
            if ranking:
                print(f"\n📊 DETAILED RANKING:")
                for entry in ranking:
                    rank = entry.get("rank", "?")
                    title = entry.get("game_title", "Unknown")
                    rating = entry.get("rating", "N/A")
                    recommendation = entry.get("recommendation", "N/A")
                    why_rank = entry.get("why_this_rank", "No explanation")

                    print(f"   #{rank}. {title}")
                    print(f"       Rating: {rating} | Rec: {recommendation}")
                    print(f"       Why: {why_rank}")
                    print()

            # Display comparison summary
            comparison_summary = result.get("comparison_summary", "")
            if comparison_summary:
                print(f"📝 COMPARISON SUMMARY:")
                print(f"   {comparison_summary}")

            # Display failed games if any
            failed_games = result.get("failed_games", [])
            if failed_games:
                print(f"\n⚠️ Failed Games: {', '.join(failed_games)}")

            return True
        else:
            print("❌ GAMES COMPARISON FAILED!")
            print(f"Error: {result.get('error', 'Unknown error')}")
            failed_games = result.get("failed_games", [])
            if failed_games:
                print(f"Failed Games: {', '.join(failed_games)}")
            return False

    except Exception as e:
        print(f"❌ Exception during games comparison test: {e}")
        return False


def run_phase3_point1_tests():
    """Run all Phase 3 Point 1 tests."""
    print("🚀 STARTING PHASE 3 POINT 1 TESTS")
    print("Testing comprehensive review generation system...")
    print("=" * 70)

    results = []

    # Test 1: Comprehensive Review
    test1_result = test_comprehensive_review()
    results.append(("Comprehensive Review", test1_result))

    # Test 2: Quick Opinion
    test2_result = test_quick_opinion()
    results.append(("Quick Opinion", test2_result))

    # Test 3: Games Comparison
    test3_result = test_games_comparison()
    results.append(("Games Comparison", test3_result))

    # Test z losowymi deals
    random_deals = get_random_game_sample(5, "deals")
    test_games = random_deals["selected_games"]

    # Test z highest-rated games
    top_games = scrape_dekudeals_category("highest-rated", max_games=8)
    quality_test = top_games["game_titles"]

    # Test mieszany z różnych kategorii
    mixed_collection = get_games_from_popular_categories(
        3, ["hottest", "staff-picks", "deepest-discounts"]
    )
    diverse_test = mixed_collection["all_unique_titles"]

    # Summary
    print("\n" + "=" * 70)
    print("📊 PHASE 3 PUNKT 1 - TEST RESULTS SUMMARY")
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
        print("🎉 ALL PHASE 3 POINT 1 TESTS PASSED!")
        print("✅ Comprehensive review generation system is fully functional!")
    else:
        print("⚠️ Some tests failed. Check the output above for details.")

    return passed == total


if __name__ == "__main__":
    success = run_phase3_point1_tests()

    print("\n" + "=" * 70)
    print("🏁 PHASE 3 POINT 1 TESTING COMPLETE")
    print("=" * 70)

    if success:
        print("✅ Phase 3 Point 1 implementation is ready!")
        print("🎮 The comprehensive review generation system is working correctly.")
        print(
            "📝 Games can now receive detailed, structured reviews combining all analyses."
        )
    else:
        print("❌ Phase 3 Point 1 needs additional work.")
        print("🔧 Check the error messages above and fix any issues.")

    print(f"\n🎯 Ready for next development phase!")

#!/usr/bin/env python3

"""
Test Collection-Based Recommendations - Phase 7.3.2
===================================================

Tests the new collection-based recommendation system that generates
personalized game recommendations based on user's owned games collection.

Features tested:
- Collection preference analysis
- Similar game recommendations
- Discovery recommendations (new genres)
- Developer-based recommendations
- Complementary recommendations (fill gaps)
- ML integration with Smart User Profiler

Author: AutoGen DekuDeals Team
Version: 1.0.0
"""

import sys
import os
import time
from datetime import datetime
from pprint import pprint

# Add parent directory to path for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from agent_tools import (
    generate_collection_based_recommendations,
    add_game_to_collection,
    get_user_game_collection,
    update_game_in_collection,
)
from utils.collection_recommendation_engine import get_collection_recommendation_engine


def print_section(title: str, char: str = "="):
    """Print formatted section header."""
    print(f"\n{char * 60}")
    print(f"{title:^60}")
    print(f"{char * 60}")


def print_subsection(title: str):
    """Print formatted subsection header."""
    print(f"\n{'-' * 40}")
    print(f"📋 {title}")
    print(f"{'-' * 40}")


def setup_test_collection():
    """Set up a test collection with diverse games for recommendation testing."""
    print_section("🎮 Setting Up Test Collection")

    # Sample games with different genres, developers, and characteristics
    test_games = [
        # Indie puzzle games
        {
            "title": "Celeste",
            "rating": 9.5,
            "status": "completed",
            "notes": "Amazing platformer",
        },
        {
            "title": "The Witness",
            "rating": 8.0,
            "status": "owned",
            "notes": "Mind-bending puzzles",
        },
        # Action/Adventure games
        {
            "title": "Hades",
            "rating": 9.8,
            "status": "completed",
            "notes": "Perfect roguelike",
        },
        {
            "title": "Dead Cells",
            "rating": 8.5,
            "status": "owned",
            "notes": "Great metroidvania",
        },
        # Indie darlings
        {
            "title": "Hollow Knight",
            "rating": 9.2,
            "status": "completed",
            "notes": "Masterpiece metroidvania",
        },
        {
            "title": "Ori and the Blind Forest",
            "rating": 8.8,
            "status": "owned",
            "notes": "Beautiful platformer",
        },
        # Strategy/Simulation
        {
            "title": "Slay the Spire",
            "rating": 8.0,
            "status": "owned",
            "notes": "Addictive card game",
        },
        {
            "title": "Into the Breach",
            "rating": 7.5,
            "status": "wishlist",
            "notes": "Want to try",
        },
        # AAA games for variety
        {
            "title": "Breath of the Wild",
            "rating": 9.0,
            "status": "completed",
            "notes": "Open world perfection",
        },
        {
            "title": "Super Mario Odyssey",
            "rating": 8.5,
            "status": "owned",
            "notes": "Classic Nintendo fun",
        },
    ]

    added_count = 0
    for game in test_games:
        try:
            result = add_game_to_collection(
                title=game["title"],
                status=game["status"],
                user_rating=game["rating"],
                notes=game["notes"],
            )

            if result.get("success"):
                added_count += 1
                print(f"✅ Added: {game['title']} (Rating: {game['rating']}/10)")
            else:
                print(
                    f"ℹ️ Skipped: {game['title']} - {result.get('error', 'Unknown error')}"
                )

        except Exception as e:
            print(f"❌ Error adding {game['title']}: {e}")

    print(f"\n📊 Setup complete: {added_count}/{len(test_games)} games processed")
    return added_count > 0


def test_collection_analysis():
    """Test collection preference analysis."""
    print_section("🔍 Testing Collection Analysis")

    try:
        # Get collection recommendation engine
        engine = get_collection_recommendation_engine()

        # Analyze collection preferences
        print("Analyzing collection preferences...")
        preferences = engine.analyze_collection_preferences()

        print(f"\n📊 Collection Analysis Results:")
        print(f"   Collection Size: {preferences.collection_size} games")
        print(f"   Average Rating: {preferences.average_rating:.1f}/10")
        print(f"   Confidence Level: {preferences.confidence_level.value}")
        print(f"   Completion Rate: {preferences.completion_rate:.1%}")
        print(f"   Diversity Score: {preferences.diversity_score:.1%}")

        if preferences.favorite_genres:
            print(f"\n🎭 Favorite Genres:")
            for genre, score in preferences.favorite_genres[:5]:
                print(f"   • {genre}: {score:.2f}")

        if preferences.high_rated_games:
            print(f"\n⭐ High-Rated Games ({len(preferences.high_rated_games)}):")
            for game in preferences.high_rated_games[:5]:
                print(f"   • {game}")

        if preferences.underrepresented_genres:
            print(f"\n🔍 Underrepresented Genres:")
            for genre in preferences.underrepresented_genres[:3]:
                print(f"   • {genre}")

        return True

    except Exception as e:
        print(f"❌ Collection analysis failed: {e}")
        return False


def test_recommendation_type(rec_type: str, description: str):
    """Test a specific recommendation type."""
    print_subsection(f"{description} Recommendations")

    try:
        # Generate recommendations
        result = generate_collection_based_recommendations(
            recommendation_type=rec_type, max_recommendations=5
        )

        if not result.get("success"):
            print(f"❌ {rec_type} recommendations failed: {result.get('error')}")
            if "requirements" in result:
                req = result["requirements"]
                print(f"   Requirements: {req.get('needed', 'Unknown')}")
                print(
                    f"   Current collection: {req.get('current_collection_size', 0)} games"
                )
            return False

        recommendations = result.get("recommendations", [])
        summary = result.get("recommendation_summary", {})

        print(f"✅ Generated {len(recommendations)} {rec_type} recommendations")
        print(
            f"   Based on {summary.get('based_on_collection', {}).get('total_games', 0)} games in collection"
        )

        # Display top recommendations
        for i, rec in enumerate(recommendations[:3], 1):
            print(
                f"\n   {i}. {rec['game_title']} (Score: {rec['recommendation_score']:.1f})"
            )
            print(f"      Confidence: {rec['confidence']}")
            print(f"      Reason: {rec['primary_reason']}")

            if rec.get("genre_matches"):
                print(f"      Genre matches: {', '.join(rec['genre_matches'][:3])}")

            if rec.get("similar_owned_games"):
                print(f"      Similar to: {', '.join(rec['similar_owned_games'][:2])}")

        return True

    except Exception as e:
        print(f"❌ {rec_type} recommendations failed: {e}")
        return False


def test_all_recommendation_types():
    """Test all types of collection-based recommendations."""
    print_section("🎯 Testing Recommendation Types")

    recommendation_types = [
        ("similar", "Similar Games"),
        ("discovery", "Discovery"),
        ("developer", "Developer-Based"),
        ("complementary", "Complementary"),
    ]

    results = {}
    for rec_type, description in recommendation_types:
        results[rec_type] = test_recommendation_type(rec_type, description)
        time.sleep(0.5)  # Brief pause between tests

    # Summary
    print_subsection("📊 Recommendation Test Summary")
    successful = sum(results.values())
    total = len(results)

    for rec_type, success in results.items():
        status = "✅ PASS" if success else "❌ FAIL"
        print(f"   {rec_type.title():>12}: {status}")

    print(f"\n📈 Overall Success Rate: {successful}/{total} ({successful/total:.1%})")
    return successful == total


def test_collection_insights():
    """Test collection insights functionality."""
    print_section("💡 Testing Collection Insights")

    try:
        engine = get_collection_recommendation_engine()
        insights = engine.get_collection_insights()

        print("📊 Collection Insights:")

        # Collection summary
        summary = insights.get("collection_summary", {})
        print(f"\n   Collection Overview:")
        print(f"   • Total Games: {summary.get('total_games', 0)}")
        print(f"   • Average Rating: {summary.get('average_rating', 0):.1f}/10")
        print(f"   • Completion Rate: {summary.get('completion_rate', 0):.1f}%")
        print(f"   • Diversity Score: {summary.get('diversity_score', 0):.1f}%")
        print(f"   • Confidence: {summary.get('confidence_level', 'unknown')}")

        # Readiness for recommendations
        readiness = insights.get("recommendations_readiness", {})
        print(f"\n   Recommendation Readiness:")
        for rec_type, ready in readiness.items():
            status = "✅ Ready" if ready else "❌ Not Ready"
            print(f"   • {rec_type.title():>12}: {status}")

        # Genre preferences
        genre_prefs = insights.get("genre_preferences", {})
        favorites = genre_prefs.get("favorites", [])
        if favorites:
            print(f"\n   Top Genres:")
            for genre, score in favorites[:3]:
                print(f"   • {genre}: {score:.2f}")

        return True

    except Exception as e:
        print(f"❌ Collection insights failed: {e}")
        return False


def run_collection_recommendation_tests():
    """Run complete collection-based recommendation test suite."""
    print_section("🚀 Collection-Based Recommendation Tests", "=")
    print(f"Test started: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

    test_results = {}

    # Test 1: Setup test collection
    print_subsection("Test 1: Collection Setup")
    test_results["setup"] = setup_test_collection()

    if not test_results["setup"]:
        print("❌ Cannot proceed without test collection. Exiting.")
        return False

    # Test 2: Collection analysis
    print_subsection("Test 2: Collection Analysis")
    test_results["analysis"] = test_collection_analysis()

    # Test 3: Collection insights
    print_subsection("Test 3: Collection Insights")
    test_results["insights"] = test_collection_insights()

    # Test 4: All recommendation types
    print_subsection("Test 4: Recommendation Generation")
    test_results["recommendations"] = test_all_recommendation_types()

    # Final summary
    print_section("📊 FINAL TEST RESULTS", "=")

    total_tests = len(test_results)
    passed_tests = sum(test_results.values())

    for test_name, passed in test_results.items():
        status = "✅ PASS" if passed else "❌ FAIL"
        print(f"   {test_name.title():>15}: {status}")

    print(
        f"\n🎯 Overall Result: {passed_tests}/{total_tests} tests passed ({passed_tests/total_tests:.1%})"
    )

    if passed_tests == total_tests:
        print("🎉 All collection-based recommendation tests PASSED!")
        print(
            "\n✨ Phase 7.3.2 - Collection-Based Recommendations: READY FOR PRODUCTION!"
        )
    else:
        print(f"⚠️ {total_tests - passed_tests} test(s) failed. Review implementation.")

    print(f"\nTest completed: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    return passed_tests == total_tests


if __name__ == "__main__":
    print("🎮 AutoGen DekuDeals - Collection-Based Recommendation Tests")
    print("=" * 70)

    try:
        success = run_collection_recommendation_tests()
        exit_code = 0 if success else 1
        sys.exit(exit_code)

    except KeyboardInterrupt:
        print("\n\n⚠️ Tests interrupted by user")
        sys.exit(1)

    except Exception as e:
        print(f"\n\n❌ Unexpected error during testing: {e}")
        import traceback

        traceback.print_exc()
        sys.exit(1)

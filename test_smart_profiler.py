#!/usr/bin/env python3
"""
Test Script for Smart User Profiler
Tests the new ML intelligence features
"""

import json
import os
from pathlib import Path
from agent_tools import (
    get_smart_user_insights,
    get_personalized_game_recommendation,
    record_smart_interaction,
)


def check_stored_profile_data():
    """Check what profile data is stored on disk"""
    print("💾 Checking Stored Profile Data...")
    print("=" * 50)

    # Check for user profiles directory
    profiles_dir = Path("user_profiles")
    if profiles_dir.exists():
        print(f"✅ User profiles directory exists: {profiles_dir}")

        # List files in profiles directory
        files = list(profiles_dir.glob("*"))
        print(f"📁 Files in user_profiles: {len(files)}")
        for file in files:
            print(f"   • {file.name} ({file.stat().st_size} bytes)")

            # Try to read JSON files
            if file.suffix == ".json" and file.stat().st_size > 0:
                try:
                    with open(file, "r") as f:
                        data = json.load(f)
                    print(f"   📄 Content preview: {list(data.keys())}")
                except:
                    print(f"   ❌ Could not read {file.name}")
    else:
        print("❌ No user_profiles directory found")

    # Check analytics data
    analytics_dir = Path("analytics_data")
    if analytics_dir.exists():
        print(f"✅ Analytics directory exists: {analytics_dir}")
        files = list(analytics_dir.glob("*"))
        print(f"📁 Files in analytics_data: {len(files)}")
        for file in files:
            print(f"   • {file.name} ({file.stat().st_size} bytes)")
    else:
        print("❌ No analytics_data directory found")

    print("\n")


def test_user_insights():
    """Test smart user insights function"""
    print("🧠 Testing Smart User Insights...")
    print("=" * 50)

    result = get_smart_user_insights()

    if result.get("success"):
        print("✅ Smart User Insights - SUCCESS")

        user_profile = result.get("user_profile")
        if user_profile:
            print(f"👤 User ID: {user_profile['user_id']}")
            print(f"🎯 Confidence Level: {user_profile['confidence_level']}")
            print(f"📊 Total Interactions: {user_profile['total_interactions']}")

            detected_patterns = user_profile.get("detected_patterns", [])
            print(f"🔍 Detected Patterns ({len(detected_patterns)}):")
            for pattern in detected_patterns:
                print(
                    f"   • {pattern['pattern']}: {pattern['confidence']:.3f} confidence"
                )
                print(
                    f"     Evidence: {pattern['evidence'][0] if pattern['evidence'] else 'None'}"
                )

            favorite_genres = user_profile.get("favorite_genres", [])
            print(f"🎮 Favorite Genres ({len(favorite_genres)}):")
            for genre in favorite_genres:
                print(f"   • {genre['genre']}: {genre['confidence']:.3f} confidence")
        else:
            print("ℹ️ No user profile data yet")
            print(f"💡 Message: {result.get('message', 'No message')}")
    else:
        print("❌ Smart User Insights - FAILED")
        print(f"Error: {result.get('error', 'Unknown error')}")

    print("\n")


def test_record_interaction():
    """Test recording interactions to build profile"""
    print("📝 Testing Interaction Recording...")
    print("=" * 50)

    # Create sample game data and record interaction
    sample_game_data = {
        "success": True,
        "title": "Test Puzzle Game",
        "current_eshop_price": "$12.99",
        "MSRP": "$19.99",
        "metacritic_score": "82",
        "opencritic_score": "80",
        "genres": ["Puzzle", "Indie"],
        "developer": "Test Studio",
        "platform": "Nintendo Switch",
        "source_url": "https://test.com",
    }

    result = record_smart_interaction("Test Puzzle Game", sample_game_data, "analyzed")

    if result.get("success"):
        print("✅ Interaction Recording - SUCCESS")
        print(f"📝 Interaction ID: {result.get('interaction_id', 'N/A')}")

        profile_update = result.get("profile_update", {})
        print(f"📊 Total Interactions: {profile_update.get('total_interactions', 0)}")
        print(
            f"🎯 Confidence Level: {profile_update.get('confidence_level', 'unknown')}"
        )
        print(f"🔍 Patterns Detected: {profile_update.get('patterns_detected', 0)}")

        insights = result.get("insights", [])
        if insights:
            print("💡 Insights:")
            for insight in insights:
                print(f"   • {insight}")
    else:
        print("❌ Interaction Recording - FAILED")
        print(f"Error: {result.get('error', 'Unknown error')}")

    print("\n")


def test_personalized_recommendation():
    """Test personalized recommendations"""
    print("🎯 Testing Personalized Recommendations...")
    print("=" * 50)

    # Create sample game data (puzzle game) - must have success flag
    sample_game_data = {
        "success": True,  # Required for analysis
        "title": "Sample Puzzle Game",
        "current_eshop_price": "$15.99",
        "MSRP": "$19.99",
        "metacritic_score": "85",
        "opencritic_score": "83",
        "genres": ["Puzzle", "Indie"],
        "developer": "Indie Studio",
        "platform": "Nintendo Switch",
        "source_url": "https://sample.com",
    }

    result = get_personalized_game_recommendation(sample_game_data)

    if result.get("success"):
        print("✅ Personalized Recommendation - SUCCESS")

        recommendation = result.get("recommendation", {})
        print(f"🎯 Personalized: {result.get('personalized', False)}")
        print(f"📊 Score: {recommendation.get('score', 'N/A')}")
        print(f"📈 Base Score: {recommendation.get('base_score', 'N/A')}")
        print(f"🎪 Recommendation: {recommendation.get('recommendation_level', 'N/A')}")
        print(f"💭 Reasoning: {recommendation.get('reasoning', 'N/A')}")

        detected_patterns = recommendation.get("detected_patterns", [])
        if detected_patterns:
            print(f"🔍 Applied Patterns: {', '.join(detected_patterns)}")

        personalization_applied = result.get("personalization_applied", {})
        if personalization_applied:
            print("⚙️ Personalization Applied:")
            for key, value in personalization_applied.items():
                if value > 0:
                    print(f"   • {key}: {value}")
    else:
        print("❌ Personalized Recommendation - FAILED")
        print(f"Error: {result.get('error', 'Unknown error')}")

    print("\n")


if __name__ == "__main__":
    print("🎮 AutoGen DekuDeals - Smart User Profiler Test")
    print("=" * 60)
    print()

    # Check stored data first
    check_stored_profile_data()

    # Test functions
    test_record_interaction()  # Test recording first
    test_user_insights()  # Then check insights
    test_personalized_recommendation()

    print("🎯 Test completed!")

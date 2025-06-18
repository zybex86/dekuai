#!/usr/bin/env python3
"""
Test Multiple Interactions for Smart User Profiler
Tests pattern detection with 3+ interactions
"""

from agent_tools import record_smart_interaction, get_smart_user_insights


def test_multiple_interactions():
    """Test with multiple interactions to trigger pattern detection"""
    print("🧠 Testing Multiple Interactions for Pattern Detection...")
    print("=" * 60)

    # Game 1: Puzzle game
    game1 = {
        "success": True,
        "title": "Tetris Effect: Connected",
        "current_eshop_price": "$39.99",
        "MSRP": "$39.99",
        "metacritic_score": "94",
        "opencritic_score": "89",
        "genres": ["Puzzle", "Music"],
        "developer": "Monstars Inc.",
        "platform": "Nintendo Switch",
    }

    # Game 2: Another puzzle game
    game2 = {
        "success": True,
        "title": "Portal 2",
        "current_eshop_price": "$19.99",
        "MSRP": "$19.99",
        "metacritic_score": "88",
        "opencritic_score": "90",
        "genres": ["Puzzle", "Action"],
        "developer": "Valve",
        "platform": "Nintendo Switch",
    }

    # Game 3: Indie puzzle game
    game3 = {
        "success": True,
        "title": "The Witness",
        "current_eshop_price": "$14.99",
        "MSRP": "$39.99",
        "metacritic_score": "87",
        "opencritic_score": "85",
        "genres": ["Puzzle", "Indie"],
        "developer": "Thekla Inc.",
        "platform": "Nintendo Switch",
    }

    games = [
        ("Tetris Effect: Connected", game1),
        ("Portal 2", game2),
        ("The Witness", game3),
    ]

    # Record multiple interactions
    for i, (game_name, game_data) in enumerate(games, 1):
        print(f"\n📝 Recording Interaction {i}: {game_name}")
        result = record_smart_interaction(game_name, game_data, "analyzed")

        if result.get("success"):
            profile_update = result.get("profile_update", {})
            print(
                f"   ✅ Success - Total interactions: {profile_update.get('total_interactions', 0)}"
            )
            print(
                f"   🎯 Confidence: {profile_update.get('confidence_level', 'unknown')}"
            )
            print(f"   🔍 Patterns: {profile_update.get('patterns_detected', 0)}")

            insights = result.get("insights", [])
            if insights:
                for insight in insights:
                    print(f"   💡 {insight}")
        else:
            print(f"   ❌ Failed: {result.get('error', 'Unknown error')}")

    print("\n" + "=" * 60)
    print("🧠 Getting Final User Insights...")

    # Get final insights
    insights_result = get_smart_user_insights()

    if insights_result.get("success"):
        user_profile = insights_result.get("user_profile")
        if user_profile:
            print("✅ USER PROFILE CREATED!")
            print(f"👤 User ID: {user_profile['user_id']}")
            print(f"📊 Total Interactions: {user_profile['total_interactions']}")
            print(f"🎯 Confidence Level: {user_profile['confidence_level']}")

            detected_patterns = user_profile.get("detected_patterns", [])
            print(f"🔍 Detected Patterns ({len(detected_patterns)}):")
            for pattern in detected_patterns:
                print(
                    f"   • {pattern['pattern']}: {pattern['confidence']:.3f} confidence"
                )
                if pattern["evidence"]:
                    print(f"     Evidence: {pattern['evidence'][0]}")

            favorite_genres = user_profile.get("favorite_genres", [])
            print(f"🎮 Favorite Genres ({len(favorite_genres)}):")
            for genre in favorite_genres:
                print(f"   • {genre['genre']}: {genre['confidence']:.3f} confidence")

        else:
            print("❌ No user profile available")
    else:
        print(f"❌ Error getting insights: {insights_result.get('error', 'Unknown')}")


if __name__ == "__main__":
    test_multiple_interactions()
    print("\n🎯 Test completed!")

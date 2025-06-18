#!/usr/bin/env python3
"""
Test Personalized Recommendations with Learned Profile
Tests ML-powered recommendations using detected patterns
"""

from agent_tools import get_personalized_game_recommendation


def test_personalized_recommendations():
    """Test personalized recommendations with learned user profile"""
    print("🎯 Testing ML-Powered Personalized Recommendations!")
    print("=" * 55)

    # Test with a puzzle game (should get personalized boost)
    puzzle_game = {
        "success": True,
        "title": "New Puzzle Game",
        "current_eshop_price": "$16.99",
        "MSRP": "$24.99",
        "metacritic_score": "88",
        "opencritic_score": "85",
        "genres": ["Puzzle", "Indie"],
        "developer": "Indie Studio",
        "platform": "Nintendo Switch",
    }

    print("🧩 Testing with PUZZLE GAME (should match user preferences):")
    print(f"   Game: {puzzle_game['title']}")
    print(f"   Price: {puzzle_game['current_eshop_price']} (was {puzzle_game['MSRP']})")
    print(f"   Score: {puzzle_game['metacritic_score']}")
    print(f"   Genres: {puzzle_game['genres']}")
    print()

    result = get_personalized_game_recommendation(puzzle_game)

    if result.get("success"):
        rec = result["recommendation"]
        print("✅ RECOMMENDATION SUCCESS!")
        print(f"🧠 PERSONALIZED: {result.get('personalized', False)}")
        print(f"📊 Final Score: {rec.get('score', 'N/A')}")
        print(f"📈 Base Score: {rec.get('base_score', 'N/A')}")
        print(f"🎪 Recommendation: {rec.get('recommendation_level', 'N/A')}")
        print(f"🎯 Confidence: {rec.get('confidence', 'N/A')}")
        print(f"💭 Reasoning: {rec.get('reasoning', 'N/A')}")

        patterns = rec.get("detected_patterns", [])
        if patterns:
            print(f"🔍 Applied Patterns: {', '.join(patterns)}")

        personalization = result.get("personalization_applied", {})
        if personalization:
            print("⚙️ Personalization Applied:")
            for key, value in personalization.items():
                if value > 0:
                    print(f"   • {key}: {value}")
    else:
        print(f"❌ Error: {result.get('error', 'Unknown error')}")


if __name__ == "__main__":
    test_personalized_recommendations()
    print("\n🎯 Personalized recommendation test completed!")

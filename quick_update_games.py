#!/usr/bin/env python3
"""
Quick Game Update Script

Use this script to quickly update multiple games in your collection with ratings and tags.
This will enable better collection-based recommendations.
"""

import sys
from pathlib import Path

# Add current directory to path
sys.path.insert(0, str(Path(__file__).parent))


def main():
    print("⚡ QUICK GAME UPDATE SCRIPT")
    print("=" * 40)

    try:
        from utils.collection_updater import get_collection_updater

        updater = get_collection_updater()
        print("✅ Collection updater ready")
        print()

        # Batch of common games with suggested ratings and tags
        # Adjust ratings based on your personal preferences (1.0-10.0)
        games_to_update = {
            "Minecraft": {
                "user_rating": 9.0,
                "tags": ["Simulation", "Survival", "Indie", "Creative"],
            },
            "Mario + Rabbids Kingdom Battle": {
                "user_rating": 7.5,
                "tags": ["Strategy", "Adventure", "Nintendo", "Turn-Based"],
            },
            "Overcooked! All You Can Eat": {
                "user_rating": 8.0,
                "tags": ["Party", "Simulation", "Co-op", "Arcade"],
            },
            "SteamWorld Dig": {
                "user_rating": 8.0,
                "tags": ["Platformer", "Adventure", "Indie", "Metroidvania"],
            },
            "SteamWorld Dig 2": {
                "user_rating": 8.5,
                "tags": ["Platformer", "Adventure", "Indie", "Metroidvania"],
            },
            "Rayman Legends Definitive Edition": {
                "user_rating": 8.5,
                "tags": ["Platformer", "Adventure", "Family", "Arcade"],
            },
            "Trine Enchanted Edition": {
                "user_rating": 7.5,
                "tags": ["Platformer", "Adventure", "Co-op", "Fantasy"],
            },
            "FINAL FANTASY XV POCKET EDITION HD": {
                "user_rating": 7.0,
                "tags": ["RPG", "Adventure", "JRPG", "Fantasy"],
            },
            "Wargroove": {
                "user_rating": 8.0,
                "tags": ["Strategy", "Fantasy", "Indie", "Turn-Based"],
            },
            "Moonlighter": {
                "user_rating": 7.5,
                "tags": ["RPG", "Simulation", "Indie", "Action"],
            },
        }

        print(f"🎮 Updating {len(games_to_update)} games...")
        print()

        success_count = 0
        error_count = 0

        for game_title, updates in games_to_update.items():
            print(f"   Updating '{game_title}'...")

            success, message = updater.update_game(game_title, updates)

            if success:
                print(f"   ✅ {message}")
                print(f"      Rating: {updates['user_rating']}/10")
                print(f"      Tags: {', '.join(updates['tags'])}")
                success_count += 1
            else:
                print(f"   ❌ Failed: {message}")
                error_count += 1
            print()

        print("=" * 40)
        print(f"📊 BATCH UPDATE RESULTS:")
        print(f"   ✅ Successful updates: {success_count}")
        print(f"   ❌ Failed updates: {error_count}")
        print()

        # Check collection status after updates
        print("📈 UPDATED COLLECTION STATUS:")
        summary = updater.view_collection_summary()
        print(f"   Total Games: {summary['total_games']}")
        print(f"   Rated Games: {summary['rated_games']}")
        print(f"   Tagged Games: {summary['tagged_games']}")
        print(f"   Completion: {summary['completion_percentage']}%")
        print(
            f"   Recommendation Ready: {'✅ Yes' if summary['recommendation_ready'] else '❌ No'}"
        )
        print()

        # Test recommendations
        if summary["recommendation_ready"]:
            print("🎯 TESTING RECOMMENDATIONS:")
            print("   Your collection is ready! Let's test recommendations...")

            try:
                from agent_tools import generate_collection_based_recommendations

                # Test similar recommendations
                result = generate_collection_based_recommendations("similar", 3)

                if result.get("success"):
                    recommendations = result.get("recommendations", [])
                    print(
                        f"   ✅ Generated {len(recommendations)} similar game recommendations!"
                    )

                    for i, rec in enumerate(recommendations[:3], 1):
                        title = rec.get("title", "Unknown")
                        score = rec.get("score", {}).get("final_score", 0)
                        print(f"      {i}. {title} (Score: {score:.1f})")
                else:
                    error = result.get("error", "Unknown error")
                    print(f"   ⚠️  Recommendations still need work: {error}")

            except Exception as e:
                print(f"   ⚠️  Recommendation test failed: {e}")

        print()
        print("🎉 Quick update complete!")
        print()
        print("✨ What's Next:")
        print("1. Your collection now has much more data for recommendations")
        print("2. Try: generate_collection_based_recommendations('similar', 5)")
        print("3. Or try other types: 'discovery', 'developer', 'complementary'")
        print("4. Add more ratings and tags to improve recommendation quality")

    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback

        traceback.print_exc()


if __name__ == "__main__":
    main()

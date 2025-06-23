#!/usr/bin/env python3
"""
Simple Collection Management Test

Direct test of collection management functionality without AutoGen decorators.
This will help you update your games with ratings and tags to enable recommendations.
"""

import json
import sys
from pathlib import Path

# Add current directory to path
sys.path.insert(0, str(Path(__file__).parent))


def main():
    print("🎮 COLLECTION MANAGEMENT - DIRECT TEST")
    print("=" * 60)

    try:
        # Import collection updater directly
        from utils.collection_updater import get_collection_updater

        updater = get_collection_updater()
        print("✅ Collection updater loaded successfully")
        print()

        # Step 1: View current collection status
        print("📊 STEP 1: Current Collection Status")
        print("-" * 40)

        summary = updater.view_collection_summary()
        print(f"   Total Games: {summary['total_games']}")
        print(f"   Rated Games: {summary['rated_games']}")
        print(f"   Tagged Games: {summary['tagged_games']}")
        print(f"   Complete Games: {summary['complete_games']}")
        print(f"   Completion: {summary['completion_percentage']}%")
        print(
            f"   Recommendation Ready: {'✅ Yes' if summary['recommendation_ready'] else '❌ No'}"
        )
        print()

        # Step 2: Get improvement suggestions
        print("💡 STEP 2: Improvement Suggestions")
        print("-" * 40)

        suggestions = updater.auto_suggest_improvements()
        print(f"   Games needing ratings: {len(suggestions['missing_ratings'])}")
        print(f"   Games needing tags: {len(suggestions['missing_tags'])}")
        print(f"   Priority games: {len(suggestions['priority_games'])}")

        if suggestions["priority_games"]:
            print(f"\n   🎯 Priority Games to Update First:")
            for game in suggestions["priority_games"][:5]:
                print(f"      - {game}")

        if suggestions["completion_tips"]:
            print(f"\n   📝 Tips:")
            for tip in suggestions["completion_tips"]:
                print(f"      • {tip}")
        print()

        # Step 3: Show some games that need updating
        print("🎮 STEP 3: Games That Need Updating")
        print("-" * 40)

        games = updater.list_games(limit=50)
        print(f"   Showing {len(games)} games:")
        print()

        for game in games:
            status = game["completion_status"]
            rating = game["user_rating"] if game["user_rating"] else "No rating"
            tags = ", ".join(game["tags"]) if game["tags"] else "No tags"

            status_icon = {"Complete": "✅", "Partial": "⚠️", "Empty": "❌"}.get(
                status, "❓"
            )

            print(f"   {status_icon} {game['title']}")
            print(f"      Rating: {rating} | Tags: {tags}")

            # Show suggested genres for empty games
            if status == "Empty":
                suggested = suggestions["suggested_tags"].get(game["title"], [])
                if suggested:
                    print(f"      💡 Suggested: {', '.join(suggested[:3])}")
            print()

        # Step 4: Demonstrate updating a game
        print("⚡ STEP 4: Demo - Update Bastion")
        print("-" * 40)

        demo_game = "Bastion"
        demo_rating = 8.5
        demo_tags = ["Action", "RPG", "Indie"]

        print(
            f"   Updating '{demo_game}' with rating {demo_rating} and tags {demo_tags}..."
        )

        success, message = updater.update_game(
            demo_game, {"user_rating": demo_rating, "tags": demo_tags}
        )

        if success:
            print(f"   ✅ {message}")
            updated_details = updater.get_game_details(demo_game)
            if updated_details:
                print(f"      Rating: {updated_details['user_rating']}/10")
                print(f"      Tags: {', '.join(updated_details['tags'])}")
                print(f"      Status: {updated_details['completion_status']}")
        else:
            print(f"   ❌ Update failed: {message}")
        print()

        # Step 5: Validate collection readiness
        print("🔍 STEP 5: Check Recommendation Readiness")
        print("-" * 40)

        validation = updater.validate_collection_for_recommendations()

        print(f"   Overall Ready: {'✅ Yes' if validation.get('ready') else '❌ No'}")
        print(f"   Collection Size: {validation.get('collection_size')} games")
        print(f"   Confidence Level: {validation.get('confidence_level')}")
        print()
        print("   Recommendation Types:")

        recommendations = validation.get("recommendations", {})
        for rec_type, status in recommendations.items():
            print(f"      {rec_type.title():>12}: {status}")
        print()

        # Step 6: Provide action plan
        print("📋 STEP 6: Action Plan")
        print("-" * 25)

        print("   To enable recommendations, update more games:")
        print()

        if summary["rated_games"] < 5:
            needed_ratings = 5 - summary["rated_games"]
            print(f"   1. ⭐ Add ratings to {needed_ratings} more games")
            print(
                "      Example: updater.update_game('Minecraft', {'user_rating': 9.0})"
            )

        if summary["tagged_games"] < 5:
            needed_tags = 5 - summary["tagged_games"]
            print(f"   2. 🏷️  Add tags to {needed_tags} more games")
            print(
                "      Example: updater.update_game('Overcooked', {'tags': ['Party', 'Simulation']})"
            )

        print()
        print("   📖 Quick update examples:")
        print("   # Update Mario + Rabbids")
        print("   updater.update_game('Mario + Rabbids Kingdom Battle', {")
        print("       'user_rating': 7.5,")
        print("       'tags': ['Strategy', 'Adventure', 'Nintendo']")
        print("   })")
        print()
        print("   # Update Minecraft")
        print("   updater.update_game('Minecraft', {")
        print("       'user_rating': 9.0,")
        print("       'tags': ['Simulation', 'Survival', 'Indie']")
        print("   })")
        print()
        print("   # Update SteamWorld Dig")
        print("   updater.update_game('SteamWorld Dig', {")
        print("       'user_rating': 8.0,")
        print("       'tags': ['Platformer', 'Adventure', 'Indie']")
        print("   })")

        print()
        print("🎉 Collection Management Test Complete!")
        print()
        print("✨ Next Steps:")
        print("1. Use the update examples above to add ratings and tags")
        print("2. Run this script again to check progress")
        print("3. Once you have 5+ rated and tagged games, recommendations will work!")
        print("4. Test with: generate_collection_based_recommendations('similar', 5)")

    except ImportError as e:
        print(f"❌ Import Error: {e}")
        print("Make sure you're running this from the correct directory")
    except Exception as e:
        print(f"❌ Unexpected Error: {e}")
        import traceback

        traceback.print_exc()


if __name__ == "__main__":
    main()

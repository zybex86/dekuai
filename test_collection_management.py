#!/usr/bin/env python3
"""
Collection Management Demo Script

This script demonstrates how to use the collection management tools to:
1. View your current collection status
2. Get improvement suggestions
3. Update games with ratings and tags
4. Validate collection readiness for recommendations

Run this to fix your collection and enable recommendations!
"""

import json
import sys
from pathlib import Path

# Add current directory to path
sys.path.insert(0, str(Path(__file__).parent))


def main():
    print("🎮 COLLECTION MANAGEMENT DEMO")
    print("=" * 60)

    try:
        # Import the collection management functions
        from agent_tools import (
            view_collection_summary,
            list_collection_games,
            get_collection_improvement_suggestions,
            update_collection_game,
            quick_game_update,
            validate_collection_readiness,
        )

        print("✅ Successfully imported collection management tools")
        print()

        # Step 1: View current collection status
        print("📊 STEP 1: Current Collection Status")
        print("-" * 40)

        summary_result = view_collection_summary()
        if summary_result.get("success"):
            summary = summary_result["collection_summary"]
            print(f"   Total Games: {summary['total_games']}")
            print(f"   Rated Games: {summary['rated_games']}")
            print(f"   Tagged Games: {summary['tagged_games']}")
            print(f"   Complete Games: {summary['complete_games']}")
            print(f"   Completion: {summary['completion_percentage']}%")
            print(
                f"   Recommendation Ready: {'✅ Yes' if summary['recommendation_ready'] else '❌ No'}"
            )
        else:
            print(f"   ❌ Error: {summary_result.get('error')}")

        print()

        # Step 2: Get improvement suggestions
        print("💡 STEP 2: Improvement Suggestions")
        print("-" * 40)

        suggestions_result = get_collection_improvement_suggestions()
        if suggestions_result.get("success"):
            suggestions = suggestions_result["suggestions"]
            summary = suggestions_result["summary"]

            print(f"   Games needing ratings: {summary['games_needing_ratings']}")
            print(f"   Games needing tags: {summary['games_needing_tags']}")
            print(f"   Priority games: {summary['priority_games']}")

            if suggestions["priority_games"]:
                print(f"\n   🎯 Priority Games to Update First:")
                for game in suggestions["priority_games"][:5]:
                    print(f"      - {game}")

            if suggestions["completion_tips"]:
                print(f"\n   📝 Tips:")
                for tip in suggestions["completion_tips"]:
                    print(f"      • {tip}")
        else:
            print(f"   ❌ Error: {suggestions_result.get('error')}")

        print()

        # Step 3: Show some games that need updating
        print("🎮 STEP 3: Games That Need Updating")
        print("-" * 40)

        games_result = list_collection_games(limit=10)
        if games_result.get("success"):
            games = games_result["games"]
            print(f"   Showing {len(games)} games (showing completion status):")
            print()

            for game in games[:8]:  # Show first 8 games
                status = game["completion_status"]
                rating = game["user_rating"] if game["user_rating"] else "No rating"
                tags = ", ".join(game["tags"]) if game["tags"] else "No tags"

                status_icon = {"Complete": "✅", "Partial": "⚠️", "Empty": "❌"}.get(
                    status, "❓"
                )

                print(f"   {status_icon} {game['title']}")
                print(f"      Rating: {rating} | Tags: {tags}")
                print(f"      Status: {status}")

                # Show suggested genres for empty games
                if status == "Empty" and suggestions_result.get("success"):
                    suggested = suggestions_result["suggestions"]["suggested_tags"].get(
                        game["title"], []
                    )
                    if suggested:
                        print(f"      💡 Suggested genres: {', '.join(suggested[:3])}")
                print()
        else:
            print(f"   ❌ Error: {games_result.get('error')}")

        # Step 4: Demonstrate updating a game
        print("⚡ STEP 4: Demo - Update a Game")
        print("-" * 40)

        # Try to update Bastion (popular game from the collection)
        demo_game = "Bastion"
        demo_rating = 8.5
        demo_tags = "Action,RPG,Indie"

        print(
            f"   Updating '{demo_game}' with rating {demo_rating} and tags '{demo_tags}'..."
        )

        update_result = quick_game_update(demo_game, demo_rating, demo_tags)
        if update_result.get("success"):
            print(f"   ✅ Successfully updated '{demo_game}'!")
            print(f"      Rating: {update_result['rating_added']}/10")
            print(f"      Tags: {', '.join(update_result['tags_added'])}")
            print(f"      Completion Status: {update_result['completion_status']}")
        else:
            print(f"   ❌ Update failed: {update_result.get('error')}")

        print()

        # Step 5: Validate collection readiness
        print("🔍 STEP 5: Check Recommendation Readiness")
        print("-" * 40)

        validation_result = validate_collection_readiness()
        if validation_result.get("success"):
            validation = validation_result["validation_results"]

            print(
                f"   Overall Ready: {'✅ Yes' if validation_result['overall_ready'] else '❌ No'}"
            )
            print(f"   Collection Size: {validation_result['collection_size']} games")
            print(f"   Confidence Level: {validation_result['confidence_level']}")
            print()
            print("   Recommendation Types:")

            for rec_type, status in validation["recommendations"].items():
                print(f"      {rec_type.title():>12}: {status}")
        else:
            print(f"   ❌ Error: {validation_result.get('error')}")

        print()

        # Step 6: Provide action plan
        print("📋 STEP 6: Action Plan to Enable Recommendations")
        print("-" * 50)

        if summary_result.get("success") and suggestions_result.get("success"):
            summary = summary_result["collection_summary"]
            suggestions = suggestions_result["suggestions"]

            print("   To enable collection-based recommendations:")
            print()

            if summary["rated_games"] < 5:
                needed_ratings = 5 - summary["rated_games"]
                print(f"   1. ⭐ Add ratings to {needed_ratings} more games")
                if suggestions["priority_games"]:
                    print(
                        f"      Start with: {', '.join(suggestions['priority_games'][:3])}"
                    )
                print()

            if summary["tagged_games"] < 5:
                needed_tags = 5 - summary["tagged_games"]
                print(f"   2. 🏷️  Add genre tags to {needed_tags} more games")
                print("      Example tags: Action, Adventure, RPG, Platformer, Indie")
                print()

            print("   3. 🚀 Use these functions to update your games:")
            print("      • quick_game_update('Game Title', 8.5, 'Action,RPG')")
            print(
                "      • update_collection_game('Game Title', user_rating=8.0, tags='Indie,Puzzle')"
            )
            print()

            print("   4. 📊 Check progress with:")
            print("      • validate_collection_readiness()")
            print("      • view_collection_summary()")

        print()
        print("🎉 Collection Management Demo Complete!")
        print()
        print("Next steps:")
        print("1. Use the functions above to add ratings and tags to your games")
        print("2. Focus on the priority games first")
        print("3. Run validate_collection_readiness() to check progress")
        print("4. Once ready, try generate_collection_based_recommendations()")

    except ImportError as e:
        print(f"❌ Import Error: {e}")
        print("Make sure you're running this from the correct directory")
    except Exception as e:
        print(f"❌ Unexpected Error: {e}")
        import traceback

        traceback.print_exc()


if __name__ == "__main__":
    main()

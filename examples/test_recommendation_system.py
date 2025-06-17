"""
Test Recommendation System - Phase 2 Point 3
Test systemu rekomendacji - Faza 2 Punkt 3

This example tests the recommendation system including:
- Personalized recommendations for different user types
- Game comparison for specific users
- Multi-user analysis for games
- User preference profiles

Ten przykład testuje system rekomendacji.
"""

import os
import sys

# Add parent directory to Python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from agent_tools import (
    generate_personalized_recommendations,
    compare_games_for_user,
    get_recommendation_insights,
)
import json


def test_personalized_recommendations() -> None:
    """Testuje spersonalizowane rekomendacje dla różnych typów użytkowników."""
    print("🎯 Testing Personalized Recommendations")
    print("=" * 80)

    # Test games list
    test_games = [
        "Slay the Spire",
        "Mario Kart 8 Deluxe",
        "Super Smash Bros. Ultimate",
        "The Legend of Zelda: Tears of the Kingdom",
        "Animal Crossing: New Horizons",
        "Baten Kaitos I & II HD Remaster",
        "Teenage Mutant Ninja Turtles: Shredder's Revenge",
        "Sonic Frontiers",
        "Street Fighter 6",
        "Ace Attorney Investigations",
        "Deltarune",
        "The Legend of Zelda: Breath of the Wild",
        "Mario & Luigi: Brothership",
        "Super Mario Odyssey",
        "MARIO + RABBIDS SPARKS OF HOPE",
        "Super Mario 3D Land",
        "WarioWare: Touched!",
        "Xenoblade Chronicles 3",
        "Atelier Ryza: Ever Darkness & the Secret Hideout",
    ]

    # Test different user preferences
    user_types = ["bargain_hunter", "quality_seeker", "indie_lover", "casual_player"]

    for user_type in user_types:
        print(
            f"\n👤 Testing recommendations for: {user_type.replace('_', ' ').title()}"
        )
        print("-" * 60)

        try:
            result = generate_personalized_recommendations(
                games_list=test_games, user_preference=user_type, max_recommendations=3
            )

            if result.get("success", False):
                # Display user profile
                profile = result.get("user_profile", {})
                print(f"📋 User Profile:")
                print(f"  🎯 Primary Preference: {profile.get('primary_preference')}")
                print(
                    f"  🏷️ Preferred Genres: {', '.join(profile.get('preferred_genres', []))}"
                )
                print(f"  💰 Budget Range: {profile.get('budget_range')}")
                print(f"  ⭐ Minimum Score: {profile.get('minimum_score')}")

                # Display statistics
                stats = result.get("statistics", {})
                print(f"\n📊 Statistics:")
                print(
                    f"  📈 Games Processed: {stats.get('successfully_processed')}/{stats.get('total_games_requested')}"
                )
                print(f"  🎯 Recommendations: {stats.get('recommendations_generated')}")

                # Display recommendations
                recommendations = result.get("recommendations", [])
                print(f"\n🏆 Top Recommendations:")

                for i, rec in enumerate(recommendations, 1):
                    print(f"\n  {i}. 🎮 {rec['game_title']}")
                    print(f"     📊 Score: {rec['recommendation_score']:.1f}/100")
                    print(f"     🎯 Match: {rec['match_percentage']:.0f}%")
                    print(f"     💡 Primary Reason: {rec['primary_reason']}")
                    print(f"     💌 Message: {rec['personalized_message']}")

                    if rec["reasons"]:
                        print(f"     ✅ Reasons: {'; '.join(rec['reasons'][:2])}")

                    if rec["warnings"]:
                        print(f"     ⚠️ Warnings: {'; '.join(rec['warnings'])}")

                # Summary
                summary = result.get("recommendation_summary", "")
                print(f"\n📝 Summary: {summary}")

            else:
                print(f"❌ Failed: {result.get('error', 'Unknown error')}")

        except Exception as e:
            print(f"❌ Error testing {user_type}: {e}")


def test_game_comparison() -> None:
    """Testuje porównanie gier dla konkretnego użytkownika."""
    print("\n🆚 Testing Game Comparison")
    print("=" * 80)

    comparison_games = [
        "Hollow Knight",
        "Celeste",
        "INSIDE",
        "Death's Door",
        "Slay the Spire",
        "Mario Kart 8 Deluxe",
        "Super Smash Bros. Ultimate",
        "The Legend of Zelda: Tears of the Kingdom",
        "Animal Crossing: New Horizons",
        "Baten Kaitos I & II HD Remaster",
        "Teenage Mutant Ninja Turtles: Shredder's Revenge",
        "Sonic Frontiers",
        "Street Fighter 6",
        "Ace Attorney Investigations",
        "Deltarune",
        "The Legend of Zelda: Breath of the Wild",
        "Mario & Luigi: Brothership",
        "Super Mario Odyssey",
        "MARIO + RABBIDS SPARKS OF HOPE",
        "Super Mario 3D Land",
        "WarioWare: Touched!",
        "Xenoblade Chronicles 3",
        "Atelier Ryza: Ever Darkness & the Secret Hideout",
    ]

    user_preference = "indie_lover"

    print(f"👤 Comparing games for: {user_preference.replace('_', ' ').title()}")
    print(f"🎮 Games: {', '.join(comparison_games)}")
    print("-" * 60)

    try:
        result = compare_games_for_user(comparison_games, user_preference)

        if result.get("success", False):
            print(f"📊 Comparison Type: {result.get('comparison_type')}")
            print(f"🎯 Games Compared: {result.get('games_compared')}")

            # Best and worst choices
            best_choice = result.get("best_choice", {})
            worst_choice = result.get("worst_choice", {})

            if best_choice:
                print(f"\n🏆 Best Choice: {best_choice['game']}")
                print(f"   📊 Score: {best_choice['score']:.1f}/100")
                print(f"   💌 {best_choice['message']}")

            if worst_choice:
                print(f"\n🔻 Worst Choice: {worst_choice['game']}")
                print(f"   📊 Score: {worst_choice['score']:.1f}/100")
                if worst_choice.get("reasons"):
                    print(f"   ⚠️ Issues: {'; '.join(worst_choice['reasons'])}")

            # Detailed ranking
            ranking = result.get("ranking", [])
            print(f"\n📈 Detailed Ranking:")

            for entry in ranking:
                rank = entry["rank"]
                title = entry["game_title"]
                score = entry["score"]
                match = entry["match_percentage"]
                why_rank = entry["why_this_rank"]
                strengths = entry.get("key_strengths", [])

                print(f"\n  {rank}. 🎮 {title}")
                print(f"     📊 Score: {score:.1f} | Match: {match:.0f}%")
                print(f"     🤔 Why this rank: {why_rank}")
                if strengths:
                    print(f"     💪 Strengths: {'; '.join(strengths[:2])}")

            # Summary
            summary = result.get("comparison_summary", "")
            print(f"\n📝 Comparison Summary: {summary}")

        else:
            print(f"❌ Comparison failed: {result.get('error', 'Unknown error')}")

    except Exception as e:
        print(f"❌ Error in game comparison: {e}")


def test_multi_user_analysis() -> None:
    """Testuje analizę gry dla różnych typów użytkowników."""
    print("\n🔍 Testing Multi-User Analysis")
    print("=" * 80)

    test_game = "Hollow Knight"
    user_types = [
        "bargain_hunter",
        "quality_seeker",
        "indie_lover",
        "aaa_gamer",
        "casual_player",
    ]

    print(f"🎮 Analyzing '{test_game}' for different user types")
    print(
        f"👥 User Types: {', '.join([u.replace('_', ' ').title() for u in user_types])}"
    )
    print("-" * 60)

    try:
        result = get_recommendation_insights(test_game, user_types)

        if result.get("success", False):
            game_title = result.get("game_title", test_game)
            print(f"✅ Analysis completed for: {game_title}")

            # Best and worst fit users
            best_fit = result.get("best_fit_user", {})
            worst_fit = result.get("worst_fit_user", {})

            print(f"\n🏆 Best Fit User Type:")
            print(f"   👤 {best_fit.get('user_type', '').replace('_', ' ').title()}")
            print(f"   📊 Score: {best_fit.get('score', 0):.1f}/100")
            print(f"   🎯 Suitability: {best_fit.get('suitability', 'Unknown')}")

            print(f"\n🔻 Worst Fit User Type:")
            print(f"   👤 {worst_fit.get('user_type', '').replace('_', ' ').title()}")
            print(f"   📊 Score: {worst_fit.get('score', 0):.1f}/100")
            print(f"   🎯 Suitability: {worst_fit.get('suitability', 'Unknown')}")

            # Detailed analysis for each user type
            user_analyses = result.get("user_analyses", {})
            print(f"\n📊 Detailed User Analysis:")

            for user_type, analysis in user_analyses.items():
                user_name = user_type.replace("_", " ").title()
                score = analysis.get("recommendation_score", 0)
                suitability = analysis.get("suitability", "Unknown")
                recommendation = analysis.get("recommendation", "Unknown")
                key_reasons = analysis.get("key_reasons", [])
                concerns = analysis.get("concerns", [])

                print(f"\n  👤 {user_name}:")
                print(f"     📊 Score: {score:.1f}/100")
                print(f"     🎯 Suitability: {suitability}")
                print(f"     🏷️ Recommendation: {recommendation}")

                if key_reasons:
                    print(f"     ✅ Key Reasons: {'; '.join(key_reasons)}")

                if concerns:
                    print(f"     ⚠️ Concerns: {'; '.join(concerns)}")

            # Overall insights
            insights = result.get("overall_insights", [])
            if insights:
                print(f"\n💡 Overall Insights:")
                for insight in insights:
                    print(f"   • {insight}")

        else:
            print(
                f"❌ Multi-user analysis failed: {result.get('error', 'Unknown error')}"
            )

    except Exception as e:
        print(f"❌ Error in multi-user analysis: {e}")


def test_user_preferences_showcase() -> None:
    """Demonstruje różnice w profilach użytkowników."""
    print("\n👥 User Preferences Showcase")
    print("=" * 80)

    from utils.recommendation_engine import RecommendationEngine

    engine = RecommendationEngine()
    profiles = engine.get_predefined_profiles()

    print("📋 Available User Profiles:")

    for profile_id, profile in profiles.items():
        user_name = profile_id.replace("_", " ").title()
        primary_pref = profile.primary_preference.value.replace("_", " ").title()

        print(f"\n👤 {user_name}:")
        print(f"   🎯 Primary Preference: {primary_pref}")
        print(
            f"   💰 Budget Range: {profile.budget_range[0]:.0f} - {profile.budget_range[1]:.0f} PLN"
        )
        print(f"   ⭐ Minimum Score: {profile.minimum_score}")
        print(f"   🏷️ Preferred Genres: {', '.join(profile.preferred_genres[:4])}")
        print(f"   ⏱️ Playtime Preference: {profile.playtime_preference}")

        if profile.avoided_genres:
            print(f"   ❌ Avoided Genres: {', '.join(profile.avoided_genres)}")


def demonstrate_recommendation_flow() -> None:
    """Demonstruje pełny flow rekomendacji."""
    print("\n🚀 Complete Recommendation Flow Demo")
    print("=" * 80)

    # Scenario: User wants to find a good indie game under 30 PLN
    print("📋 Scenario: Indie lover looking for games under 30 PLN")
    print("-" * 60)

    games_to_analyze = [
        "Hollow Knight",  # Premium indie
        "INSIDE",  # Budget indie gem
        "Celeste",  # Mid-tier indie
        "Death's Door",  # Action indie
        "Moving Out",  # Casual indie
        "Slay the Spire",
        "Mario Kart 8 Deluxe",
        "Super Smash Bros. Ultimate",
        "The Legend of Zelda: Tears of the Kingdom",
        "Animal Crossing: New Horizons",
        "Baten Kaitos I & II HD Remaster",
        "Teenage Mutant Ninja Turtles: Shredder's Revenge",
        "Sonic Frontiers",
        "Street Fighter 6",
        "Ace Attorney Investigations",
        "Deltarune",
        "The Legend of Zelda: Breath of the Wild",
        "Mario & Luigi: Brothership",
        "Super Mario Odyssey",
        "MARIO + RABBIDS SPARKS OF HOPE",
        "Super Mario 3D Land",
        "WarioWare: Touched!",
        "Xenoblade Chronicles 3",
        "Atelier Ryza: Ever Darkness & the Secret Hideout",
    ]

    user_preference = "indie_lover"

    try:
        # Step 1: Get personalized recommendations
        print("🎯 Step 1: Getting personalized recommendations...")
        recommendations = generate_personalized_recommendations(
            games_to_analyze, user_preference, max_recommendations=3
        )

        if recommendations.get("success"):
            top_recs = recommendations.get("recommendations", [])
            print(f"✅ Found {len(top_recs)} top recommendations")

            # Show top pick
            if top_recs:
                top_pick = top_recs[0]
                print(f"\n🏆 Top Recommendation: {top_pick['game_title']}")
                print(f"   📊 Score: {top_pick['recommendation_score']:.1f}/100")
                print(f"   💌 {top_pick['personalized_message']}")

        # Step 2: Compare with other user types
        print(f"\n🔍 Step 2: Comparing with other user types...")
        if top_recs:
            top_game = top_recs[0]["game_title"]
            multi_analysis = get_recommendation_insights(top_game)

            if multi_analysis.get("success"):
                best_fit = multi_analysis.get("best_fit_user", {})
                print(
                    f"✅ Best fit user type: {best_fit.get('user_type', '').replace('_', ' ').title()}"
                )
                print(f"   📊 Score for that user: {best_fit.get('score', 0):.1f}/100")

        # Step 3: Final recommendation
        print(f"\n💡 Step 3: Final recommendation summary")
        if recommendations.get("success"):
            summary = recommendations.get("recommendation_summary", "")
            print(f"📝 {summary}")

        print(f"\n✅ Recommendation flow completed successfully!")

    except Exception as e:
        print(f"❌ Error in recommendation flow: {e}")


if __name__ == "__main__":
    print("🚀 Phase 2 Point 3 - Recommendation System Testing")
    print("=" * 100)

    # Test 1: Personalized recommendations
    test_personalized_recommendations()

    # Test 2: Game comparison
    test_game_comparison()

    # Test 3: Multi-user analysis
    test_multi_user_analysis()

    # Test 4: User preferences showcase
    test_user_preferences_showcase()

    # Test 5: Complete flow demo
    demonstrate_recommendation_flow()

    print(f"\n🎉 Phase 2 Point 3 testing completed!")
    print("✅ Recommendation system fully implemented and tested!")

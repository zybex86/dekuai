"""
Test Advanced Value Analysis - Phase 2 Point 2
Test zaawansowanej analizy wartości - Faza 2 Punkt 2

This example tests the advanced value analysis algorithms including:
- Genre-based analysis
- Market position scoring
- Age factor calculations
- Comprehensive scoring

Ten przykład testuje zaawansowane algorytmy analizy wartości.
"""

import os
import sys

# Add parent directory to Python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from agent_tools import search_and_scrape_game, calculate_advanced_value_analysis
import json


def test_advanced_analysis(game_name: str) -> None:
    """
    Testuje zaawansowaną analizę wartości dla podanej gry.

    Args:
        game_name (str): Nazwa gry do przetestowania
    """
    print(f"🎮 Testing advanced value analysis for: {game_name}")
    print("=" * 70)

    try:
        # Step 1: Get game data
        print("📡 Step 1: Collecting game data...")
        game_data = search_and_scrape_game(game_name)

        if not game_data.get("success", False):
            print(
                f"❌ Failed to get game data: {game_data.get('message', 'Unknown error')}"
            )
            return

        print(f"✅ Game data collected for: {game_data.get('title', 'Unknown')}")

        # Step 2: Advanced analysis
        print("🚀 Step 2: Performing advanced value analysis...")
        advanced_analysis = calculate_advanced_value_analysis(game_data)

        if not advanced_analysis.get("success", False):
            print(
                f"❌ Advanced analysis failed: {advanced_analysis.get('error', 'Unknown error')}"
            )
            return

        # Step 3: Display comprehensive results
        print("✅ Advanced analysis completed!")
        print("\n" + "🔍 COMPREHENSIVE RESULTS:")
        print("=" * 70)

        # Basic info
        basic_info = advanced_analysis.get("basic_info", {})
        title = advanced_analysis.get("game_title", "Unknown")
        analysis_type = advanced_analysis.get("analysis_type", "Unknown")
        confidence = advanced_analysis.get("confidence_level", "Unknown")

        print(f"🎮 Game: {title}")
        print(f"📊 Analysis Type: {analysis_type}")
        print(f"🎯 Confidence Level: {confidence}")
        print(f"💰 Price: {basic_info.get('current_price')}")
        print(f"🏷️ Genres: {', '.join(basic_info.get('genres', []))}")
        print(f"👨‍💻 Developer: {basic_info.get('developer')}")

        # Comprehensive analysis results
        comp_analysis = advanced_analysis.get("comprehensive_analysis", {})
        comp_score = comp_analysis.get("comprehensive_score", 0)
        recommendation = comp_analysis.get("advanced_recommendation", "Unknown")

        print(f"\n🏆 Comprehensive Score: {comp_score}")
        print(f"🎯 Advanced Recommendation: {recommendation}")

        # Market analysis
        market_analysis = comp_analysis.get("market_analysis", {})
        if market_analysis:
            print(f"\n📈 MARKET ANALYSIS:")
            print(
                f"  💸 Price Category: {market_analysis.get('price_category', 'Unknown')}"
            )
            print(
                f"  ⭐ Quality Category: {market_analysis.get('quality_category', 'Unknown')}"
            )
            print(
                f"  🎯 Market Position: {market_analysis.get('market_position', 'Unknown')}"
            )
            print(f"  🏆 Value Tier: {market_analysis.get('value_tier', 'Unknown')}")
            print(f"  📊 Position Score: {market_analysis.get('position_score', 0)}")

        # Genre analysis
        genre_analysis = comp_analysis.get("genre_analysis", {})
        if genre_analysis:
            print(f"\n🎮 GENRE ANALYSIS:")
            print(
                f"  🏷️ Primary Genre: {genre_analysis.get('primary_genre', 'Unknown')}"
            )
            print(f"  ⏱️ Expected Hours: {genre_analysis.get('expected_hours', 0)}")
            print(f"  💰 Cost per Hour: {genre_analysis.get('cost_per_hour', 0):.2f}")
            print(
                f"  📊 Genre Value Score: {genre_analysis.get('final_value_score', 0)}"
            )
            print(
                f"  🔥 Developer Multiplier: {genre_analysis.get('developer_multiplier', 1.0)}"
            )

        # Age factor
        age_factor = comp_analysis.get("age_factor", 1.0)
        print(f"\n📅 AGE FACTOR: {age_factor:.2f}")

        # Value breakdown
        value_breakdown = comp_analysis.get("value_breakdown", {})
        if value_breakdown:
            print(f"\n💎 VALUE BREAKDOWN:")
            print(
                f"  🎮 Genre Contribution: {value_breakdown.get('genre_contribution', 0)}"
            )
            print(
                f"  📈 Market Contribution: {value_breakdown.get('market_contribution', 0)}"
            )
            print(
                f"  📅 Age Contribution: {value_breakdown.get('age_contribution', 0)}"
            )

        # Advanced insights
        insights = advanced_analysis.get("insights", [])
        if insights:
            print(f"\n💡 ADVANCED INSIGHTS:")
            for i, insight in enumerate(insights, 1):
                print(f"  {i}. {insight}")

        # Summary
        summary = comp_analysis.get("analysis_summary", "No summary available")
        print(f"\n📝 SUMMARY: {summary}")

        print("\n" + "=" * 70)
        print("✅ Advanced value analysis test completed successfully!")

    except Exception as e:
        print(f"❌ Error during advanced analysis test: {e}")


def compare_basic_vs_advanced(game_name: str) -> None:
    """
    Porównuje podstawową i zaawansowaną analizę wartości.

    Args:
        game_name (str): Nazwa gry do porównania
    """
    print(f"🔄 Comparing basic vs advanced analysis for: {game_name}")
    print("=" * 70)

    try:
        from agent_tools import calculate_value_score

        # Get game data
        game_data = search_and_scrape_game(game_name)
        if not game_data.get("success", False):
            print(f"❌ Failed to get game data")
            return

        # Basic analysis
        print("📊 Basic Analysis:")
        basic_result = calculate_value_score(game_data)
        if basic_result.get("success"):
            basic_rec = basic_result.get("value_metrics", {}).get(
                "recommendation", "Unknown"
            )
            basic_score = basic_result.get("value_metrics", {}).get("value_score", 0)
            basic_timing = basic_result.get("value_metrics", {}).get(
                "buy_timing", "Unknown"
            )
            print(f"  🎯 Recommendation: {basic_rec}")
            print(f"  💎 Value Score: {basic_score}")
            print(f"  ⏰ Buy Timing: {basic_timing}")

        # Advanced analysis
        print("\n🚀 Advanced Analysis:")
        advanced_result = calculate_advanced_value_analysis(game_data)
        if advanced_result.get("success"):
            comp_analysis = advanced_result.get("comprehensive_analysis", {})
            adv_rec = comp_analysis.get("advanced_recommendation", "Unknown")
            adv_score = comp_analysis.get("comprehensive_score", 0)
            market_pos = comp_analysis.get("market_analysis", {}).get(
                "market_position", "Unknown"
            )
            value_tier = comp_analysis.get("market_analysis", {}).get(
                "value_tier", "Unknown"
            )

            print(f"  🎯 Advanced Recommendation: {adv_rec}")
            print(f"  🏆 Comprehensive Score: {adv_score}")
            print(f"  📈 Market Position: {market_pos}")
            print(f"  🏆 Value Tier: {value_tier}")

        print("\n✅ Comparison completed!")

    except Exception as e:
        print(f"❌ Error during comparison: {e}")


def test_genre_specific_games() -> None:
    """Testuje analizę dla gier różnych gatunków."""
    genre_games = {
        "Action": "Death's Door",
        "Platformer": "Celeste",
        "Role-Playing": "Baten Kaitos I & II HD Remaster",
        "Puzzle": "INSIDE",
        "Adventure": "Ace Attorney Investigations",
        "Fighting": "Teenage Mutant Ninja Turtles: Shredder's Revenge",
        "Shooter": "Sonic Frontiers",
        "Strategy": "Slay the Spire",
        "Racing": "Mario Kart 8 Deluxe",
        "Sports": "Super Smash Bros. Ultimate",
        "RPG": "The Legend of Zelda: Tears of the Kingdom",
        "Simulation": "Animal Crossing: New Horizons",
    }

    print("🎮 Genre-Specific Advanced Value Analysis")
    print("=" * 80)

    for genre, game in genre_games.items():
        print(f"\n🏷️ Testing {genre} game: {game}")
        print("-" * 50)

        try:
            game_data = search_and_scrape_game(game)
            if game_data.get("success", False):
                advanced_result = calculate_advanced_value_analysis(game_data)
                if advanced_result.get("success", False):
                    comp_analysis = advanced_result.get("comprehensive_analysis", {})
                    genre_analysis = comp_analysis.get("genre_analysis", {})
                    market_analysis = comp_analysis.get("market_analysis", {})

                    detected_genre = genre_analysis.get("primary_genre", "Unknown")
                    expected_hours = genre_analysis.get("expected_hours", 0)
                    cost_per_hour = genre_analysis.get("cost_per_hour", 0)
                    market_position = market_analysis.get("market_position", "Unknown")

                    print(f"  🎯 Detected Genre: {detected_genre}")
                    print(f"  ⏱️ Expected Hours: {expected_hours}")
                    print(f"  💰 Cost/Hour: {cost_per_hour:.2f}")
                    print(f"  📈 Market Position: {market_position}")
                else:
                    print(f"  ❌ Analysis failed for {game}")
            else:
                print(f"  ❌ Data collection failed for {game}")

        except Exception as e:
            print(f"  ❌ Error analyzing {game}: {e}")


if __name__ == "__main__":
    print("🚀 Phase 2 Point 2 - Advanced Value Analysis Testing")
    print("=" * 80)

    # Test individual game
    test_game = "Hollow Knight"
    test_advanced_analysis(test_game)

    print("\n" + "=" * 80)

    # Compare basic vs advanced
    compare_basic_vs_advanced(test_game)

    print("\n" + "=" * 80)

    # Test genre-specific analysis
    test_genre_specific_games()

    print(f"\n🎉 Phase 2 Point 2 testing completed!")
    print("✅ Advanced value analysis algorithms implemented and tested!")
